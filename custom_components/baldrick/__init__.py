"""Intégration Home Assistant pour la carte Baldrick8 d'iLightThat.

Home Assistant integration for the iLightThat Baldrick8 board.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BaldrickApi
from .coordinator import BaldrickCoordinator

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SENSOR]

type BaldrickConfigEntry = ConfigEntry[BaldrickCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: BaldrickConfigEntry) -> bool:
    api = BaldrickApi(async_get_clientsession(hass), entry.data[CONF_HOST])
    coordinator = BaldrickCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BaldrickConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
