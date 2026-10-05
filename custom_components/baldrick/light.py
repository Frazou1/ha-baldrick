"""Lumière Baldrick pilotée par le mode test de la carte.

Baldrick light driven by the board's built-in test mode.
"""

from __future__ import annotations

import re
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BaldrickConfigEntry
from .api import BaldrickError
from .const import (
    DEFAULT_TEST_PORTS,
    DEFAULT_TEST_TARGET,
    HIDDEN_PATTERNS,
    PATTERN_CHOOSE,
    PATTERN_OFF,
)
from .coordinator import BaldrickCoordinator
from .entity import BaldrickEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BaldrickConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([BaldrickLight(entry.runtime_data)])


def _valid_ports(ports: str | None) -> str:
    """Garde la sélection de ports de la carte seulement si elle est valide.

    Keep the board's port selection only when it is valid ("all_pixel" or "1,3,").
    Après un redémarrage la carte peut renvoyer « | » (aucun port) : rien ne s'allumerait.
    After a reboot the board may report "|" (no port): nothing would light up.
    """
    if ports and re.fullmatch(r"all_\w+|(\d+,)+", ports):
        return ports
    return DEFAULT_TEST_PORTS


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


class BaldrickLight(BaldrickEntity, LightEntity):
    _attr_name = None
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(self, coordinator: BaldrickCoordinator) -> None:
        super().__init__(coordinator, "light")
        self._attr_effect_list = [
            p for p in coordinator.pixel_patterns if p not in HIDDEN_PATTERNS
        ]
        self._rgb = (255, 255, 255)
        self._update_rgb()

    def _update_rgb(self) -> None:
        # La carte renvoie #000000 quand un effet est actif : on garde la dernière couleur unie
        # The board reports #000000 while an effect runs: keep the last solid colour
        if self._state.get("test_pattern") == PATTERN_CHOOSE and (
            colour := self._state.get("test_fixed_colours")
        ):
            self._rgb = _hex_to_rgb(colour)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_rgb()
        super()._handle_coordinator_update()

    @property
    def _state(self) -> dict[str, Any]:
        return self.coordinator.data

    @property
    def is_on(self) -> bool:
        return bool(self._state.get("test_mode_active"))

    @property
    def brightness(self) -> int:
        # Carte : 0-100 %, HA : 0-255. Après un redémarrage la carte peut renvoyer 0 : on prend 100 %
        # Board: 0-100 %, HA: 0-255. After a reboot the board may report 0: use 100 %
        return round((self._state.get("test_brightness") or 100) * 255 / 100)

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        return self._rgb

    @property
    def effect(self) -> str | None:
        pattern = self._state.get("test_pattern")
        return pattern if pattern not in HIDDEN_PATTERNS else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        state = self._state
        current = state.get("test_pattern", PATTERN_OFF)
        if ATTR_EFFECT in kwargs:
            pattern = kwargs[ATTR_EFFECT]
        elif ATTR_RGB_COLOR in kwargs or current == PATTERN_OFF:
            pattern = PATTERN_CHOOSE
        else:
            pattern = current

        r, g, b = kwargs.get(ATTR_RGB_COLOR, self.rgb_color)
        brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)

        # La carte ignore les réglages si test_mode_active n'est pas à true : on envoie tout
        # The board ignores settings unless test_mode_active is true: send everything
        await self._send(
            {
                "test_mode_active": True,
                "test_pattern": pattern,
                "test_brightness": max(1, round(brightness * 100 / 255)),
                "test_colour_picked_r": r,
                "test_colour_picked_g": g,
                "test_colour_picked_b": b,
                "test_dmx_preset": state.get("test_dmx_preset", 0),
                "test_ports": _valid_ports(state.get("test_ports")),
                "test_target": state.get("test_target") or DEFAULT_TEST_TARGET,
            }
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._send({"test_mode_active": False})

    async def _send(self, settings: dict[str, Any]) -> None:
        try:
            await self.coordinator.api.async_set_test(settings)
        except BaldrickError as err:
            raise HomeAssistantError(f"Baldrick: {err}") from err
        await self.coordinator.async_request_refresh()
