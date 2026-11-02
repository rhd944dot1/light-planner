"""Pure flow logic: which time window applies to which light at which moment."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, tzinfo
from typing import Any, Protocol

import voluptuous as vol

DAYS = range(7)
START_TYPES = ("time", "sunset", "sunrise", "sun_elevation")
END_TYPES = ("time", "sunset", "sunrise")
TARGET_KEYS = ("entity_id", "device_id", "area_id", "floor_id", "label_id")
CONDITIONS = ("always", "anyone_home", "everyone_home", "nobody_home", "person")
NOON = time(12)


def _time(value: Any) -> str:
    """Normalize to HH:MM, the only format stored."""
    if not isinstance(value, str):
        raise vol.Invalid("Time must be a string")
    try:
        return time.fromisoformat(value).strftime("%H:%M")
    except ValueError as err:
        raise vol.Invalid(f"Invalid time: {value}") from err


_LOOK = vol.Schema(
    {
        vol.Required("mode"): vol.In(("keep", "white", "color", "off", "unchanged")),
        vol.Optional("kelvin", default=2700): vol.All(int, vol.Range(1000, 10000)),
        vol.Optional("rgb", default=[255, 255, 255]): vol.All(
            [vol.All(int, vol.Range(0, 255))], vol.Length(3, 3)
        ),
        vol.Optional("brightness", default=None): vol.Any(
            None, vol.All(int, vol.Range(1, 100))
        ),
    }
)

_OFFSET = vol.All(int, vol.Range(-720, 720))


def _id_list(value: Any) -> list[str]:
    """Home Assistant's target picker may give a single id or a list."""
    return [value] if isinstance(value, str) else value


_IDS = vol.All(_id_list, [vol.All(str, vol.Length(min=1))])
_TARGET_IDS: dict[Any, Any] = {vol.Optional(key): _IDS for key in TARGET_KEYS}

_BAR = vol.Schema(
    {
        vol.Required("id"): vol.All(str, vol.Length(min=1)),
        vol.Required("start"): {
            vol.Required("type"): vol.In(START_TYPES),
            vol.Optional("time", default=None): vol.Any(None, _time),
            vol.Optional("elevation", default=None): vol.Any(None, vol.Coerce(float)),
            vol.Optional("offset", default=0): _OFFSET,
        },
        vol.Required("end"): {
            vol.Required("type"): vol.In(END_TYPES),
            vol.Optional("time", default=None): vol.Any(None, _time),
            vol.Optional("offset", default=0): _OFFSET,
        },
        vol.Optional("at_start", default="turn_on"): vol.In(("turn_on", "adjust")),
        vol.Optional("at_end", default="turn_off"): vol.In(("turn_off", "restore", "nothing")),
        vol.Required("look"): _LOOK,
    }
)

FLOW_SCHEMA = vol.Schema(
    {
        vol.Required("id"): vol.All(str, vol.Length(min=1)),
        vol.Required("name"): str,
        vol.Optional("enabled", default=True): bool,
        vol.Required("days"): [vol.In(DAYS)],
        vol.Optional("condition", default="always"): vol.In(CONDITIONS),
        vol.Optional("person", default=None): vol.Any(None, str),
        vol.Optional("on_arrival", default="apply"): vol.In(("apply", "nothing")),
        vol.Optional("respect_manual", default=False): bool,
        vol.Optional("manual_hours", default=4): vol.All(int, vol.Range(1, 24)),
        vol.Required("rows"): [
            {
                vol.Required("id"): vol.All(str, vol.Length(min=1)),
                vol.Required("target"): {**_TARGET_IDS, vol.Optional("exclude"): _TARGET_IDS},
                vol.Optional("bars", default=list): [_BAR],
            }
        ],
    }
)


def upgrade_flow(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Rows stored by 0.3 name one target as type and id; now they hold a Home Assistant target."""
    keys = {"light": "entity_id", "scene": "entity_id", "area": "area_id", "label": "label_id"}
    rows = []
    for row in raw.get("rows", []):
        target = row.get("target", {})
        if "type" in target and "id" in target:
            target = {keys.get(target["type"], "entity_id"): [target["id"]]}
        rows.append({**row, "target": target})
    return {**raw, "rows": rows}


def _target_items(row: Mapping[str, Any]) -> list[tuple[str, str]]:
    return [(key, item) for key in TARGET_KEYS for item in row["target"].get(key, [])]


def _bar_incomplete(bar: Mapping[str, Any]) -> str | None:
    start, end = bar["start"], bar["end"]
    if start["type"] == "time" and not start["time"]:
        return "Pick a start time."
    if start["type"] == "sun_elevation" and start["elevation"] is None:
        return "Enter a sun elevation."
    if end["type"] == "time" and not end["time"]:
        return "Pick an end time."
    if start["type"] == "time" and end["type"] == "time" and start["time"] == end["time"]:
        return "Start and end can't be the same time."
    return None


def _fixed_span(bar: Mapping[str, Any]) -> tuple[int, int] | None:
    """Minutes of a bar with fixed times; sun bars move daily, the later start wins at runtime."""
    start, end = bar["start"], bar["end"]
    if start["type"] != "time" or end["type"] != "time":
        return None
    begin = time.fromisoformat(start["time"])
    finish = time.fromisoformat(end["time"])
    begin_minutes = begin.hour * 60 + begin.minute
    finish_minutes = finish.hour * 60 + finish.minute
    if finish_minutes <= begin_minutes:
        finish_minutes += 1440
    return begin_minutes, finish_minutes


def _overlap(first: tuple[int, int], second: tuple[int, int]) -> bool:
    return any(
        first[0] < second[1] + shift and second[0] + shift < first[1] for shift in (-1440, 0, 1440)
    )


def flow_incomplete_reason(data: Mapping[str, Any]) -> str | None:
    """Why a normalized flow cannot be saved."""
    if not data["name"].strip():
        return "Give this flow a name."
    if not data["days"]:
        return "Pick at least one day."
    if data["condition"] == "person" and not data["person"]:
        return "Pick a person."
    items = [item for row in data["rows"] for item in _target_items(row)]
    if len(items) != len(set(items)):
        return "Each target can only be in one row."
    if not all(_target_items(row) for row in data["rows"]):
        return "Pick a target for every row."
    if not any(row["bars"] for row in data["rows"]):
        return "Add at least one time window."
    for row in data["rows"]:
        for bar in row["bars"]:
            if reason := _bar_incomplete(bar):
                return reason
        spans = [span for bar in row["bars"] if (span := _fixed_span(bar))]
        for index, span in enumerate(spans):
            if any(_overlap(span, other) for other in spans[index + 1 :]):
                return "Time windows in one row can't overlap."
    return None


@dataclass(frozen=True)
class Look:
    """How a light should appear."""

    mode: str = "keep"
    kelvin: int = 2700
    rgb: tuple[int, int, int] = (255, 255, 255)
    brightness: int | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Look:
        return cls(data["mode"], data["kelvin"], tuple(data["rgb"]), data["brightness"])

    def service_data(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.mode == "white":
            result["color_temp_kelvin"] = self.kelvin
        elif self.mode == "color":
            result["rgb_color"] = list(self.rgb)
        if self.brightness is not None:
            result["brightness_pct"] = self.brightness
        return result


OFF = "off"
UNCHANGED = "unchanged"
type Action = Look | str


def _action(data: Mapping[str, Any]) -> Action:
    if data["mode"] == OFF:
        return OFF
    if data["mode"] == UNCHANGED:
        return UNCHANGED
    return Look.from_dict(data)


@dataclass(frozen=True)
class Bar:
    """One time window on a row of a flow."""

    id: str
    start_type: str
    start_time: time | None
    elevation: float | None
    start_offset: int
    end_type: str
    end_time: time | None
    end_offset: int
    at_start: str
    at_end: str
    action: Action

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Bar:
        start, end = data["start"], data["end"]
        return cls(
            id=data["id"],
            start_type=start["type"],
            start_time=time.fromisoformat(start["time"]) if start["time"] else None,
            elevation=start["elevation"],
            start_offset=start["offset"],
            end_type=end["type"],
            end_time=time.fromisoformat(end["time"]) if end["time"] else None,
            end_offset=end["offset"],
            at_start=data["at_start"],
            at_end=data["at_end"],
            action=_action(data["look"]),
        )


@dataclass(frozen=True)
class Row:
    """One Home Assistant target of a flow with its time windows."""

    id: str
    target: Mapping[str, Any]
    direct: frozenset[str]
    bars: tuple[Bar, ...]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Row:
        target = data["target"]
        excluded = target.get("exclude", {}).get("entity_id", [])
        return cls(
            id=data["id"],
            target=target,
            direct=frozenset(target.get("entity_id", [])) - frozenset(excluded),
            bars=tuple(Bar.from_dict(bar) for bar in data["bars"]),
        )

    @property
    def scenes(self) -> list[str]:
        """Scenes count only when picked themselves, not via an area or label."""
        return sorted(entity for entity in self.direct if entity.startswith("scene."))


@dataclass(frozen=True)
class Flow:
    """A named flow, immutable once parsed."""

    id: str
    name: str
    enabled: bool
    days: frozenset[int]
    condition: str
    person: str | None
    on_arrival: str
    respect_manual: bool
    manual_hours: int
    rows: tuple[Row, ...]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Flow:
        return cls(
            id=data["id"],
            name=data["name"],
            enabled=data["enabled"],
            days=frozenset(data["days"]),
            condition=data["condition"],
            person=data["person"],
            on_arrival=data["on_arrival"],
            respect_manual=data["respect_manual"],
            manual_hours=data["manual_hours"],
            rows=tuple(Row.from_dict(row) for row in data["rows"]),
        )


class Sun(Protocol):
    """Sun moments for a day; None when the event doesn't happen that day."""

    def event(self, kind: str, day: date) -> datetime | None: ...

    def below(self, elevation: float, day: date) -> datetime | None: ...


@dataclass(frozen=True)
class Env:
    """Time zone and sun of the location."""

    tz: tzinfo
    sun: Sun

    def at(self, day: date, clock: time) -> datetime:
        return datetime.combine(day, clock, self.tz)


@dataclass(frozen=True)
class Window:
    start: datetime
    end: datetime


def _shifted(moment: datetime | None, offset: int) -> datetime | None:
    return None if moment is None else moment + timedelta(minutes=offset)


def _start(bar: Bar, day: date, env: Env) -> datetime | None:
    earliest = env.at(day, bar.start_time) if bar.start_time else None
    if bar.start_type == "time":
        return earliest
    if bar.start_type == "sun_elevation":
        if bar.elevation is None:
            return None
        moment = env.sun.below(bar.elevation, day)
    else:
        moment = env.sun.event(bar.start_type, day)
    moment = _shifted(moment, bar.start_offset)
    if moment is None:
        return None
    return max(moment, earliest) if earliest else moment


def _end(bar: Bar, day: date, start: datetime, env: Env) -> datetime | None:
    if bar.end_type != "time":
        for candidate in (day, day + timedelta(days=1)):
            moment = _shifted(env.sun.event(bar.end_type, candidate), bar.end_offset)
            if moment is not None and moment > start:
                return moment
        return None
    if bar.end_time is None:
        return None
    moment = env.at(day, bar.end_time)
    if moment > start:
        return moment
    # A sunset can drift past an afternoon end time: that day is skipped, not 24 hours long.
    overnight = bar.end_time < NOON and start.astimezone(env.tz).time() >= NOON
    if bar.start_type == "time" or overnight:
        return env.at(day + timedelta(days=1), bar.end_time)
    return None


def window(flow: Flow, bar: Bar, day: date, env: Env) -> Window | None:
    """The window of this bar starting on this day, if any."""
    if day.weekday() not in flow.days:
        return None
    start = _start(bar, day, env)
    if start is None:
        return None
    end = _end(bar, day, start, env)
    return Window(start, end) if end is not None else None


def active_window(flow: Flow, bar: Bar, now: datetime, env: Env) -> Window | None:
    today = now.astimezone(env.tz).date()
    for day in (today, today - timedelta(days=1)):
        found = window(flow, bar, day, env)
        if found is not None and found.start <= now < found.end:
            return found
    return None


def active_bar(flow: Flow, row: Row, now: datetime, env: Env) -> tuple[Bar, Window] | None:
    """The running bar of a row; sun bars can overlap on some days, the later start wins."""
    best: tuple[Bar, Window] | None = None
    for bar in row.bars:
        found = active_window(flow, bar, now, env)
        if found is not None and (best is None or found.start >= best[1].start):
            best = (bar, found)
    return best


@dataclass(frozen=True)
class Decision:
    flow: Flow
    row: Row
    bar: Bar
    action: Action


def _decide_flow(
    flow: Flow, now: datetime, env: Env, lights_of: Callable[[Row], Iterable[str]]
) -> dict[str, tuple[datetime, Decision]]:
    """A row naming the light beats rows reaching it as a group; among those the last started wins."""
    ranked: dict[str, tuple[tuple[bool, datetime, int], Window, Bar, Row]] = {}
    for index, row in enumerate(flow.rows):
        if (running := active_bar(flow, row, now, env)) is None:
            continue
        bar, found = running
        for light in lights_of(row):
            rank = (light in row.direct, found.start, index)
            if light not in ranked or rank > ranked[light][0]:
                ranked[light] = (rank, found, bar, row)
    return {
        light: (found.start, Decision(flow, row, bar, bar.action))
        for light, (_, found, bar, row) in ranked.items()
        if bar.action != UNCHANGED
    }


def decide(
    flows: Iterable[Flow],
    now: datetime,
    env: Env,
    lights_of: Callable[[Row], Iterable[str]],
    counts: Callable[[Flow], bool] = lambda _: True,
) -> dict[str, Decision]:
    """The last started bar wins each light; "unchanged" hands it to the next flow."""
    best: dict[str, tuple[tuple[datetime, int], Decision]] = {}
    for index, flow in enumerate(flows):
        if not flow.enabled or not counts(flow):
            continue
        for light, (start, decision) in _decide_flow(flow, now, env, lights_of).items():
            rank = (start, index)
            if light not in best or rank > best[light][0]:
                best[light] = (rank, decision)
    return {light: decision for light, (_, decision) in best.items()}


def left_alone(flow: Flow, light: str, now: datetime, env: Env) -> bool:
    """The row naming this light currently says "unchanged", so this flow must not touch it."""
    for row in flow.rows:
        if light in row.direct:
            running = active_bar(flow, row, now, env)
            return running is not None and running[0].action == UNCHANGED
    return False


def run_start(flow: Flow, now: datetime, env: Env) -> datetime | None:
    """When the flow's current run began: bars that touch or overlap count as one run."""
    today = now.astimezone(env.tz).date()
    windows = [
        found
        for row in flow.rows
        for bar in row.bars
        for offset in range(-2, 1)
        if (found := window(flow, bar, today + timedelta(days=offset), env)) is not None
    ]
    begun = [found.start for found in windows if found.start <= now < found.end]
    if not begun:
        return None
    start = min(begun)
    while earlier := [f.start for f in windows if f.start < start <= f.end]:
        start = min(earlier)
    return start


def manual_counts(flow: Flow, changed: datetime, now: datetime, env: Env) -> bool:
    """A foreign change counts if it is recent or happened while this run of the flow lasts."""
    if not flow.respect_manual:
        return False
    if now - changed <= timedelta(hours=flow.manual_hours):
        return True
    begun = run_start(flow, now, env)
    return begun is not None and changed >= begun


@dataclass(frozen=True)
class Event:
    moment: datetime
    kind: str
    flow: Flow
    row: Row
    bar: Bar


def _bars(flows: Iterable[Flow]) -> Iterable[tuple[Flow, Row, Bar]]:
    for flow in flows:
        if flow.enabled:
            for row in flow.rows:
                for bar in row.bars:
                    yield flow, row, bar


def _windows(
    flows: Iterable[Flow], since: datetime, until: datetime, env: Env
) -> Iterator[tuple[Flow, Row, Bar, Window]]:
    first = since.astimezone(env.tz).date() - timedelta(days=2)
    last = until.astimezone(env.tz).date()
    for flow, row, bar in _bars(flows):
        day = first
        while day <= last:
            found = window(flow, bar, day, env)
            day += timedelta(days=1)
            if found is not None:
                yield flow, row, bar, found


def _in_order(events: list[Event]) -> list[Event]:
    return sorted(events, key=lambda e: (e.moment, e.kind != "end"))


def events_between(
    flows: Iterable[Flow], since: datetime, until: datetime, env: Env
) -> list[Event]:
    """Starts and ends in (since, until], ends first so a handover sees the new state."""
    events: list[Event] = []
    for flow, row, bar, found in _windows(flows, since, until, env):
        if since < found.start <= until:
            events.append(Event(found.start, "start", flow, row, bar))
        if since < found.end <= until:
            events.append(Event(found.end, "end", flow, row, bar))
    return _in_order(events)


def missed_events(
    flows: Iterable[Flow], since: datetime, until: datetime, env: Env
) -> list[Event]:
    """What is still relevant after an outage: a time window fully inside it changes nothing."""
    events: list[Event] = []
    for flow, row, bar, found in _windows(flows, since, until, env):
        if since < found.start <= until < found.end:
            events.append(Event(found.start, "start", flow, row, bar))
        if found.start <= since < found.end <= until:
            events.append(Event(found.end, "end", flow, row, bar))
    return _in_order(events)


def next_moment(flows: Iterable[Flow], after: datetime, env: Env) -> datetime | None:
    """Next start or end of any enabled flow within the coming days."""
    moments: list[datetime] = []
    today = after.astimezone(env.tz).date()
    for flow, _, bar in _bars(flows):
        for offset in range(-2, 9):
            found = window(flow, bar, today + timedelta(days=offset), env)
            if found is None:
                continue
            moments.extend(m for m in (found.start, found.end) if m > after)
    return min(moments, default=None)


def day_segments(flow: Flow, bar: Bar, day: date, env: Env) -> list[tuple[float, float]]:
    """Parts of the given day this bar covers, in hours, for the timeline."""
    day_start = env.at(day, time(0))
    day_end = env.at(day + timedelta(days=1), time(0))
    segments = []
    for candidate in (day - timedelta(days=1), day):
        found = window(flow, bar, candidate, env)
        if found is None:
            continue
        begin, finish = max(found.start, day_start), min(found.end, day_end)
        if begin < finish:
            segments.append(
                (
                    round((begin - day_start).total_seconds() / 3600, 3),
                    round((finish - day_start).total_seconds() / 3600, 3),
                )
            )
    return segments
