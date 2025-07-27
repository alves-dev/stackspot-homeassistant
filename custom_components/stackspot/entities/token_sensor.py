import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.restore_state import RestoreEntity

from ..util import get_device_info_agent

_LOGGER = logging.getLogger(__name__)


class TokenSensor(SensorEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "tokens"
    _attr_icon = "mdi:counter"

    def __init__(self, entry_id: str, agent_name: str):
        self._agent_name = agent_name
        self._attr_native_value = 0
        self._attr_device_info = get_device_info_agent(entry_id, agent_name)

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
            new_value = self.native_value + value
            _LOGGER.debug(f'{self._friendly_name_internal()}: old value={self.native_value} -> new value={new_value}')
            self._attr_native_value = new_value
            self.schedule_update_ha_state()
        else:
            _LOGGER.warning(f"Attempted to update token sensor with non-numeric value: {value}")
