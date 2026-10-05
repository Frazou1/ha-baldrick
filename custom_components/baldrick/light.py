"""Lumière Baldrick : couleur unie, effets CunningFX, presets de la carte et motifs de test.

Baldrick light: solid colour, CunningFX effects, board presets and test patterns.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    EFFECT_OFF,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BaldrickConfigEntry
from .api import BaldrickError
from .const import HA_JOB, PATTERN_CHOOSE, PRESET_PREFIX, TEST_EFFECT_PATTERNS, TEST_PREFIX
from .coordinator import BaldrickCoordinator
from .entity import BaldrickEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BaldrickConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([BaldrickLight(entry.runtime_data)])


class BaldrickLight(BaldrickEntity, LightEntity):
    _attr_name = None
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(self, coordinator: BaldrickCoordinator) -> None:
        super().__init__(coordinator, "light")

    @property
    def _state(self) -> dict[str, Any]:
        return self.coordinator.data

    @property
    def _test_patterns(self) -> list[str]:
        return [p for p in TEST_EFFECT_PATTERNS if p in self.coordinator.pixel_patterns]

    @property
    def effect_list(self) -> list[str]:
        # Effets animés (avec la couleur choisie), puis presets de la carte, puis motifs de test
        # Animated effects (using the picked colour), then board presets, then test patterns
        return (
            [EFFECT_OFF]
            + list(self.coordinator.fx_effects)
            + [PRESET_PREFIX + p for p in self.coordinator.presets]
            + [TEST_PREFIX + p for p in self._test_patterns]
        )

    @property
    def is_on(self) -> bool:
        return bool(self._state.get("test_mode_active") or self._state.get("fx_state"))

    @property
    def brightness(self) -> int:
        return self.coordinator.brightness

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        return self.coordinator.rgb

    @property
    def effect(self) -> str | None:
        state = self._state
        if state.get("fx_state"):
            active = state.get("fx_active", "")
            if active == HA_JOB:
                return self.coordinator.ha_effect
            return PRESET_PREFIX + active
        if state.get("test_mode_active") and state.get("test_pattern") != PATTERN_CHOOSE:
            return TEST_PREFIX + state.get("test_pattern", "")
        return EFFECT_OFF

    async def async_turn_on(self, **kwargs: Any) -> None:
        coordinator = self.coordinator
        if ATTR_RGB_COLOR in kwargs:
            coordinator.rgb = tuple(kwargs[ATTR_RGB_COLOR])
        if ATTR_BRIGHTNESS in kwargs:
            coordinator.brightness = kwargs[ATTR_BRIGHTNESS]

        effect = kwargs.get(ATTR_EFFECT)
        if effect is None and (ATTR_RGB_COLOR in kwargs or ATTR_BRIGHTNESS in kwargs):
            # Nouvelle couleur pendant un effet HA : on garde l'effet, sinon couleur unie
            # New colour during an HA effect: keep the effect, otherwise solid colour
            effect = coordinator.ha_effect or EFFECT_OFF
        elif effect is None:
            if self.is_on:
                return
            effect = EFFECT_OFF

        try:
            if effect == EFFECT_OFF:
                await coordinator.async_set_solid()
            elif effect in coordinator.fx_effects:
                await coordinator.async_run_effect(effect)
            elif effect.startswith(PRESET_PREFIX):
                await coordinator.async_run_preset(effect.removeprefix(PRESET_PREFIX))
            elif effect.startswith(TEST_PREFIX):
                await coordinator.async_set_solid(effect.removeprefix(TEST_PREFIX))
            else:
                raise HomeAssistantError(f"Baldrick: unknown effect '{effect}'")
        except BaldrickError as err:
            raise HomeAssistantError(f"Baldrick: {err}") from err

    async def async_turn_off(self, **kwargs: Any) -> None:
        try:
            await self.coordinator.async_turn_off()
        except BaldrickError as err:
            raise HomeAssistantError(f"Baldrick: {err}") from err
