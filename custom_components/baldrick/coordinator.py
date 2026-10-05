"""Interrogation périodique de la carte / Periodic board polling."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BaldrickApi, BaldrickError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class BaldrickCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: BaldrickApi) -> None:
        super().__init__(
            hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=SCAN_INTERVAL
        )
        self.api = api
        self.pixel_patterns: list[str] = []

    async def _async_setup(self) -> None:
        try:
            self.pixel_patterns = await self.api.async_get_pixel_patterns()
        except BaldrickError as err:
            raise UpdateFailed(str(err)) from err

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.async_get_state()
        except BaldrickError as err:
            raise UpdateFailed(str(err)) from err
