"""Entité de base Baldrick / Baldrick base entity."""

from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
    format_mac,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BaldrickCoordinator


class BaldrickEntity(CoordinatorEntity[BaldrickCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: BaldrickCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        board_id = entry.unique_id
        data = coordinator.data
        firmware = next(iter(data.get("ota", {}).get("updatable", [])), {})

        self._attr_unique_id = f"{board_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, board_id)},
            connections={(CONNECTION_NETWORK_MAC, format_mac(board_id))},
            name=entry.title,
            manufacturer=data.get("board_manufacturer"),
            model=data.get("board_model"),
            sw_version=firmware.get("current_firmware_version"),
            configuration_url=f"http://{entry.data[CONF_HOST]}",
        )
