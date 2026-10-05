"""Vitesse des effets animés / Animated effect speed."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import BaldrickConfigEntry
from .api import BaldrickError
from .const import FX_SPEEDS
from .coordinator import BaldrickCoordinator
from .entity import BaldrickEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BaldrickConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([BaldrickEffectSpeed(entry.runtime_data)])


class BaldrickEffectSpeed(BaldrickEntity, SelectEntity, RestoreEntity):
    _attr_translation_key = "effect_speed"
    _attr_options = FX_SPEEDS
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: BaldrickCoordinator) -> None:
        super().__init__(coordinator, "effect_speed")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) and last.state in FX_SPEEDS:
            self.coordinator.fx_speed = last.state

    @property
    def current_option(self) -> str:
        return self.coordinator.fx_speed

    async def async_select_option(self, option: str) -> None:
        self.coordinator.fx_speed = option
        # Relance l'effet en cours pour appliquer la vitesse / Restart the running effect to apply the speed
        if effect := self.coordinator.ha_effect:
            try:
                await self.coordinator.async_run_effect(effect)
            except BaldrickError as err:
                raise HomeAssistantError(f"Baldrick: {err}") from err
        self.async_write_ha_state()
