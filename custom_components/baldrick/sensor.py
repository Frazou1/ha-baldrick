"""Capteur de température de la carte / Board temperature sensor."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BaldrickConfigEntry
from .coordinator import BaldrickCoordinator
from .entity import BaldrickEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BaldrickConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([BaldrickTemperatureSensor(entry.runtime_data)])


class BaldrickTemperatureSensor(BaldrickEntity, SensorEntity):
    _attr_translation_key = "temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator: BaldrickCoordinator) -> None:
        super().__init__(coordinator, "temperature")

    @property
    def native_value(self) -> float | None:
        temps = self.coordinator.data.get("temperature") or []
        return temps[0] if temps else None
