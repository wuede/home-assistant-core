"""Support for the Netatmo climate schedule selector."""

from __future__ import annotations

from collections.abc import Callable
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import slugify

from .const import NETATMO_CREATE_TEMPERATURE_SET_ENTRY
from .data_handler import HOME, SIGNAL_NAME, NetatmoHome
from .entity import NetatmoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Netatmo temperature set number platform."""

    @callback
    def _create_temperature_set_number(
        netatmo_home: NetatmoHome, data: dict, update_schedule_callback: Callable
    ) -> None:
        """Handle the creation of a temperature set number entity."""
        async_add_entities(
            [NetatmoTemperatureSetEntry(netatmo_home, data, update_schedule_callback)]
        )

    entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            NETATMO_CREATE_TEMPERATURE_SET_ENTRY,
            _create_temperature_set_number,
        )
    )


class NetatmoTemperatureSetEntry(NumberEntity, NetatmoBaseEntity):
    """Representation of a Netatmo temperature set as a number entity."""

    def __init__(
        self, netatmo_home: NetatmoHome, data: dict, update_schedule_callback: Callable
    ) -> None:
        """Initialize the temperature set number entity."""
        super().__init__(netatmo_home.data_handler)

        self._home = netatmo_home.home

        self._publishers.extend(
            [
                {
                    "name": HOME,
                    "home_id": self._home.entity_id,
                    SIGNAL_NAME: netatmo_home.signal_name,
                },
            ]
        )

        self._schedule_id = data["schedule_id"]
        self._temp_set_id = data["temp_set_id"]
        self._room_id = data["room_id"]
        self._update_schedule_callback = update_schedule_callback

        schedule = self._home.schedules[self._schedule_id]
        if schedule is None:
            raise PlatformNotReady(f"schedule with id {self._schedule_id} not found")

        temp_set_name, temperature = self._extract_zone_and_room_info()

        # we cannot extract the room name from the schedule/zones object
        room = self._home.rooms[self._room_id]
        room_name = None
        if room is not None:
            room_name = room.name

        self._attr_name = f"{schedule.name} {temp_set_name} {room_name} Temperature"
        self._attr_unique_id = f"{self._home.entity_id}-{self._schedule_id}-{self._temp_set_id}-{self._room_id}"

        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_native_value = temperature

        # Explicitly set the entity ID to avoid conflicts
        sanitized_temp_set_name = temp_set_name.lower().replace("+", "plus")
        sanitized_entity_id_part = slugify(
            f"{schedule.name}_{sanitized_temp_set_name}_{room_name}"
        )
        self.entity_id = f"number.{sanitized_entity_id_part}"

    @callback
    def async_update_callback(self) -> None:
        """Update the entity's state."""
        _, temperature = self._extract_zone_and_room_info()
        self._attr_native_value = temperature

    def _extract_zone_and_room_info(self) -> tuple[str, float]:
        """Extract temp set name and temperature."""
        schedule = self._home.schedules[self._schedule_id]
        temp_set_name = ""
        temperature = 0.0

        for zone in schedule.zones:
            if zone.entity_id == self._temp_set_id:
                temp_set_name = zone.name or temp_set_name
                for room in zone.rooms:
                    if room.entity_id == self._room_id:
                        temperature = room.therm_setpoint_temperature or temperature
                        break
                break

        return temp_set_name, temperature

    async def async_set_native_value(self, value: float) -> None:
        """Set a new target temperature."""
        _LOGGER.debug(
            "Setting temperature for room %s temperature set %s and schedule %s in home %s to %s°C",
            self._room_id,
            self._temp_set_id,
            self._schedule_id,
            self._home.entity_id,
            value,
        )

        # Update the temperature in the schedule
        self._update_schedule_callback(
            home_id=self._home.entity_id,
            schedule_id=self._schedule_id,
            temp_set_id=self._temp_set_id,
            room_id=self._room_id,
            new_temperature=value,
        )

        # Update the local state
        self._attr_native_value = value
        self.async_write_ha_state()
