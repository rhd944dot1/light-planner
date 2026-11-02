"""Flow logic without a running Home Assistant."""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from custom_components.light_planner.schedule import (
    FLOW_SCHEMA,
    OFF,
    UNCHANGED,
    Env,
    Flow,
    Look,
    Row,
    active_window,
    day_segments,
    decide,
    events_between,
    left_alone,
    manual_counts,
    next_moment,
    run_start,
    window,
)

TZ = ZoneInfo("Europe/Berlin")
MONDAY = date(2026, 11, 2)


class FakeSun:
    """Sunset 17:00, sunrise 07:00, 12 degrees reached 16:00, changeable per test."""

    sunset = (17, 0)
    below_at = (16, 0)

    def event(self, kind, day):
        hour, minute = self.sunset if kind == "sunset" else (7, 0)
        return datetime(day.year, day.month, day.day, hour, minute, tzinfo=TZ)

    def below(self, elevation, day):
        if self.below_at is None:
            return None
        return datetime(day.year, day.month, day.day, *self.below_at, tzinfo=TZ)


def env(**sun) -> Env:
    fake = FakeSun()
    for key, value in sun.items():
        setattr(fake, key, value)
    return Env(TZ, fake)


WARM = {"mode": "white", "kelvin": 2200, "brightness": 50}


def bar(id="b", start="time", at="18:00", end="23:00", **extra) -> dict:
    end_block = {"type": "time", "time": end} if isinstance(end, str) else end
    return {
        "id": id,
        "start": {
            "type": start,
            "time": at,
            "elevation": extra.pop("elevation", None),
            "offset": extra.pop("offset", 0),
        },
        "end": end_block,
        "look": extra.pop("look", WARM),
        **extra,
    }


def row(*bars: dict, kind="entity_id", target="light.x") -> dict:
    return {"id": f"{kind}-{target}", "target": {kind: [target]}, "bars": list(bars)}


def flow(id="a", *rows: dict, days=(0, 1, 2, 3, 4, 5, 6), enabled=True) -> Flow:
    data = {"id": id, "name": id, "days": list(days), "enabled": enabled, "rows": list(rows)}
    return Flow.from_dict(FLOW_SCHEMA(data))


def make(id="a", start="time", at="18:00", end="23:00", **extra) -> Flow:
    """A flow with one row and one bar."""
    days, enabled = extra.pop("days", range(7)), extra.pop("enabled", True)
    return flow(id, row(bar(id, start, at, end, **extra)), days=days, enabled=enabled)


def only(item: Flow):
    return item, item.rows[0].bars[0]


def at(hour: int, minute: int = 0, day: date = MONDAY) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=TZ)


def lights(*names):
    return lambda _: names


def members(mapping: dict):
    """Lights per row: the lights it names, plus what the mapping says for a label or area."""

    def resolve(item: Row):
        groups = (*item.target.get("label_id", []), *item.target.get("area_id", []))
        return [*item.direct, *(light for group in groups for light in mapping.get(group, []))]

    return resolve


def test_same_day_window() -> None:
    found = window(*only(make()), MONDAY, env())
    assert (found.start, found.end) == (at(18), at(23))


def test_overnight_window_runs_into_next_day() -> None:
    assert window(*only(make(end="06:00")), MONDAY, env()).end == at(6, day=MONDAY + timedelta(days=1))


def test_overnight_window_belongs_to_the_starting_weekday() -> None:
    schedule = make(end="06:00", days=[0])
    tuesday = MONDAY + timedelta(days=1)
    assert active_window(*only(schedule), at(3, day=tuesday), env()) is not None
    assert active_window(*only(schedule), at(20, day=tuesday), env()) is None


def test_weekday_filter() -> None:
    assert window(*only(make(days=[1])), MONDAY, env()) is None


def test_sunset_with_not_before_uses_the_later_moment() -> None:
    assert window(*only(make(start="sunset", at="18:30")), MONDAY, env()).start == at(18, 30)
    assert window(*only(make(start="sunset", at="16:00")), MONDAY, env()).start == at(17)
    assert window(*only(make(start="sunset", at=None)), MONDAY, env()).start == at(17)


def test_sun_elevation_uses_the_later_moment() -> None:
    schedule = make(start="sun_elevation", at="16:30", elevation=12, end="06:00")
    assert window(*only(schedule), MONDAY, env()).start == at(16, 30)
    assert window(*only(schedule), MONDAY, env(below_at=(21, 30))).start == at(21, 30)


def test_sun_elevation_never_reached_skips_the_day() -> None:
    assert window(*only(make(start="sun_elevation", elevation=12)), MONDAY, env(below_at=None)) is None


def test_sunset_past_afternoon_end_skips_the_day_instead_of_lasting_24h() -> None:
    assert window(*only(make(start="sunset", at=None, end="17:00")), MONDAY, env(sunset=(17, 30))) is None


def test_end_at_sunrise_is_next_morning() -> None:
    schedule = make(start="sunset", at=None, end={"type": "sunrise"})
    assert window(*only(schedule), MONDAY, env()).end == at(7, day=MONDAY + timedelta(days=1))


def test_end_at_sunset_same_day() -> None:
    schedule = make(start="time", at="10:00", end={"type": "sunset"})
    assert window(*only(schedule), MONDAY, env()).end == at(17)


def test_window_is_half_open() -> None:
    assert active_window(*only(make()), at(18), env()) is not None
    assert active_window(*only(make()), at(23), env()) is None


def test_last_started_wins_and_earlier_returns_after_it_ends() -> None:
    evening = make("evening", at="17:00", end="23:30")
    night = make("night", at="22:00", end="23:00")
    assert decide([evening, night], at(21), env(), lights("light.x"))["light.x"].flow == evening
    assert decide([evening, night], at(22), env(), lights("light.x"))["light.x"].flow == night
    assert decide([night, evening], at(22), env(), lights("light.x"))["light.x"].flow == night
    assert decide([evening, night], at(23), env(), lights("light.x"))["light.x"].flow == evening


def test_later_on_the_list_wins_a_tie() -> None:
    first, second = make("first"), make("second")
    assert decide([first, second], at(19), env(), lights("light.x"))["light.x"].flow == second


def test_overnight_flow_keeps_its_real_start_when_ranking() -> None:
    """At 03:00 the bar from 22:00 yesterday started after the one from 20:00."""
    early = make("early", at="20:00", end="06:00")
    late = make("late", at="22:00", end="06:00")
    tuesday = MONDAY + timedelta(days=1)
    assert decide([late, early], at(3, day=tuesday), env(), lights("light.x"))["light.x"].flow == late


def test_disabled_flow_is_ignored() -> None:
    assert decide([make(enabled=False)], at(19), env(), lights("light.x")) == {}


def test_counts_filters_flows() -> None:
    assert decide([make()], at(19), env(), lights("light.x"), lambda _: False) == {}


def test_own_row_beats_label_row_only_while_it_has_a_bar() -> None:
    red = {"mode": "color", "rgb": [255, 0, 0]}
    item = flow(
        "a",
        row(bar("night", at="22:00", end="23:00", look=red)),
        row(bar("evening", at="16:00", end="23:30"), kind="label_id", target="windows"),
    )
    resolve = members({"windows": ["light.x", "light.y"]})
    assert decide([item], at(20), env(), resolve)["light.x"].bar.id == "evening"
    night = decide([item], at(22), env(), resolve)
    assert night["light.x"].bar.id == "night"
    assert night["light.y"].bar.id == "evening"
    assert decide([item], at(23), env(), resolve)["light.x"].bar.id == "evening"


def test_own_row_wins_even_if_the_label_bar_started_later() -> None:
    item = flow(
        "a",
        row(bar("own", at="17:00")),
        row(bar("group", at="18:00"), kind="label_id", target="windows"),
    )
    result = decide([item], at(19), env(), members({"windows": ["light.x"]}))
    assert result["light.x"].bar.id == "own"


def test_later_started_of_two_group_rows_wins() -> None:
    item = flow(
        "a",
        row(bar("late", at="18:00"), kind="area_id", target="kitchen"),
        row(bar("early", at="17:00"), kind="label_id", target="windows"),
    )
    resolve = members({"windows": ["light.x"], "kitchen": ["light.x"]})
    assert decide([item], at(19), env(), resolve)["light.x"].bar.id == "late"


def test_lights_join_one_after_another() -> None:
    item = flow(
        "a",
        row(bar("x", at="16:00", end="23:00")),
        row(bar("y", at="17:30", end="23:00"), target="light.y"),
        row(bar("z", at="16:00", end="19:00"), target="light.z"),
    )
    resolve = members({})
    assert set(decide([item], at(17), env(), resolve)) == {"light.x", "light.z"}
    assert set(decide([item], at(18), env(), resolve)) == {"light.x", "light.y", "light.z"}
    assert set(decide([item], at(20), env(), resolve)) == {"light.x", "light.y"}


def test_two_bars_in_one_row_with_a_gap() -> None:
    item = flow("a", row(bar("one", at="16:00", end="17:00"), bar("two", at="18:00", end="19:00")))
    resolve = members({})
    assert decide([item], at(16), env(), resolve)["light.x"].bar.id == "one"
    assert decide([item], at(17), env(), resolve) == {}
    assert decide([item], at(18), env(), resolve)["light.x"].bar.id == "two"


def test_overlapping_sun_bars_later_start_wins() -> None:
    item = flow(
        "a",
        row(bar("sun", "sunset", None, "23:00"), bar("fixed", at="18:00", end="20:00")),
    )
    resolve = members({})
    assert decide([item], at(17, 30), env(), resolve)["light.x"].bar.id == "sun"
    assert decide([item], at(19), env(), resolve)["light.x"].bar.id == "fixed"


def test_off_bar_beats_earlier_flow() -> None:
    other = make("other", at="17:00")
    off = make("off", look={"mode": "off"})
    assert decide([other, off], at(19), env(), lights("light.x"))["light.x"].action == OFF


def test_unchanged_bar_leaves_the_light_to_other_flows() -> None:
    other = make("other", at="17:00")
    skip = make("skip", look={"mode": "unchanged"})
    assert decide([skip], at(19), env(), lights("light.x")) == {}
    assert decide([other, skip], at(19), env(), lights("light.x"))["light.x"].flow == other


def test_unchanged_own_row_also_overrules_its_label_row() -> None:
    item = flow(
        "a",
        row(bar("free", at="18:00", end="20:00", look={"mode": "unchanged"})),
        row(bar("group", at="17:00", end="23:00"), kind="label_id", target="windows"),
    )
    resolve = members({"windows": ["light.x"]})
    assert decide([item], at(19), env(), resolve) == {}
    assert left_alone(item, "light.x", at(19), env())
    assert decide([item], at(20), env(), resolve)["light.x"].bar.id == "group"
    assert not left_alone(item, "light.x", at(20), env())
    assert not left_alone(item, "light.other", at(19), env())


def test_last_started_bar_ranks_across_flows() -> None:
    first = flow(
        "first",
        row(bar("old", at="16:00", end="23:00"), kind="label_id", target="windows"),
        row(bar("new", at="21:00", end="23:00"), target="light.other"),
    )
    second = make("second", at="20:00")
    resolve = members({"windows": ["light.x"]})
    assert decide([second, first], at(22), env(), resolve)["light.x"].flow == second


def test_offset_shifts_sun_moments() -> None:
    late = make(start="sunset", at=None, offset=30, end="23:00")
    assert window(*only(late), MONDAY, env()).start == at(17, 30)
    early = make(start="sunset", at=None, offset=-30, end="23:00")
    assert window(*only(early), MONDAY, env()).start == at(16, 30)
    elevation = make(start="sun_elevation", at=None, elevation=12, offset=15, end="23:00")
    assert window(*only(elevation), MONDAY, env()).start == at(16, 15)


def test_not_before_applies_after_the_offset() -> None:
    item = make(start="sunset", at="17:15", offset=-30, end="23:00")
    assert window(*only(item), MONDAY, env()).start == at(17, 15)


def test_offset_shifts_a_sun_end() -> None:
    item = make(at="10:00", end={"type": "sunset", "offset": 45})
    assert window(*only(item), MONDAY, env()).end == at(17, 45)
    morning = make(start="sunset", at=None, end={"type": "sunrise", "offset": -30})
    assert window(*only(morning), MONDAY, env()).end == at(6, 30, day=MONDAY + timedelta(days=1))


def test_offset_is_ignored_for_fixed_times() -> None:
    item = make(at="18:00", offset=30, end={"type": "time", "time": "23:00", "offset": 10})
    found = window(*only(item), MONDAY, env())
    assert (found.start, found.end) == (at(18), at(23))


def test_events_of_several_bars_name_their_bar() -> None:
    item = flow("a", row(bar("one", at="16:00", end="17:00"), bar("two", at="17:00", end="18:00")))
    events = events_between([item], at(16, 30), at(17), env())
    assert [(e.kind, e.bar.id) for e in events] == [("end", "one"), ("start", "two")]


def test_unchanged_constant_on_a_parsed_bar() -> None:
    assert make(look={"mode": "unchanged"}).rows[0].bars[0].action == UNCHANGED


def test_look_service_data() -> None:
    assert Look("keep").service_data() == {}
    assert Look("keep", brightness=40).service_data() == {"brightness_pct": 40}
    assert Look("white", 2200, brightness=100).service_data() == {
        "color_temp_kelvin": 2200,
        "brightness_pct": 100,
    }


def test_events_are_ordered_with_ends_before_starts() -> None:
    first = make("first", at="17:00", end="18:00")
    second = make("second", at="18:00", end="19:00")
    events = events_between([second, first], at(17, 59), at(18), env())
    assert [(e.kind, e.flow.id) for e in events] == [("end", "first"), ("start", "second")]


def test_events_exclude_the_lower_bound_include_the_upper() -> None:
    assert events_between([make()], at(18), at(18, 1), env()) == []
    assert [e.kind for e in events_between([make()], at(17), at(18), env())] == ["start"]


def test_events_find_the_overnight_end() -> None:
    tuesday = MONDAY + timedelta(days=1)
    events = events_between([make(end="06:00")], at(5, day=tuesday), at(7, day=tuesday), env())
    assert [e.kind for e in events] == ["end"]


def test_next_moment() -> None:
    assert next_moment([make()], at(12), env()) == at(18)
    assert next_moment([make()], at(18), env()) == at(23)
    assert next_moment([make()], at(23), env()) == at(18, day=MONDAY + timedelta(days=1))
    assert next_moment([make(enabled=False)], at(12), env()) is None


def test_next_moment_skips_to_the_next_selected_day() -> None:
    assert next_moment([make(days=[4])], at(12), env()) == at(18, day=date(2026, 11, 6))


def test_day_segments_split_overnight() -> None:
    assert day_segments(*only(make(end="06:00")), MONDAY, env()) == [(0.0, 6.0), (18.0, 24.0)]
    assert day_segments(*only(make(at="08:30", end="12:00")), MONDAY, env()) == [(8.5, 12.0)]


def test_day_segments_respect_days() -> None:
    assert day_segments(*only(make(end="06:00", days=[0])), MONDAY, env()) == [(18.0, 24.0)]
    tuesday = MONDAY + timedelta(days=1)
    assert day_segments(*only(make(end="06:00", days=[0])), tuesday, env()) == [(0.0, 6.0)]


def test_dst_change_keeps_clock_times() -> None:
    sunday = date(2026, 10, 25)
    found = window(*only(make(at="22:00", end="06:00")), date(2026, 10, 24), env())
    assert found.end == at(6, day=sunday)
    assert found.end.astimezone(UTC) - found.start.astimezone(UTC) == timedelta(hours=9)


def flagged(*bars: dict, hours: int = 4) -> Flow:
    data = {
        "id": "a",
        "name": "a",
        "days": list(range(7)),
        "respect_manual": True,
        "manual_hours": hours,
        "rows": [row(*bars)],
    }
    return Flow.from_dict(FLOW_SCHEMA(data))


def test_run_start_joins_touching_bars_only() -> None:
    item = flagged(
        bar("one", at="16:00", end="18:00"),
        bar("two", at="18:00", end="19:00"),
        bar("three", at="20:00", end="21:00"),
    )
    assert run_start(item, at(18, 30), env()) == at(16)
    assert run_start(item, at(20, 30), env()) == at(20)
    assert run_start(item, at(19, 30), env()) is None


def test_run_start_reaches_back_over_midnight() -> None:
    item = flagged(bar("night", at="22:00", end="06:00"))
    assert run_start(item, at(3, day=MONDAY + timedelta(days=1)), env()) == at(22)


def test_manual_counts_while_recent_or_during_the_run() -> None:
    item = flagged(bar("long", at="10:00", end="23:00"), hours=2)
    assert manual_counts(item, at(9), at(10), env())
    assert not manual_counts(item, at(7), at(10), env())
    assert manual_counts(item, at(11), at(22), env())
    assert not manual_counts(item, at(9), at(22), env())


def test_manual_never_counts_without_the_flag() -> None:
    assert not manual_counts(make(), at(18), at(18, 1), env())
