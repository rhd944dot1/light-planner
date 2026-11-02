"""Makes custom_components discoverable in the HA test core."""

from datetime import datetime
from unittest.mock import patch

import pytest


class FakeSun:
    """Sunset 17:00, sunrise 07:00, 12 degrees reached at 16:00 local time."""

    below_at = (16, 0)

    def __init__(self, hass) -> None:
        from homeassistant.util import dt as dt_util

        self.tz = dt_util.get_default_time_zone()

    def event(self, kind, day):
        hour = 17 if kind == "sunset" else 7
        return datetime(day.year, day.month, day.day, hour, tzinfo=self.tz)

    def below(self, elevation, day):
        return datetime(day.year, day.month, day.day, *self.below_at, tzinfo=self.tz)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def fake_sun(request):
    if "real_sun" in request.keywords:
        yield
        return
    with patch("custom_components.light_planner.engine.HaSun", FakeSun):
        yield
