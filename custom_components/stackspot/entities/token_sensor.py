from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.const import STATE_UNKNOWN

from ..util import get_device_info
import logging

_LOGGER = logging.getLogger(__name__)


class TokenSensor(SensorEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "tokens"

    def __init__(self, entry_id: str, agent_name: str):
        self._agent_name = agent_name
        self._attr_native_value = 0
        self._attr_device_info = get_device_info(entry_id, agent_name)

    @property
    def icon(self):
        return "mdi:numeric"

    async def async_added_to_hass(self) -> None:
        """This method is called by the Home Assistant when the entity is added"""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state != STATE_UNKNOWN:
            try:
                self._attr_native_value = int(last_state.state)
                _LOGGER.debug(f"Restored {self._agent_name} to {self._attr_native_value} from last state.")
            except ValueError:
                _LOGGER.warning(
                    f"Could not convert persisted state '{last_state.state}' for {self._agent_name} to a number. Starting from 0.")
        else:
            _LOGGER.debug(f"{self._agent_name} has no previous state or is unknown. Starting from 0.")

    def update_native_value_adding(self, value: int) -> None:
        if isinstance(value, int) or isinstance(value, float):
            self._attr_native_value = self.native_value + value
            self.schedule_update_ha_state()
        else:
            _LOGGER.warning(f"Attempted to update token sensor with non-numeric value: {value}")
