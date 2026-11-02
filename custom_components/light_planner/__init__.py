"""Light Planner: run lights, labels, areas and scenes through named flows from a panel."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from . import websocket_api
from .const import DOMAIN, PANEL_COMPONENT, PANEL_PATH, STATIC_URL
from .engine import Engine
from .store import PlannerStore

_REGISTERED = f"{DOMAIN}_registered"


async def _async_register_panel(hass: HomeAssistant) -> None:
    integration = await async_get_integration(hass, DOMAIN)
    if _REGISTERED not in hass.data:
        # Static routes and commands can't be removed, so they survive a reload.
        hass.data[_REGISTERED] = True
        websocket_api.async_setup(hass)
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "frontend"), False)]
        )
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_PATH,
        webcomponent_name=PANEL_COMPONENT,
        sidebar_title="Light Planner",
        sidebar_icon="mdi:lightbulb-auto-outline",
        module_url=f"{STATIC_URL}/{PANEL_COMPONENT}.js?v={integration.version}",
        require_admin=True,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    store = PlannerStore(hass)
    await store.async_load()
    engine = Engine(hass, store)
    hass.data[DOMAIN] = engine
    await _async_register_panel(hass)
    engine.async_start()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    engine: Engine = hass.data.pop(DOMAIN)
    engine.async_stop()
    await engine.store.async_flush()
    frontend.async_remove_panel(hass, PANEL_PATH)
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Removing the integration also removes the flows."""
    await PlannerStore(hass).async_remove()
