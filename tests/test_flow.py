"""Flow model and its validation."""

from datetime import time
from typing import Any

from custom_components.light_planner.schedule import (
    FLOW_SCHEMA,
    upgrade_flow,
    OFF,
    UNCHANGED,
    Flow,
    Look,
    flow_incomplete_reason,
)
import pytest
import voluptuous as vol

WARM = {"mode": "white", "kelvin": 2200, "brightness": 50}


def bar(id: str = "b", start: str = "18:00", end: str = "23:00", **extra: Any) -> dict[str, Any]:
    return {
        "id": id,
        "start": extra.pop("start_block", {"type": "time", "time": start}),
        "end": extra.pop("end_block", {"type": "time", "time": end}),
        "look": extra.pop("look", WARM),
        **extra,
    }


def row(*bars: dict[str, Any], kind: str = "entity_id", target: str = "light.a") -> dict[str, Any]:
    return {"id": f"{kind}-{target}", "target": {kind: [target]}, "bars": list(bars)}


def flow(*rows: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return FLOW_SCHEMA(
        {
            "id": "f",
            "name": "Evening",
            "days": [0, 1, 2, 3, 4, 5, 6],
            "rows": list(rows) if rows else [row(bar())],
            **extra,
        }
    )


def test_defaults_are_filled_in() -> None:
    data = flow()
    assert data["enabled"] is True
    assert data["condition"] == "always"
    assert data["on_arrival"] == "apply"
    assert data["respect_manual"] is False
    assert data["manual_hours"] == 4
    assert data["rows"][0]["bars"][0]["start"]["offset"] == 0
    assert data["rows"][0]["bars"][0]["at_start"] == "turn_on"
    assert data["rows"][0]["bars"][0]["at_end"] == "turn_off"


def test_times_are_normalized() -> None:
    assert flow(row(bar(start="18:00:00")))["rows"][0]["bars"][0]["start"]["time"] == "18:00"


@pytest.mark.parametrize(
    "change",
    [
        {"manual_hours": 0},
        {"manual_hours": 25},
        {"condition": "sometimes"},
        {"rows": [row(bar(look={"mode": "sparkle"}))]},
        {"rows": [row(bar(start_block={"type": "time", "time": "18:00", "offset": 721}))]},
        {"rows": [row(bar(end_block={"type": "sun_elevation"}))]},
        {"rows": [{"id": "r", "target": {"entity_id": [""]}, "bars": []}]},
        {"rows": [{"id": "r", "target": {"unknown_id": ["x"]}, "bars": []}]},
    ],
)
def test_invalid_values_are_rejected(change: dict[str, Any]) -> None:
    with pytest.raises(vol.Invalid):
        flow(**change)


def test_parsed_flow() -> None:
    data = flow(
        row(
            bar(
                "sun",
                start_block={"type": "sunset", "time": "16:00", "offset": 30},
                end_block={"type": "sunrise", "offset": -15},
                at_start="adjust",
                at_end="restore",
            ),
            kind="label_id",
            target="windows",
        ),
        row(bar("x", look={"mode": "off"}), bar("y", "23:30", "23:45", look={"mode": "unchanged"})),
        days=[1],
        respect_manual=True,
        manual_hours=2,
    )
    parsed = Flow.from_dict(data)
    assert parsed.days == frozenset({1})
    assert parsed.respect_manual is True
    assert parsed.manual_hours == 2
    first = parsed.rows[0]
    assert first.target == {"label_id": ["windows"]}
    assert first.direct == frozenset()
    assert parsed.rows[1].direct == {"light.a"}
    sun = first.bars[0]
    assert (sun.start_type, sun.start_time, sun.start_offset) == ("sunset", time(16), 30)
    assert (sun.end_type, sun.end_time, sun.end_offset) == ("sunrise", None, -15)
    assert (sun.at_start, sun.at_end) == ("adjust", "restore")
    assert sun.action == Look("white", 2200, (255, 255, 255), 50)
    assert parsed.rows[1].bars[0].action == OFF
    assert parsed.rows[1].bars[1].action == UNCHANGED


def test_complete_flow_has_no_reason() -> None:
    assert flow_incomplete_reason(flow()) is None


@pytest.mark.parametrize(
    ("data", "reason"),
    [
        (flow(name="  "), "Give this flow a name."),
        (flow(days=[]), "Pick at least one day."),
        (flow(condition="person"), "Pick a person."),
        (flow(row()), "Add at least one time window."),
        (flow(row(bar()), row(bar("c"))), "Each target can only be in one row."),
        (flow(row(bar()), {"id": "r", "target": {}, "bars": []}), "Pick a target for every row."),
        (flow(row(bar(start="18:00", end="18:00"))), "Start and end can't be the same time."),
        (flow(row(bar(start_block={"type": "time"}))), "Pick a start time."),
        (flow(row(bar(start_block={"type": "sun_elevation"}))), "Enter a sun elevation."),
        (flow(row(bar(end_block={"type": "time"}))), "Pick an end time."),
    ],
)
def test_incomplete_flows(data: dict[str, Any], reason: str) -> None:
    assert flow_incomplete_reason(data) == reason


def test_same_light_may_be_in_a_label_row_and_its_own_row() -> None:
    data = flow(row(bar(), kind="label_id", target="windows"), row(bar("c")))
    assert flow_incomplete_reason(data) is None


@pytest.mark.parametrize(
    ("first", "second", "overlaps"),
    [
        (("16:00", "19:00"), ("18:00", "20:00"), True),
        (("16:00", "19:00"), ("19:00", "20:00"), False),
        (("22:00", "06:00"), ("05:00", "07:00"), True),
        (("22:00", "06:00"), ("06:00", "07:00"), False),
        (("22:00", "06:00"), ("23:00", "23:30"), True),
        (("22:00", "02:00"), ("01:00", "03:00"), True),
    ],
)
def test_overlapping_fixed_bars(
    first: tuple[str, str], second: tuple[str, str], overlaps: bool
) -> None:
    data = flow(row(bar("a", *first), bar("b", *second)))
    expected = "Time windows in one row can't overlap." if overlaps else None
    assert flow_incomplete_reason(data) == expected


def test_sun_bars_are_not_checked_for_overlap() -> None:
    sunny = bar("a", start_block={"type": "sunset"}, end="23:00")
    assert flow_incomplete_reason(flow(row(sunny, bar("b", "18:00", "20:00")))) is None


def test_target_accepts_single_ids_and_several_kinds() -> None:
    data = flow(
        {
            "id": "r",
            "target": {
                "entity_id": "light.a",
                "device_id": ["dev"],
                "area_id": ["kitchen"],
                "floor_id": ["ground"],
                "label_id": ["windows"],
                "exclude": {"entity_id": "light.led", "area_id": ["hall"]},
            },
            "bars": [bar()],
        }
    )
    target = data["rows"][0]["target"]
    assert target["entity_id"] == ["light.a"]
    assert target["exclude"] == {"entity_id": ["light.led"], "area_id": ["hall"]}
    assert flow_incomplete_reason(data) is None


def test_excluded_light_is_not_direct_and_scenes_are_found() -> None:
    parsed = Flow.from_dict(
        flow(
            {
                "id": "r",
                "target": {
                    "entity_id": ["light.a", "light.b", "scene.movie"],
                    "exclude": {"entity_id": ["light.b"]},
                },
                "bars": [bar()],
            }
        )
    )
    assert parsed.rows[0].direct == {"light.a", "scene.movie"}
    assert parsed.rows[0].scenes == ["scene.movie"]


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ({"type": "light", "id": "light.a"}, {"entity_id": ["light.a"]}),
        ({"type": "scene", "id": "scene.a"}, {"entity_id": ["scene.a"]}),
        ({"type": "area", "id": "kitchen"}, {"area_id": ["kitchen"]}),
        ({"type": "label", "id": "windows"}, {"label_id": ["windows"]}),
        ({"entity_id": ["light.a"]}, {"entity_id": ["light.a"]}),
    ],
)
def test_rows_stored_by_older_versions_are_upgraded(
    old: dict[str, Any], new: dict[str, Any]
) -> None:
    raw = {"id": "f", "name": "F", "days": [0], "rows": [{"id": "r", "target": old, "bars": []}]}
    assert FLOW_SCHEMA(upgrade_flow(raw))["rows"][0]["target"] == new
