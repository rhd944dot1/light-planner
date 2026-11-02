"""Persists flows and the light states to restore."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
import voluptuous as vol

from .const import DOMAIN
from .schedule import FLOW_SCHEMA, upgrade_flow

_LOGGER = logging.getLogger(__name__)


class PlannerStore:
    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, 1, f"{DOMAIN}.flows")
        self.flows: list[dict[str, Any]] = []
        # Flow id, bar id, entity id.
        self.snapshots: dict[str, dict[str, dict[str, Any]]] = {}
        # Entity id, moment of the last change that didn't come from Light Planner.
        self.manual: dict[str, str] = {}

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        self.snapshots = data.get("snapshots", {})
        self.manual = data.get("manual", {})
        self.flows = []
        for raw in data.get("flows", []):
            try:
                self.flows.append(FLOW_SCHEMA(upgrade_flow(raw)))
            except vol.Invalid as err:
                _LOGGER.warning("Skipping invalid flow %s: %s", raw.get("name"), err)

    def _data(self) -> dict[str, Any]:
        return {"flows": self.flows, "snapshots": self.snapshots, "manual": self.manual}

    def save(self) -> None:
        self._store.async_delay_save(self._data, 1)

    async def async_flush(self) -> None:
        """A reload creates a new store, which only sees what reached the disk."""
        await self._store.async_save(self._data())
