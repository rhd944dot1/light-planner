"""Full flow in the real HA test core, driven through the panel's WebSocket API."""

from datetime import datetime
from typing import Any

from custom_components.light_planner.const import DOMAIN, PANEL_PATH
from custom_components.light_planner.engine import HaSun
from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Context, CoreState
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    floor_registry as fr,
    label_registry as lr,
)
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    async_mock_service,
)


def local(hour: int, minute: int = 0) -> datetime:
    return dt_util.as_utc(dt_util.now().replace(hour=hour, minute=minute, second=0, microsecond=0))


def target_of(item: dict[str, Any]) -> dict[str, Any]:
    keys = {"light": "entity_id", "scene": "entity_id", "area": "area_id", "label": "label_id"}
    return {keys[item["type"]]: [item["id"]]}


def flow(id: str = "s", at: str = "18:00", end: str = "23:00", **extra: Any) -> dict[str, Any]:
    """One bar per target, all with the same times; own rows can be added with extra_rows."""
    targets = extra.pop("targets", [{"type": "light", "id": "light.a"}])
    look = extra.pop("look", {"mode": "white", "kelvin": 2200, "brightness": 50})
    bar = {
        "start": extra.pop("start", {"type": "time", "time": at}),
        "end": {"type": "time", "time": end},
        "look": look,
    }
    for key in ("at_start", "at_end"):
        if key in extra:
            bar[key] = extra.pop(key)
    rows = [
        {"id": f"{id}-{n}", "target": target_of(target), "bars": [{**bar, "id": f"{id}-{n}-0"}]}
        for n, target in enumerate(targets)
    ]
    return {
        "id": id,
        "name": id,
        "days": [0, 1, 2, 3, 4, 5, 6],
        "rows": rows + extra.pop("extra_rows", []),
        **extra,
    }


def own_row(light: str, at: str, end: str, look: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {
        "id": f"own-{light}",
        "target": {"entity_id": [light]},
        "bars": [
            {
                "id": f"own-{light}-{at}",
                "start": {"type": "time", "time": at},
                "end": {"type": "time", "time": end},
                "look": look,
                **extra,
            }
        ],
    }


WARM = {"color_temp_kelvin": 2200, "brightness_pct": 50}


@pytest.fixture
def on(hass):
    return async_mock_service(hass, "light", "turn_on")


@pytest.fixture
def off(hass):
    return async_mock_service(hass, "light", "turn_off")


async def setup(hass) -> MockConfigEntry:
    for light in ("a", "b", "c"):
        hass.states.async_set(f"light.{light}", "on")
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    return entry


async def save(client, *flows: dict[str, Any]) -> None:
    for item in flows:
        await client.send_json_auto_id({"type": f"{DOMAIN}/save", "flow": item})
        result = await client.receive_json()
        assert result["success"], result


async def to(hass, freezer, moment: datetime) -> None:
    freezer.move_to(moment)
    async_fire_time_changed(hass, moment)
    await hass.async_block_till_done()


def calls(mock) -> dict[str, dict]:
    result = {}
    for call in mock:
        data = dict(call.data)
        result[data.pop("entity_id")] = data
    return result


@pytest.fixture
async def client(hass, hass_ws_client, freezer):
    # Routes must exist before connecting, and the auth token before time is frozen.
    entry = await setup(hass)
    connection = await hass_ws_client(hass)
    freezer.move_to(local(12))
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    return connection


async def test_start_turns_on_and_end_turns_off(hass, client, freezer, on, off) -> None:
    await save(client, flow())
    await to(hass, freezer, local(18))
    assert calls(on) == {"light.a": WARM}
    assert not off
    await to(hass, freezer, local(23))
    assert calls(off) == {"light.a": {}}


async def test_adjust_only_touches_lights_that_are_on(hass, client, freezer, on) -> None:
    hass.states.async_set("light.b", "off")
    targets = [{"type": "light", "id": "light.a"}, {"type": "light", "id": "light.b"}]
    await save(client, flow(targets=targets, at_start="adjust"))
    await to(hass, freezer, local(18))
    assert calls(on) == {"light.a": WARM}


async def test_later_flow_wins_and_earlier_takes_over_again(
    hass, client, freezer, on, off
) -> None:
    red = {"mode": "color", "rgb": [255, 0, 0]}
    await save(
        client,
        flow("long", at="17:00", end="23:30"),
        flow("short", at="20:00", end="21:00", look=red),
    )
    await to(hass, freezer, local(20))
    assert calls(on) == {"light.a": {"rgb_color": [255, 0, 0]}}
    on.clear()
    await to(hass, freezer, local(21))
    assert calls(on) == {"light.a": WARM}
    assert not off


async def test_end_of_an_outranked_flow_leaves_the_light_alone(
    hass, client, freezer, on, off
) -> None:
    red = {"mode": "color", "rgb": [255, 0, 0]}
    await save(
        client,
        flow("first", at="17:00", end="20:00"),
        flow("second", at="18:00", end="23:00", look=red),
    )
    await to(hass, freezer, local(20))
    assert calls(on) == {"light.a": {"rgb_color": [255, 0, 0]}}
    assert not off


async def test_off_and_unchanged_own_rows(hass, client, freezer, on, off) -> None:
    entities, labels = er.async_get(hass), lr.async_get(hass)
    label = labels.async_create("Evening")
    for light in ("x", "y", "z"):
        lamp = entities.async_get_or_create("light", "test", light, suggested_object_id=light)
        entities.async_update_entity(lamp.entity_id, labels={label.label_id})
    await save(
        client,
        flow(
            targets=[{"type": "label", "id": label.label_id}],
            extra_rows=[
                own_row("light.y", "18:00", "23:00", {"mode": "off"}),
                own_row("light.z", "18:00", "23:00", {"mode": "unchanged"}),
            ],
        ),
    )
    await to(hass, freezer, local(18))
    assert calls(on) == {"light.x": WARM}
    assert calls(off) == {"light.y": {}}
    off.clear()
    await to(hass, freezer, local(23))
    assert set(calls(off)) == {"light.x", "light.y"}


async def test_flow_with_lights_joining_and_leaving(hass, client, freezer, on, off) -> None:
    await save(
        client,
        flow(
            at="16:00",
            end="23:00",
            extra_rows=[
                own_row("light.b", "17:30", "23:00", {"mode": "keep"}),
                own_row("light.c", "16:00", "19:00", {"mode": "keep"}),
            ],
        ),
    )
    await to(hass, freezer, local(16))
    assert set(calls(on)) == {"light.a", "light.c"}
    on.clear()
    await to(hass, freezer, local(17, 30))
    assert set(calls(on)) == {"light.b"}
    await to(hass, freezer, local(19))
    assert set(calls(off)) == {"light.c"}


async def test_own_row_takes_over_and_gives_back_to_the_label_row(
    hass, client, freezer, on, off
) -> None:
    entities, labels = er.async_get(hass), lr.async_get(hass)
    label = labels.async_create("Evening")
    lamp = entities.async_get_or_create("light", "test", "x", suggested_object_id="x")
    entities.async_update_entity(lamp.entity_id, labels={label.label_id})
    red = {"mode": "color", "rgb": [255, 0, 0]}
    await save(
        client,
        flow(
            at="16:00",
            end="23:30",
            targets=[{"type": "label", "id": label.label_id}],
            extra_rows=[own_row("light.x", "20:00", "22:00", red)],
        ),
    )
    await to(hass, freezer, local(20))
    assert calls(on) == {"light.x": {"rgb_color": [255, 0, 0]}}
    on.clear()
    await to(hass, freezer, local(22))
    assert calls(on) == {"light.x": WARM}
    assert not off


async def test_end_of_a_label_bar_spares_a_light_left_alone(
    hass, client, freezer, on, off
) -> None:
    entities, labels = er.async_get(hass), lr.async_get(hass)
    label = labels.async_create("Evening")
    lamp = entities.async_get_or_create("light", "test", "x", suggested_object_id="x")
    entities.async_update_entity(lamp.entity_id, labels={label.label_id})
    await save(
        client,
        flow(
            at="16:00",
            end="20:00",
            targets=[{"type": "label", "id": label.label_id}],
            extra_rows=[own_row("light.x", "19:00", "21:00", {"mode": "unchanged"})],
        ),
    )
    await to(hass, freezer, local(20))
    assert not off


async def test_end_of_leave_alone_returns_the_light_to_its_label_row(
    hass, client, freezer, on, off
) -> None:
    entities, labels = er.async_get(hass), lr.async_get(hass)
    label = labels.async_create("Evening")
    lamp = entities.async_get_or_create("light", "test", "x", suggested_object_id="x")
    entities.async_update_entity(lamp.entity_id, labels={label.label_id})
    await save(
        client,
        flow(
            at="16:00",
            end="23:00",
            targets=[{"type": "label", "id": label.label_id}],
            extra_rows=[own_row("light.x", "19:00", "21:00", {"mode": "unchanged"})],
        ),
    )
    await to(hass, freezer, local(21))
    assert calls(on) == {"light.x": WARM}
    assert not off


async def test_end_of_leave_alone_alone_does_nothing(hass, client, freezer, off) -> None:
    await save(client, flow(look={"mode": "unchanged"}))
    await to(hass, freezer, local(23))
    assert not off


async def test_each_bar_restores_for_itself(hass, client, freezer, on) -> None:
    hass.states.async_set("light.a", "on", {"brightness": 77, "color_mode": "brightness"})
    item = flow(at="18:00", end="19:00", at_end="restore")
    item["rows"][0]["bars"].append(
        {
            "id": "second",
            "start": {"type": "time", "time": "20:00"},
            "end": {"type": "time", "time": "21:00"},
            "look": {"mode": "keep", "brightness": 10},
            "at_end": "restore",
        }
    )
    await save(client, item)
    await to(hass, freezer, local(18))
    on.clear()
    await to(hass, freezer, local(19))
    assert calls(on) == {"light.a": {"brightness": 77}}
    hass.states.async_set("light.a", "on", {"brightness": 200, "color_mode": "brightness"})
    await to(hass, freezer, local(20))
    on.clear()
    await to(hass, freezer, local(21))
    assert calls(on) == {"light.a": {"brightness": 200}}


def native_flow(target: dict[str, Any], at: str = "18:00", end: str = "23:00") -> dict[str, Any]:
    return {
        "id": "n",
        "name": "n",
        "days": [0, 1, 2, 3, 4, 5, 6],
        "rows": [
            {
                "id": "r",
                "target": target,
                "bars": [
                    {
                        "id": "b",
                        "start": {"type": "time", "time": at},
                        "end": {"type": "time", "time": end},
                        "look": {"mode": "white", "kelvin": 2200, "brightness": 50},
                    }
                ],
            }
        ],
    }


def device_with_lights(hass, *names: str) -> str:
    entry = MockConfigEntry(domain="test")
    entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={("test", names[0])}
    )
    entities = er.async_get(hass)
    for name in names:
        entities.async_get_or_create(
            "light", "test", name, suggested_object_id=name, device_id=device.id
        )
    return device.id


async def test_device_target_switches_its_lights(hass, client, freezer, on) -> None:
    device = device_with_lights(hass, "x", "y")
    await save(client, native_flow({"device_id": [device]}))
    await to(hass, freezer, local(18))
    assert set(calls(on)) == {"light.x", "light.y"}


async def test_exclude_leaves_out_a_light_of_a_device(hass, client, freezer, on) -> None:
    device = device_with_lights(hass, "x", "led")
    await save(
        client,
        native_flow({"device_id": [device], "exclude": {"entity_id": ["light.led"]}}),
    )
    await to(hass, freezer, local(18))
    assert set(calls(on)) == {"light.x"}


async def test_exclude_can_take_out_a_whole_area(hass, client, freezer, on) -> None:
    entities, labels, areas = er.async_get(hass), lr.async_get(hass), ar.async_get(hass)
    label = labels.async_create("Evening")
    area = areas.async_create("Kitchen")
    for name, place in (("x", None), ("y", area.id)):
        lamp = entities.async_get_or_create("light", "test", name, suggested_object_id=name)
        entities.async_update_entity(lamp.entity_id, labels={label.label_id}, area_id=place)
    await save(
        client,
        native_flow({"label_id": [label.label_id], "exclude": {"area_id": [area.id]}}),
    )
    await to(hass, freezer, local(18))
    assert set(calls(on)) == {"light.x"}


async def test_floor_target(hass, client, freezer, on) -> None:
    floor = fr.async_get(hass).async_create("Ground")
    area = ar.async_get(hass).async_create("Hall", floor_id=floor.floor_id)
    entities = er.async_get(hass)
    lamp = entities.async_get_or_create("light", "test", "x", suggested_object_id="x")
    entities.async_update_entity(lamp.entity_id, area_id=area.id)
    await save(client, native_flow({"floor_id": [floor.floor_id]}))
    await to(hass, freezer, local(18))
    assert set(calls(on)) == {"light.x"}


async def test_one_row_with_several_targets_and_a_scene(hass, client, freezer, on) -> None:
    scenes = async_mock_service(hass, "scene", "turn_on")
    hass.states.async_set("scene.movie", "scening")
    await save(client, native_flow({"entity_id": ["light.a", "light.b", "scene.movie"]}))
    await to(hass, freezer, local(18))
    assert set(calls(on)) == {"light.a", "light.b"}
    assert calls(scenes) == {"scene.movie": {}}


async def test_area_does_not_activate_a_scene_in_it(hass, client, freezer) -> None:
    scenes = async_mock_service(hass, "scene", "turn_on")
    entities, areas = er.async_get(hass), ar.async_get(hass)
    area = areas.async_create("Kitchen")
    scene = entities.async_get_or_create("scene", "test", "s", suggested_object_id="s")
    entities.async_update_entity(scene.entity_id, area_id=area.id)
    hass.states.async_set("scene.s", "scening")
    await save(client, native_flow({"area_id": [area.id]}))
    await to(hass, freezer, local(18))
    assert not scenes


async def test_mixed_targets_label_area_light(hass, client, freezer, on) -> None:
    entities, labels, areas = er.async_get(hass), lr.async_get(hass), ar.async_get(hass)
    label = labels.async_create("Evening")
    area = areas.async_create("Outside")
    lamp = entities.async_get_or_create("light", "test", "lab", suggested_object_id="lab")
    entities.async_update_entity(lamp.entity_id, labels={label.label_id})
    lamp = entities.async_get_or_create("light", "test", "are", suggested_object_id="are")
    entities.async_update_entity(lamp.entity_id, area_id=area.id)
    await save(
        client,
        flow(
            targets=[
                {"type": "label", "id": label.label_id},
                {"type": "area", "id": area.id},
                {"type": "light", "id": "light.c"},
                {"type": "light", "id": "light.lab"},
            ]
        ),
    )
    await to(hass, freezer, local(18))
    assert sorted(c.data["entity_id"] for c in on) == ["light.are", "light.c", "light.lab"]


async def test_new_labeled_light_joins_without_restart(hass, client, freezer, on) -> None:
    entities, labels = er.async_get(hass), lr.async_get(hass)
    label = labels.async_create("Evening")
    await save(client, flow(targets=[{"type": "label", "id": label.label_id}]))
    lamp = entities.async_get_or_create("light", "test", "new", suggested_object_id="new")
    entities.async_update_entity(lamp.entity_id, labels={label.label_id})
    await to(hass, freezer, local(18))
    assert calls(on) == {"light.new": WARM}


async def test_area_skips_indicator_lights(hass, client, freezer, on) -> None:
    entities, areas = er.async_get(hass), ar.async_get(hass)
    area = areas.async_create("Outside")
    led = entities.async_get_or_create(
        "light", "test", "led", suggested_object_id="led", entity_category=er.EntityCategory.CONFIG
    )
    entities.async_update_entity(led.entity_id, area_id=area.id)
    await save(client, flow(targets=[{"type": "area", "id": area.id}]))
    await to(hass, freezer, local(18))
    assert not on


async def test_scene_activates_and_restore_brings_back_state(hass, client, freezer, on, off) -> None:
    scenes = async_mock_service(hass, "scene", "turn_on")
    hass.states.async_set("scene.movie", "scening", {"entity_id": ["light.a", "light.b"]})
    hass.states.async_set("light.a", "on", {"brightness": 77, "color_mode": "brightness"})
    hass.states.async_set("light.b", "off")
    await save(
        client,
        flow(targets=[{"type": "scene", "id": "scene.movie"}], at_end="restore"),
    )
    await to(hass, freezer, local(18))
    assert calls(scenes) == {"scene.movie": {}}
    await to(hass, freezer, local(23))
    assert calls(on) == {"light.a": {"brightness": 77}}
    assert calls(off) == {"light.b": {}}


async def test_restore_of_overlapping_flows_returns_the_original(
    hass, client, freezer, on
) -> None:
    hass.states.async_set("light.a", "on", {"brightness": 77, "color_mode": "brightness"})
    await save(
        client,
        flow("first", at="17:00", end="20:00", at_end="restore"),
        flow("second", at="18:00", end="23:00", at_end="restore"),
    )
    await to(hass, freezer, local(17))
    hass.states.async_set("light.a", "on", {"brightness": 127, "color_mode": "brightness"})
    await to(hass, freezer, local(18))
    await to(hass, freezer, local(20))
    on.clear()
    await to(hass, freezer, local(23))
    assert calls(on) == {"light.a": {"brightness": 77}}


async def test_restore_survives_a_reload(hass, client, freezer, on) -> None:
    hass.states.async_set("light.a", "on", {"brightness": 77, "color_mode": "brightness"})
    await save(client, flow(at_end="restore"))
    await to(hass, freezer, local(18))
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    on.clear()
    await to(hass, freezer, local(23))
    assert calls(on) == {"light.a": {"brightness": 77}}


async def test_condition_blocks_start(hass, client, freezer, on) -> None:
    hass.states.async_set("person.x", "not_home")
    await save(client, flow(condition="anyone_home"))
    await to(hass, freezer, local(18))
    assert not on


async def test_arrival_applies_everything_for_the_current_time(hass, client, freezer, on) -> None:
    """The original question: one light differs from 18:51, arriving later still sets all."""
    hass.states.async_set("person.x", "not_home")
    hass.states.async_set("light.a", "off")
    hass.states.async_set("light.b", "off")
    await save(
        client,
        flow(
            "evening",
            at="17:00",
            end="23:30",
            condition="anyone_home",
            targets=[{"type": "light", "id": "light.a"}, {"type": "light", "id": "light.b"}],
        ),
        flow(
            "kids",
            at="18:51",
            end="23:30",
            condition="anyone_home",
            at_start="adjust",
            look={"mode": "color", "rgb": [255, 0, 0]},
            targets=[{"type": "light", "id": "light.b"}],
        ),
    )
    await to(hass, freezer, local(20))
    assert not on
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert calls(on) == {"light.a": WARM, "light.b": {"rgb_color": [255, 0, 0]}}


async def test_arrival_can_be_disabled(hass, client, freezer, on) -> None:
    hass.states.async_set("person.x", "not_home")
    await save(client, flow(at="11:00", condition="anyone_home", on_arrival="nothing"))
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert not on


async def test_arrival_outside_the_window_does_nothing(hass, client, on) -> None:
    hass.states.async_set("person.x", "not_home")
    await save(client, flow(condition="anyone_home"))
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert not on


async def test_second_person_is_no_arrival(hass, client, on) -> None:
    hass.states.async_set("person.x", "home")
    hass.states.async_set("person.y", "not_home")
    await save(client, flow(at="11:00", condition="anyone_home"))
    hass.states.async_set("person.y", "home")
    await hass.async_block_till_done()
    assert not on


async def test_everyone_home_needs_the_last_person(hass, client, on) -> None:
    hass.states.async_set("person.x", "not_home")
    hass.states.async_set("person.y", "not_home")
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    await save(client, flow(at="11:00", condition="everyone_home"))
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert not on
    hass.states.async_set("person.y", "home")
    await hass.async_block_till_done()
    assert calls(on) == {"light.a": WARM}


async def test_specific_person(hass, client, on) -> None:
    hass.states.async_set("person.x", "not_home")
    hass.states.async_set("person.y", "not_home")
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    await save(client, flow(at="11:00", condition="person", person="person.y"))
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert not on
    hass.states.async_set("person.y", "home")
    await hass.async_block_till_done()
    assert calls(on) == {"light.a": WARM}


async def test_nobody_home_applies_when_the_last_person_leaves(hass, client, on) -> None:
    hass.states.async_set("person.x", "home")
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    await save(client, flow(at="11:00", condition="nobody_home"))
    hass.states.async_set("person.x", "not_home")
    await hass.async_block_till_done()
    assert calls(on) == {"light.a": WARM}


async def test_return_from_unavailable_is_no_arrival(hass, client, on) -> None:
    hass.states.async_set("person.x", "unavailable")
    await save(client, flow(at="11:00", condition="anyone_home"))
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert not on


async def test_startup_does_not_count_as_arrival(hass, hass_ws_client, on) -> None:
    hass.states.async_set("person.x", "not_home")
    hass.set_state(CoreState.not_running)
    await setup(hass)
    client = await hass_ws_client(hass)
    await save(client, flow(at="00:00", end="23:59", condition="anyone_home"))
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert not on

    hass.set_state(CoreState.running)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()
    assert not on

    hass.states.async_set("person.x", "not_home")
    await hass.async_block_till_done()
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert on


async def test_disabled_flow_does_nothing(hass, client, freezer, on) -> None:
    await save(client, flow(enabled=False))
    await to(hass, freezer, local(18))
    assert not on


async def test_deleted_flow_does_nothing(hass, client, freezer, on) -> None:
    await save(client, flow())
    await client.send_json_auto_id({"type": f"{DOMAIN}/delete", "flow_id": "s"})
    assert (await client.receive_json())["success"]
    await to(hass, freezer, local(18))
    assert not on


async def test_broken_light_does_not_stop_the_others(hass, client, freezer) -> None:
    targets = [{"type": "light", "id": f"light.{x}"} for x in "ab"]
    seen = []

    async def handler(call):
        seen.append(call.data["entity_id"])
        if call.data["entity_id"] == "light.a":
            raise HomeAssistantError("broken")

    hass.services.async_register("light", "turn_on", handler)
    await save(client, flow(targets=targets))
    await to(hass, freezer, local(18))
    assert seen == ["light.a", "light.b"]


async def test_sunset_flow_uses_the_sun(hass, client, freezer, on) -> None:
    await save(client, flow(start={"type": "sunset", "time": None}))
    await to(hass, freezer, local(16, 59))
    assert not on
    await to(hass, freezer, local(17))
    assert calls(on) == {"light.a": WARM}


async def test_save_rejects_incomplete_and_list_returns_saved(hass, client) -> None:
    await client.send_json_auto_id(
        {"type": f"{DOMAIN}/save", "flow": flow(name=" ")}
    )
    result = await client.receive_json()
    assert not result["success"]
    assert "name" in result["error"]["message"]

    await save(client, flow())
    await save(client, flow(name="renamed"))
    await client.send_json_auto_id({"type": f"{DOMAIN}/list"})
    saved = (await client.receive_json())["result"]["flows"]
    assert [s["name"] for s in saved] == ["renamed"]


async def test_options_list_home_assistant_objects(hass, client) -> None:
    lr.async_get(hass).async_create("Evening")
    ar.async_get(hass).async_create("Outside")
    hass.states.async_set("scene.movie", "scening")
    hass.states.async_set("person.x", "home", {"friendly_name": "Alex"})
    await client.send_json_auto_id({"type": f"{DOMAIN}/options"})
    options = (await client.receive_json())["result"]
    assert {"id": "light.a", "name": "a"} in options["light"]
    assert options["scene"] == [{"id": "scene.movie", "name": "movie"}]
    assert options["person"] == [{"id": "person.x", "name": "Alex"}]
    assert options["label"][0]["name"] == "Evening"
    assert options["area"][0]["name"] == "Outside"


async def preview(client, *flows, weekday=None, at="20:00") -> dict[str, Any]:
    if weekday is None:
        weekday = dt_util.now().weekday()
    await client.send_json_auto_id(
        {"type": f"{DOMAIN}/preview", "flows": list(flows), "weekday": weekday, "time": at}
    )
    result = await client.receive_json()
    assert result["success"], result
    return result["result"]


async def test_preview_on_unsaved_drafts(hass, client) -> None:
    result = await preview(
        client,
        flow(
            "long",
            at="17:00",
            extra_rows=[
                own_row("light.b", "17:00", "23:00", {"mode": "off"}),
                own_row("light.c", "17:00", "23:00", {"mode": "unchanged"}),
            ],
        ),
    )
    by_id = {light["id"]: light for light in result["lights"]}
    assert by_id["light.a"]["action"]["kind"] == "look"
    assert by_id["light.a"]["flow"] == "long"
    assert by_id["light.a"]["row"] == "long-0"
    assert by_id["light.b"]["action"] == {"kind": "off"}
    assert by_id["light.c"]["action"] is None
    assert result["flows"]["long"]["bars"]["long-0-0"] == [[17.0, 23.0]]
    assert result["flows"]["long"]["rows"]["long-0"] == [{"id": "light.a", "name": "a"}]


async def test_preview_gives_the_sun_of_that_day(hass, client) -> None:
    sun = (await preview(client))["sun"]
    assert (sun["sunset"], sun["sunrise"]) == (17.0, 7.0)
    assert [-12, 16.0] in sun["below"]


async def test_preview_skips_on_arrival_nothing_and_broken_drafts(hass, client) -> None:
    result = await preview(
        client,
        flow("quiet", at="17:00", on_arrival="nothing"),
        {"id": "broken"},
    )
    assert result["lights"][0]["action"] is None
    assert "broken" not in result["flows"]


async def test_preview_lists_active_scenes(hass, client) -> None:
    hass.states.async_set("scene.movie", "scening", {"friendly_name": "Movie"})
    result = await preview(client, flow(targets=[{"type": "scene", "id": "scene.movie"}]))
    assert result["scenes"] == [{"id": "scene.movie", "name": "Movie"}]


async def apply_now(client, item: dict[str, Any]) -> None:
    await client.send_json_auto_id({"type": f"{DOMAIN}/apply_now", "flow": item})
    assert (await client.receive_json())["success"]


async def test_apply_now_uses_what_runs_at_this_moment(hass, client, off, on) -> None:
    await apply_now(client, flow())
    assert not on
    hass.states.async_set("person.x", "not_home")
    await apply_now(client, flow(at="11:00", condition="anyone_home", enabled=False))
    assert calls(on) == {"light.a": WARM}


async def test_apply_now_activates_running_scenes(hass, client) -> None:
    scenes = async_mock_service(hass, "scene", "turn_on")
    hass.states.async_set("scene.movie", "scening")
    await apply_now(client, flow(at="11:00", targets=[{"type": "scene", "id": "scene.movie"}]))
    assert calls(scenes) == {"scene.movie": {}}


MANUAL = {"respect_manual": True}


def light_on(hass, entity: str = "light.a", **extra: Any) -> None:
    hass.states.async_set(
        entity, "on", {"brightness": 100, "color_mode": "brightness", **extra.pop("attributes", {})}, **extra
    )


async def test_manual_change_before_the_start_is_left_alone(hass, client, freezer, on) -> None:
    await save(client, flow(**MANUAL))
    await to(hass, freezer, local(17))
    hass.states.async_set("light.a", "off")
    await to(hass, freezer, local(18))
    assert not on


async def test_only_lights_of_flows_with_the_flag_are_watched(hass, client) -> None:
    store = hass.data[DOMAIN].store
    await save(client, flow("plain"), flow("flagged", targets=[{"type": "light", "id": "light.b"}], **MANUAL))
    hass.states.async_set("light.a", "off")
    hass.states.async_set("light.c", "off")
    assert not store.manual
    hass.states.async_set("light.b", "off")
    assert set(store.manual) == {"light.b"}


async def test_without_the_flag_manual_changes_are_ignored(hass, client, freezer, on) -> None:
    await save(client, flow())
    await to(hass, freezer, local(17))
    hass.states.async_set("light.a", "off")
    await to(hass, freezer, local(18))
    assert calls(on) == {"light.a": WARM}


async def test_old_manual_change_no_longer_counts(hass, client, freezer, on) -> None:
    await save(client, flow(at="18:00", manual_hours=2, **MANUAL))
    await to(hass, freezer, local(15))
    hass.states.async_set("light.a", "off")
    await to(hass, freezer, local(17, 59))
    await to(hass, freezer, local(18))
    assert calls(on) == {"light.a": WARM}


async def test_user_and_automation_changes_both_count(hass, client, freezer, on) -> None:
    await save(
        client,
        flow(
            targets=[{"type": "light", "id": "light.a"}, {"type": "light", "id": "light.b"}],
            **MANUAL,
        ),
    )
    await to(hass, freezer, local(17))
    hass.states.async_set("light.a", "off", context=Context(user_id="someone"))
    hass.states.async_set("light.b", "off", context=Context(parent_id="automation"))
    await to(hass, freezer, local(18))
    assert not on


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ({"brightness": 100}, {"brightness": 104}),
        (
            {"color_mode": "color_temp", "color_temp_kelvin": 2700},
            {"color_mode": "color_temp", "color_temp_kelvin": 2750},
        ),
        ({"rgb_color": [255, 0, 0]}, {"rgb_color": [250, 5, 10]}),
        ({"brightness": None}, {"brightness": 100}),
    ],
)
async def test_small_differences_are_no_manual_change(
    hass, client, freezer, on, first, second
) -> None:
    light_on(hass, attributes=first)
    await save(client, flow(**MANUAL))
    hass.data[DOMAIN].store.manual.clear()
    await to(hass, freezer, local(17))
    light_on(hass, attributes=second)
    await to(hass, freezer, local(18))
    assert set(calls(on)) == {"light.a"}


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ({"brightness": 100}, {"brightness": 150}),
        (
            {"color_mode": "color_temp", "color_temp_kelvin": 2700},
            {"color_mode": "color_temp", "color_temp_kelvin": 4000},
        ),
        ({"rgb_color": [255, 0, 0]}, {"rgb_color": [0, 0, 255]}),
    ],
)
async def test_visible_changes_count(hass, client, freezer, on, first, second) -> None:
    light_on(hass, attributes=first)
    await save(client, flow(**MANUAL))
    await to(hass, freezer, local(17))
    light_on(hass, attributes=second)
    await to(hass, freezer, local(18))
    assert not on


async def test_return_from_unavailable_is_no_manual_change(hass, client, freezer, on) -> None:
    await save(client, flow(**MANUAL))
    hass.data[DOMAIN].store.manual.clear()
    await to(hass, freezer, local(17))
    hass.states.async_set("light.a", "unavailable")
    hass.states.async_set("light.a", "on")
    await to(hass, freezer, local(18))
    assert set(calls(on)) == {"light.a"}


async def test_own_switching_is_no_manual_change(hass, client, freezer) -> None:
    """Our call, a late report without context, and an automation reacting to us."""
    seen = []

    async def handler(call):
        seen.append(call.data["entity_id"])
        hass.states.async_set(
            "light.a", "on" if call.service == "turn_on" else "off", context=call.context
        )
        hass.states.async_set(
            "light.a", "on", {"brightness": 50}, context=Context(parent_id=call.context.id)
        )

    hass.services.async_register("light", "turn_on", handler)
    hass.states.async_set("light.a", "off")
    await save(client, flow("first", at="18:00", end="19:00", at_end="nothing", **MANUAL))
    hass.data[DOMAIN].store.manual.clear()
    await to(hass, freezer, local(18))
    assert seen == ["light.a"]
    assert not hass.data[DOMAIN].store.manual
    hass.states.async_set("light.a", "on", {"brightness": 200})
    assert not hass.data[DOMAIN].store.manual
    freezer.tick(16)
    hass.states.async_set("light.a", "on", {"brightness": 100})
    assert "light.a" in hass.data[DOMAIN].store.manual


async def test_a_user_right_after_our_command_still_counts(hass, client, freezer, on) -> None:
    await save(client, flow(**MANUAL))
    hass.data[DOMAIN].store.manual.clear()
    await to(hass, freezer, local(18))
    hass.states.async_set("light.a", "off", context=Context(user_id="someone"))
    assert "light.a" in hass.data[DOMAIN].store.manual


async def test_change_during_the_run_blocks_next_bar_but_not_the_end(
    hass, client, freezer, on, off
) -> None:
    item = flow(at="18:00", end="19:00", **MANUAL)
    second = {
        "id": "second",
        "start": {"type": "time", "time": "19:00"},
        "end": {"type": "time", "time": "21:00"},
        "look": {"mode": "keep", "brightness": 10},
    }
    item["rows"][0]["bars"].append(second)
    await save(client, item)
    hass.data[DOMAIN].store.manual.clear()
    await to(hass, freezer, local(18))
    on.clear()
    await to(hass, freezer, local(18, 30))
    hass.states.async_set("light.a", "off", context=Context(user_id="someone"))
    await to(hass, freezer, local(19))
    assert not on
    assert not off
    await to(hass, freezer, local(21))
    assert calls(off) == {"light.a": {}}


async def test_end_of_the_run_forgets_the_change(hass, client, freezer, on) -> None:
    await save(
        client,
        flow("first", at="18:00", end="19:00", **MANUAL),
        flow("second", at="20:00", end="21:00", **MANUAL),
    )
    hass.data[DOMAIN].store.manual.clear()
    await to(hass, freezer, local(18))
    await to(hass, freezer, local(18, 30))
    hass.states.async_set("light.a", "off", context=Context(user_id="someone"))
    await to(hass, freezer, local(19))
    assert "light.a" not in hass.data[DOMAIN].store.manual
    on.clear()
    await to(hass, freezer, local(20))
    assert calls(on) == {"light.a": WARM}


async def test_other_running_flow_keeps_the_change(hass, client, freezer) -> None:
    await save(
        client,
        flow("first", at="18:00", end="19:00", **MANUAL),
        flow("second", at="18:00", end="21:00", **MANUAL),
    )
    await to(hass, freezer, local(18, 30))
    hass.states.async_set("light.a", "off", context=Context(user_id="someone"))
    await to(hass, freezer, local(19))
    assert "light.a" in hass.data[DOMAIN].store.manual


async def test_flow_without_flag_still_switches_the_light(hass, client, freezer, on) -> None:
    red = {"mode": "color", "rgb": [255, 0, 0]}
    await save(client, flow("plain", at="18:00", look=red), flow("flagged", at="17:30", **MANUAL))
    await to(hass, freezer, local(17, 45))
    hass.states.async_set("light.a", "off")
    await to(hass, freezer, local(18))
    assert calls(on) == {"light.a": {"rgb_color": [255, 0, 0]}}


async def test_arrival_respects_manual_changes(hass, client, on) -> None:
    hass.states.async_set("person.x", "not_home")
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    await save(client, flow(at="11:00", condition="anyone_home", **MANUAL))
    hass.states.async_set("light.a", "off")
    await hass.async_block_till_done()
    hass.states.async_set("person.x", "home")
    await hass.async_block_till_done()
    assert not on


async def test_scene_waits_if_one_of_its_lights_was_changed(hass, client, freezer) -> None:
    scenes = async_mock_service(hass, "scene", "turn_on")
    hass.states.async_set("scene.movie", "scening", {"entity_id": ["light.a", "light.b"]})
    await save(client, flow(targets=[{"type": "scene", "id": "scene.movie"}], **MANUAL))
    await to(hass, freezer, local(17))
    hass.states.async_set("light.b", "off")
    await to(hass, freezer, local(18))
    assert not scenes


async def test_manual_change_survives_a_reload(hass, client, freezer, on) -> None:
    await save(client, flow(**MANUAL))
    await to(hass, freezer, local(17))
    hass.states.async_set("light.a", "off")
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    await to(hass, freezer, local(18))
    assert not on


async def test_apply_now_overrules_and_forgets(hass, client, on) -> None:
    item = flow(at="11:00", **MANUAL)
    await save(client, item)
    hass.states.async_set("light.a", "off")
    assert "light.a" in hass.data[DOMAIN].store.manual
    await apply_now(client, item)
    assert calls(on) == {"light.a": WARM}
    assert "light.a" not in hass.data[DOMAIN].store.manual


async def test_preview_lists_and_clear_forgets(hass, client) -> None:
    item = flow(at="11:00", **MANUAL)
    await save(client, item)
    assert (await preview(client, item))["flows"]["s"]["manual"] == []
    hass.states.async_set("light.a", "off")
    listed = (await preview(client, item))["flows"]["s"]["manual"]
    assert [light["id"] for light in listed] == ["light.a"]
    assert (await preview(client, flow(at="11:00")))["flows"]["s"]["manual"] == []
    await client.send_json_auto_id({"type": f"{DOMAIN}/clear_manual", "entity_id": "light.a"})
    assert (await client.receive_json())["success"]
    assert (await preview(client, item))["flows"]["s"]["manual"] == []


async def test_panel_is_registered_and_removed_on_unload(hass, client) -> None:
    assert PANEL_PATH in hass.data[frontend.DATA_PANELS]
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert PANEL_PATH not in hass.data[frontend.DATA_PANELS]


async def test_unload_stops_timers(hass, client, freezer, on) -> None:
    await save(client, flow())
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    await to(hass, freezer, local(18))
    assert not on


async def test_config_flow_only_once(hass) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    await hass.async_block_till_done()
    assert result["type"] == "create_entry"
    again = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert again["type"] == "abort"


@pytest.mark.real_sun
async def test_real_sun_moments(hass) -> None:
    hass.config.latitude, hass.config.longitude = 48.0, 2.0
    sun = HaSun(hass)
    day = datetime(2026, 11, 2).date()
    sunset = sun.event("sunset", day)
    below = sun.below(12, day)
    assert below < sunset
    assert sun.below(50, day) is not None  # never that high in November: below all day
    assert sun.below(-80, day) is None  # never that low: above that all day
