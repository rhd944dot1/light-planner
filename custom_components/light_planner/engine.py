"""Connects the flow logic to Home Assistant: timers, presence, targets, lights."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping
from dataclasses import asdict, replace
from datetime import UTC, date, datetime, time, timedelta
import logging
from typing import Any

from astral import SunDirection
from astral.sun import elevation as sun_elevation, noon, time_at_elevation
from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP,
    EVENT_STATE_CHANGED,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import (
    CALLBACK_TYPE,
    Context,
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.sun import get_astral_event_date, get_astral_observer
from homeassistant.helpers.target import TargetSelection, async_extract_referenced_entity_ids
from homeassistant.util import dt as dt_util

from .schedule import (
    OFF,
    UNCHANGED,
    Action,
    Bar,
    Decision,
    Env,
    Event as PlanEvent,
    Flow,
    Look,
    Row,
    active_bar,
    day_segments,
    decide,
    events_between,
    left_alone,
    manual_counts,
    missed_events,
    next_moment,
    run_start,
)
from .store import PlannerStore

_LOGGER = logging.getLogger(__name__)
_GONE = (STATE_UNKNOWN, STATE_UNAVAILABLE)
# Lamps report late and round values: what changes less than this, or right after our own
# command without a user behind it, isn't somebody changing the light.
_ECHO_TIME = timedelta(seconds=15)
_OWN_CONTEXT_TIME = timedelta(minutes=1)
_BRIGHTNESS_TOLERANCE = 8
_KELVIN_TOLERANCE = 150
_RGB_TOLERANCE = 25
_MANUAL_KEPT = timedelta(hours=24)


class HaSun:
    """Sun moments at the configured home location."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._cache: dict[tuple[Any, ...], datetime | None] = {}

    def event(self, kind: str, day: date) -> datetime | None:
        key = (kind, day)
        if key not in self._cache:
            self._cache[key] = get_astral_event_date(self._hass, kind, day)
        return self._cache[key]

    def below(self, elevation: float, day: date) -> datetime | None:
        key = (elevation, day)
        if key not in self._cache:
            self._cache[key] = self._below(elevation, day)
        return self._cache[key]

    def _below(self, elevation: float, day: date) -> datetime | None:
        observer = get_astral_observer(self._hass)
        try:
            return time_at_elevation(observer, elevation, day, SunDirection.SETTING, tzinfo=UTC)
        except ValueError:
            # Never crossed: at noon the sun is either below all day or above all day.
            highest = noon(observer, day, tzinfo=UTC)
            below = sun_elevation(observer, highest) < elevation
            return highest if below else None


def _snapshot(hass: HomeAssistant, entity_id: str) -> dict[str, Any] | None:
    state = hass.states.get(entity_id)
    if state is None or state.state in _GONE:
        return None
    data: dict[str, Any] = {}
    if state.state == STATE_ON and state.domain == "light":
        attributes = state.attributes
        if attributes.get("brightness") is not None:
            data["brightness"] = attributes["brightness"]
        if attributes.get("color_mode") == "color_temp":
            data["color_temp_kelvin"] = attributes.get("color_temp_kelvin")
        elif attributes.get("rgb_color") is not None:
            data["rgb_color"] = list(attributes["rgb_color"])
    return {"state": state.state, "data": data, "at": dt_util.utcnow().isoformat()}


@callback
def _is_person(event_data: Mapping[str, Any]) -> bool:
    return event_data["entity_id"].startswith("person.")


@callback
def _is_light(event_data: Mapping[str, Any]) -> bool:
    return event_data["entity_id"].startswith("light.")


def _differs(old: Any, new: Any, tolerance: int) -> bool:
    return old is not None and new is not None and abs(old - new) >= tolerance


def _really_changed(old: State, new: State) -> bool:
    """Switched, or visibly different; a value appearing or vanishing alone doesn't count."""
    if old.state != new.state:
        return True
    if new.state != STATE_ON:
        return False
    before, after = old.attributes, new.attributes
    if _differs(before.get("brightness"), after.get("brightness"), _BRIGHTNESS_TOLERANCE):
        return True
    if before.get("color_mode") == after.get("color_mode") == "color_temp":
        return _differs(
            before.get("color_temp_kelvin"), after.get("color_temp_kelvin"), _KELVIN_TOLERANCE
        )
    old_rgb, new_rgb = before.get("rgb_color"), after.get("rgb_color")
    if old_rgb is None or new_rgb is None:
        return False
    return any(_differs(a, b, _RGB_TOLERANCE) for a, b in zip(old_rgb, new_rgb, strict=True))


class Engine:
    """Runs all flows. Everything that switches lights holds the lock."""

    def __init__(self, hass: HomeAssistant, store: PlannerStore) -> None:
        self.hass = hass
        self.store = store
        self.env = Env(dt_util.get_default_time_zone(), HaSun(hass))
        self.flows: list[Flow] = []
        self._lock = asyncio.Lock()
        self._cancel_timer: CALLBACK_TYPE | None = None
        self._cancel: list[CALLBACK_TYPE] = []
        self._last = dt_util.utcnow()
        self._home: dict[str, bool] = {}
        self._running = False
        self._own_contexts: dict[str, datetime] = {}
        self._commanded: dict[str, datetime] = {}
        self._rebuild()

    @callback
    def async_start(self) -> None:
        """Wait for startup, or restored persons would look like people arriving."""
        self._cancel.append(async_at_started(self.hass, self._arm))
        self._cancel.append(self.hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, self._on_stop))

    @callback
    def async_stop(self) -> None:
        self._running = False
        if self._cancel_timer:
            self._cancel_timer()
            self._cancel_timer = None
        while self._cancel:
            self._cancel.pop()()

    @callback
    def _on_stop(self, _event: Event) -> None:
        self.async_stop()

    @callback
    def _arm(self, _hass: HomeAssistant) -> None:
        self._running = True
        self._home = self._current_home()
        self._cancel.append(
            self.hass.bus.async_listen(
                EVENT_STATE_CHANGED, self._person_changed, event_filter=_is_person
            )
        )
        self._cancel.append(
            self.hass.bus.async_listen(
                EVENT_STATE_CHANGED, self._light_changed, event_filter=_is_light
            )
        )
        since = dt_util.parse_datetime(self.store.handled) if self.store.handled else None
        self._handled_until(dt_util.utcnow())
        self._plan()
        if since is not None:
            self.hass.async_create_task(self._catch_up(since))

    def _handled_until(self, moment: datetime) -> None:
        self._last = moment
        self.store.handled = moment.isoformat()
        self.store.save()

    async def _catch_up(self, since: datetime) -> None:
        """Starts and ends that fell into the time Home Assistant wasn't running."""
        async with self._lock:
            if not self._running:
                return
            now = dt_util.utcnow()
            await self._handle(missed_events(self.flows, since, now, self.env), now)

    def _rebuild(self) -> None:
        self.flows = [Flow.from_dict(raw) for raw in self.store.flows]

    # Configuration

    async def async_save(self, raw: dict[str, Any]) -> None:
        async with self._lock:
            for index, existing in enumerate(self.store.flows):
                if existing["id"] == raw["id"]:
                    self.store.flows[index] = raw
                    break
            else:
                self.store.flows.append(raw)
            bars = {bar["id"] for row in raw["rows"] for bar in row["bars"]}
            saved = self.store.snapshots.get(raw["id"], {})
            for bar_id in set(saved) - bars:
                del saved[bar_id]
            self._changed()

    async def async_delete(self, flow_id: str) -> None:
        async with self._lock:
            self.store.flows = [f for f in self.store.flows if f["id"] != flow_id]
            self.store.snapshots.pop(flow_id, None)
            self._changed()

    def _changed(self) -> None:
        self.store.save()
        self._rebuild()
        if self._running:
            self._handled_until(dt_util.utcnow())
            self._plan()

    # Targets

    def lights_of(self, row: Row) -> list[str]:
        """Resolved by Home Assistant, fresh every time: a newly labeled light joins by itself."""
        target = {key: value for key, value in row.target.items() if key != "exclude"}
        excluded = self._resolve(row.target.get("exclude", {}))
        return sorted(
            entity
            for entity in self._resolve(target) - excluded
            if entity.startswith("light.")
        )

    def _resolve(self, target: Mapping[str, Any]) -> set[str]:
        selected = async_extract_referenced_entity_ids(self.hass, TargetSelection(target))
        return selected.referenced | selected.indirectly_referenced

    def _scene_entities(self, row: Row) -> list[str]:
        result: dict[str, None] = {}
        for scene in row.scenes:
            if (state := self.hass.states.get(scene)) is not None:
                result.update(dict.fromkeys(state.attributes.get("entity_id", [])))
        return list(result)

    # Manual changes

    @callback
    def _light_changed(self, event: Event[EventStateChangedData]) -> None:
        old, new = event.data["old_state"], event.data["new_state"]
        if old is None or new is None or old.state in _GONE or new.state in _GONE:
            return
        if not _really_changed(old, new) or not self._is_watched(new.entity_id):
            return
        context = new.context
        now = dt_util.utcnow()
        if context.id in self._own_contexts or context.parent_id in self._own_contexts:
            return
        commanded = self._commanded.get(new.entity_id)
        if context.user_id is None and commanded is not None and now - commanded < _ECHO_TIME:
            return
        self.store.manual[new.entity_id] = now.isoformat()
        self._drop_old_marks(now)
        self.store.save()

    def _is_watched(self, entity_id: str) -> bool:
        """Only flows with the setting need this; other lights may change as often as they like."""
        return any(
            entity_id in (*self.lights_of(row), *self._scene_entities(row))
            for flow in self.flows
            if flow.enabled and flow.respect_manual
            for row in flow.rows
        )

    def _drop_old_marks(self, now: datetime) -> None:
        for entity_id, changed in list(self.store.manual.items()):
            if now - dt_util.parse_datetime(changed, raise_on_error=True) > _MANUAL_KEPT:
                del self.store.manual[entity_id]

    def _is_manual(self, flow: Flow, entity_id: str, moment: datetime) -> bool:
        changed = self.store.manual.get(entity_id)
        if changed is None:
            return False
        moment_changed = dt_util.parse_datetime(changed, raise_on_error=True)
        return manual_counts(flow, moment_changed, moment, self.env)

    def _scene_is_manual(self, flow: Flow, row: Row, moment: datetime) -> bool:
        """A scene can't skip single lights, so one changed light holds it back."""
        return any(self._is_manual(flow, e, moment) for e in self._scene_entities(row))

    def _forget_marks(self, flow: Flow, now: datetime) -> None:
        """A flow's run is over: its lights count as untouched again, unless another run needs them."""
        if not flow.respect_manual or run_start(flow, now, self.env) is not None:
            return
        for row in flow.rows:
            for entity_id in (*self.lights_of(row), *self._scene_entities(row)):
                if entity_id in self.store.manual and not self._kept_by_other_flow(flow, entity_id, now):
                    del self.store.manual[entity_id]

    def _kept_by_other_flow(self, ended: Flow, entity_id: str, now: datetime) -> bool:
        for flow in self.flows:
            if flow.id == ended.id or not flow.enabled or not flow.respect_manual:
                continue
            for row in flow.rows:
                if entity_id in (*self.lights_of(row), *self._scene_entities(row)):
                    if active_bar(flow, row, now, self.env) is not None:
                        return True
        return False

    async def async_clear_manual(self, entity_id: str) -> None:
        async with self._lock:
            self.store.manual.pop(entity_id, None)
            self.store.save()

    # Presence

    def _current_home(self) -> dict[str, bool]:
        return {
            state.entity_id: state.state == "home" for state in self.hass.states.async_all("person")
        }

    def _condition_met(self, flow: Flow) -> bool:
        home = self._current_home()
        match flow.condition:
            case "anyone_home":
                return any(home.values())
            case "everyone_home":
                return bool(home) and all(home.values())
            case "nobody_home":
                return not any(home.values())
            case "person":
                return home.get(flow.person, False)
        return True

    @staticmethod
    def _became_true(flow: Flow, before: dict[str, bool], after: dict[str, bool]) -> bool:
        match flow.condition:
            case "everyone_home":
                return bool(after) and all(after.values()) and not (before and all(before.values()))
            case "nobody_home":
                return any(before.values()) and not any(after.values())
            case "person":
                return not before.get(flow.person) and after.get(flow.person, False)
        return not any(before.values()) and any(after.values())

    @staticmethod
    def _applies_on_change(flow: Flow) -> bool:
        return flow.on_arrival == "apply" or flow.condition == "nobody_home"

    async def _person_changed(self, event: Event[EventStateChangedData]) -> None:
        old, new = event.data["old_state"], event.data["new_state"]
        if old is None or new is None or old.state in _GONE or new.state in _GONE:
            self._home = self._current_home()
            return
        before, self._home = self._home, self._current_home()
        if before == self._home:
            return
        async with self._lock:
            now = dt_util.utcnow()
            triggered = {
                flow.id
                for flow in self.flows
                if self._applies_on_change(flow) and self._became_true(flow, before, self._home)
            }
            decisions = decide(
                self.flows,
                now,
                self.env,
                self.lights_of,
                lambda f: self._condition_met(f) and self._applies_on_change(f),
            )
            for light, decision in decisions.items():
                if decision.flow.id in triggered and not self._is_manual(decision.flow, light, now):
                    self._remember(decision.flow, decision.bar, [light])
                    await self._set(light, decision.action)
            for flow in self.flows:
                if flow.id in triggered and flow.enabled:
                    await self._start_scenes(flow, now)
            self.store.save()

    async def _start_scenes(self, flow: Flow, now: datetime, respect_manual: bool = True) -> None:
        for row in flow.rows:
            if not row.scenes:
                continue
            if (running := active_bar(flow, row, now, self.env)) is None:
                continue
            if respect_manual and self._scene_is_manual(flow, row, now):
                continue
            self._remember(flow, running[0], self._scene_entities(row))
            await self._activate_scene(row)

    # Timer

    def _plan(self) -> None:
        if self._cancel_timer:
            self._cancel_timer()
        tomorrow = dt_util.start_of_local_day() + timedelta(days=1)
        moment = next_moment(self.flows, self._last, self.env)
        point = min(moment, tomorrow) if moment else tomorrow
        self._cancel_timer = async_track_point_in_utc_time(self.hass, self._tick, point)

    async def _tick(self, _now: datetime) -> None:
        self._cancel_timer = None
        async with self._lock:
            now = dt_util.utcnow()
            await self._handle(events_between(self.flows, self._last, now, self.env), now)
            self._handled_until(now)
            self._plan()

    async def _handle(self, events: list[PlanEvent], now: datetime) -> None:
        for event in events:
            if event.kind == "start":
                await self._on_start(event.flow, event.row, event.bar, now)
            else:
                await self._on_end(event, now)

    async def _on_start(self, flow: Flow, row: Row, bar: Bar, now: datetime) -> None:
        if not self._condition_met(flow):
            return
        if row.scenes and not self._scene_is_manual(flow, row, now):
            self._remember(flow, bar, self._scene_entities(row))
            await self._activate_scene(row)
        decisions = decide(self.flows, now, self.env, self.lights_of, self._condition_met)
        lights = [
            light
            for light, decision in decisions.items()
            if decision.flow.id == flow.id
            and decision.bar.id == bar.id
            and not self._is_manual(flow, light, now)
        ]
        self._remember(flow, bar, lights)
        for light in lights:
            action = decisions[light].action
            await self._set(light, action, only_if_on=bar.at_start == "adjust")

    async def _on_end(self, event: PlanEvent, now: datetime) -> None:
        flow, row, bar = event.flow, event.row, event.bar
        # Looked at just before the end: an own row ending at this moment still counts.
        before = event.moment - timedelta(microseconds=1)
        decisions = decide(self.flows, now, self.env, self.lights_of, self._condition_met)
        saved = self.store.snapshots.get(flow.id, {})
        snapshots = saved.pop(bar.id, {})
        for light in (*self.lights_of(row), *self._scene_entities(row)):
            if bar.action != UNCHANGED and left_alone(flow, light, before, self.env):
                continue
            decision = decisions.get(light)
            if decision is not None:
                self._hand_over_snapshot(decision, light, snapshots.get(light))
                if self._is_manual(decision.flow, light, now):
                    continue
                adjust = decision.bar.at_start == "adjust"
                await self._set(light, decision.action, only_if_on=adjust)
            elif bar.action == UNCHANGED:
                continue
            elif bar.at_end == "turn_off":
                await self._set(light, OFF)
            elif bar.at_end == "restore" and light in snapshots:
                await self._restore(light, snapshots[light])
        self._forget_marks(flow, now)

    # Restoring

    def _remember(self, flow: Flow, bar: Bar, entities: Iterable[str]) -> None:
        if bar.at_end != "restore":
            return
        saved = self.store.snapshots.setdefault(flow.id, {}).setdefault(bar.id, {})
        for entity_id in entities:
            if entity_id not in saved and (snapshot := _snapshot(self.hass, entity_id)):
                saved[entity_id] = snapshot

    def _hand_over_snapshot(
        self, decision: Decision, light: str, snapshot: dict[str, Any] | None
    ) -> None:
        """Whoever restores next must restore the oldest state, not a bar's look."""
        if snapshot is None or decision.bar.at_end != "restore":
            return
        saved = self.store.snapshots.setdefault(decision.flow.id, {})
        saved = saved.setdefault(decision.bar.id, {})
        if light not in saved or snapshot["at"] < saved[light]["at"]:
            saved[light] = snapshot

    async def _restore(self, entity_id: str, snapshot: dict[str, Any]) -> None:
        domain = entity_id.split(".")[0]
        if snapshot["state"] == STATE_ON:
            await self._call(domain, "turn_on", {"entity_id": entity_id, **snapshot["data"]})
        else:
            await self._call(domain, "turn_off", {"entity_id": entity_id})

    # Switching

    async def _set(self, entity_id: str, action: Action, only_if_on: bool = False) -> None:
        domain = entity_id.split(".")[0]
        if action == OFF:
            await self._call(domain, "turn_off", {"entity_id": entity_id})
            return
        if only_if_on and not self.hass.states.is_state(entity_id, STATE_ON):
            return
        await self._call(domain, "turn_on", {"entity_id": entity_id, **action.service_data()})

    async def _activate_scene(self, row: Row) -> None:
        self._note_command(self._scene_entities(row))
        for scene in row.scenes:
            await self._call("scene", "turn_on", {"entity_id": scene})

    def _note_command(self, entities: Iterable[str]) -> None:
        now = dt_util.utcnow()
        for entity_id in entities:
            self._commanded[entity_id] = now

    def _own_context(self) -> Context:
        """Marks what we switch, so it can be told apart from everybody else's changes."""
        now = dt_util.utcnow()
        for known, created in list(self._own_contexts.items()):
            if now - created > _OWN_CONTEXT_TIME:
                del self._own_contexts[known]
        context = Context()
        self._own_contexts[context.id] = now
        return context

    async def _call(self, domain: str, service: str, data: dict[str, Any]) -> None:
        """One broken light must not stop the others."""
        self._note_command([data["entity_id"]])
        try:
            await self.hass.services.async_call(
                domain, service, data, blocking=True, context=self._own_context()
            )
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.warning("%s.%s failed for %s: %s", domain, service, data["entity_id"], err)

    # Panel

    async def async_apply_now(self, flow: Flow) -> None:
        """Apply what the flow schedules for this moment, whatever its condition or manual changes say."""
        flow = replace(flow, enabled=True)
        async with self._lock:
            now = dt_util.utcnow()
            for light, decision in decide([flow], now, self.env, self.lights_of).items():
                self.store.manual.pop(light, None)
                await self._set(light, decision.action)
            await self._start_scenes(flow, now, respect_manual=False)
            for row in flow.rows:
                if active_bar(flow, row, now, self.env) is not None:
                    for entity_id in self._scene_entities(row):
                        self.store.manual.pop(entity_id, None)
            self.store.save()

    def preview(self, flows: list[Flow], weekday: int, clock: time) -> dict[str, Any]:
        """Arriving home on the next such weekday, with everyone counted as home."""
        today = dt_util.now().date()
        day = today + timedelta(days=(weekday - today.weekday()) % 7)
        now = self.env.at(day, clock)

        def counts(flow: Flow) -> bool:
            return flow.on_arrival == "apply" and flow.condition != "nobody_home"

        decisions = decide(flows, now, self.env, self.lights_of, counts)

        lights: dict[str, None] = {}
        details: dict[str, Any] = {}
        for flow in flows:
            rows: dict[str, Any] = {}
            bars: dict[str, Any] = {}
            for row in flow.rows:
                members = self.lights_of(row)
                lights.update(dict.fromkeys(members))
                rows[row.id] = [self._named(light) for light in members]
                for bar in row.bars:
                    bars[bar.id] = day_segments(flow, bar, day, self.env)
            details[flow.id] = {"rows": rows, "bars": bars, "manual": self._manual_lights(flow)}

        scenes = [
            self._named(scene)
            for flow in flows
            if flow.enabled and counts(flow)
            for row in flow.rows
            if active_bar(flow, row, now, self.env) is not None
            for scene in row.scenes
        ]
        return {
            "date": day.isoformat(),
            "sun": self._sun_day(day),
            "flows": details,
            "scenes": scenes,
            "lights": [
                {**self._named(light), **self._describe(decisions.get(light))} for light in lights
            ],
        }

    def _manual_lights(self, flow: Flow) -> list[dict[str, str]]:
        """What this flow leaves alone right now, whatever day the preview shows."""
        now = dt_util.utcnow()
        entities = dict.fromkeys(
            entity_id
            for row in flow.rows
            for entity_id in (*self.lights_of(row), *self._scene_entities(row))
        )
        return [
            {**self._named(entity_id), "at": self.store.manual[entity_id]}
            for entity_id in entities
            if self._is_manual(flow, entity_id, now)
        ]

    def _sun_day(self, day: date) -> dict[str, Any]:
        """Sun moments in local hours; the panel places sun-bound bars with them while dragging."""

        def hours(moment: datetime | None) -> float | None:
            if moment is None:
                return None
            local = dt_util.as_local(moment)
            return round(local.hour + local.minute / 60 + local.second / 3600, 3)

        sun = self.env.sun
        below = ((degrees, hours(sun.below(degrees, day))) for degrees in range(-12, 62, 2))
        return {
            "sunset": hours(sun.event("sunset", day)),
            "sunrise": hours(sun.event("sunrise", day)),
            "below": [[degrees, at] for degrees, at in below if at is not None],
        }

    def _named(self, entity_id: str) -> dict[str, str]:
        state = self.hass.states.get(entity_id)
        return {"id": entity_id, "name": state.name if state else entity_id}

    @staticmethod
    def _describe(decision: Decision | None) -> dict[str, Any]:
        if decision is None:
            return {"flow": None, "row": None, "action": None}
        action = decision.action
        result = {"kind": "off"} if action == OFF else {"kind": "look", **_look(action)}
        return {"flow": decision.flow.name, "row": decision.row.id, "action": result}


def _look(look: Look) -> dict[str, Any]:
    data = asdict(look)
    data["rgb"] = list(look.rgb)
    return data
