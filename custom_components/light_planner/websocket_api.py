"""WebSocket commands used by the panel."""

from __future__ import annotations

from datetime import time
from typing import Any

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar, label_registry as lr
import voluptuous as vol

from .const import DOMAIN
from .engine import Engine
from .schedule import FLOW_SCHEMA, Flow, flow_incomplete_reason


@callback
def async_setup(hass: HomeAssistant) -> None:
    for command in (
        ws_options,
        ws_list,
        ws_save,
        ws_delete,
        ws_preview,
        ws_apply_now,
        ws_clear_manual,
    ):
        websocket_api.async_register_command(hass, command)


def _engine(hass: HomeAssistant) -> Engine:
    return hass.data[DOMAIN]


def _by_name(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(items, key=lambda item: item["name"].casefold())


def _states(hass: HomeAssistant, domain: str) -> list[dict[str, str]]:
    return _by_name([{"id": s.entity_id, "name": s.name} for s in hass.states.async_all(domain)])


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/options"})
@websocket_api.require_admin
@callback
def ws_options(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    connection.send_result(
        msg["id"],
        {
            "light": _states(hass, "light"),
            "scene": _states(hass, "scene"),
            "person": _states(hass, "person"),
            "area": _by_name(
                [{"id": a.id, "name": a.name} for a in ar.async_get(hass).async_list_areas()]
            ),
            "label": _by_name(
                [
                    {"id": label.label_id, "name": label.name}
                    for label in lr.async_get(hass).async_list_labels()
                ]
            ),
        },
    )


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/list"})
@websocket_api.require_admin
@callback
def ws_list(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    connection.send_result(msg["id"], {"flows": _engine(hass).store.flows})


def _parse(connection: Any, msg_id: int, raw: dict[str, Any]) -> dict[str, Any] | None:
    """Normalized flow, or None after reporting why it can't be saved."""
    try:
        data = FLOW_SCHEMA(raw)
    except vol.Invalid as err:
        connection.send_error(msg_id, "invalid", str(err))
        return None
    if reason := flow_incomplete_reason(data):
        connection.send_error(msg_id, "invalid", reason)
        return None
    return data


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/save", vol.Required("flow"): dict}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    if (data := _parse(connection, msg["id"], msg["flow"])) is None:
        return
    await _engine(hass).async_save(data)
    connection.send_result(msg["id"], {"flow": data})


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/delete", vol.Required("flow_id"): str}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    await _engine(hass).async_delete(msg["flow_id"])
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/apply_now",
        vol.Required("flow"): dict,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_apply_now(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    if (data := _parse(connection, msg["id"], msg["flow"])) is None:
        return
    await _engine(hass).async_apply_now(Flow.from_dict(data))
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/clear_manual", vol.Required("entity_id"): str}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_clear_manual(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    await _engine(hass).async_clear_manual(msg["entity_id"])
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/preview",
        vol.Required("flows"): [dict],
        vol.Required("weekday"): vol.All(int, vol.Range(0, 6)),
        vol.Required("time"): str,
    }
)
@websocket_api.require_admin
@callback
def ws_preview(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    """Works on unsaved drafts; a draft that can't be parsed yet is just left out."""
    flows = []
    for raw in msg["flows"]:
        try:
            flows.append(Flow.from_dict(FLOW_SCHEMA(raw)))
        except vol.Invalid:
            continue
    try:
        clock = time.fromisoformat(msg["time"])
    except ValueError:
        connection.send_error(msg["id"], "invalid", "Pick a time.")
        return
    connection.send_result(msg["id"], _engine(hass).preview(flows, msg["weekday"], clock))
