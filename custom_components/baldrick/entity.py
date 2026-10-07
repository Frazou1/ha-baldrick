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


def network_mac(board_id: str, state: dict) -> str:
    """Adresse MAC réellement vue sur le réseau / MAC address actually seen on the network.

    board_id est l'adresse de base de l'ESP32. Selon la convention ESP-IDF, l'Ethernet
    utilise base + 3 et le Wi-Fi (station) la base elle-même.
    board_id is the ESP32 base MAC. Per ESP-IDF convention, Ethernet uses base + 3 and
    Wi-Fi (station) the base itself.
    """
    ethernet = state.get("network", {}).get("ethernet", {})
    offset = 3 if ethernet.get("connected") else 0
    return format_mac(f"{int(board_id, 16) + offset:012x}")


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
            connections={(CONNECTION_NETWORK_MAC, network_mac(board_id, data))},
            name=entry.title,
            manufacturer=data.get("board_manufacturer"),
            model=data.get("board_model"),
            sw_version=firmware.get("current_firmware_version"),
            configuration_url=f"http://{entry.data[CONF_HOST]}",
        )
