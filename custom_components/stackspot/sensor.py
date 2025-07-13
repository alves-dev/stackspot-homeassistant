import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    SENSOR_TOKENS_KEY,
    SENSOR_USER_TOKEN,
    SENSOR_ENRICHMENT_TOKEN,
    SENSOR_OUTPUT_TOKEN,
    SENSOR_TOTAL_TOKEN,
    CONF_AGENT_NAME,
    SENSOR_TOTAL_GENERAL_TOKEN
)
from .util import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    entry_id = entry.entry_id
    agent_name = entry.data.get(CONF_AGENT_NAME)

    total_sensor = TokenTotalSensor(entry_id, agent_name)
    user_sensor = TokenUserSensor(entry_id, agent_name)
    enrichment_sensor = TokenEnrichmentSensor(entry_id, agent_name)
    output_sensor = TokenOutputSensor(entry_id, agent_name)

    sensors = [
        total_sensor,
        user_sensor,
        enrichment_sensor,
        output_sensor
    ]

    hass.data[DOMAIN][entry_id] = {}
    hass.data[DOMAIN][entry_id][SENSOR_TOKENS_KEY] = {}

    hass.data[DOMAIN][entry_id][SENSOR_TOKENS_KEY][SENSOR_TOTAL_TOKEN] = total_sensor
    hass.data[DOMAIN][entry_id][SENSOR_TOKENS_KEY][SENSOR_USER_TOKEN] = user_sensor
    hass.data[DOMAIN][entry_id][SENSOR_TOKENS_KEY][SENSOR_ENRICHMENT_TOKEN] = enrichment_sensor
    hass.data[DOMAIN][entry_id][SENSOR_TOKENS_KEY][SENSOR_OUTPUT_TOKEN] = output_sensor

    if SENSOR_TOTAL_GENERAL_TOKEN not in hass.data[DOMAIN]:
        total_geral_sensor = TokenTotalSensor(SENSOR_TOTAL_GENERAL_TOKEN, 'All agents')
        hass.data[DOMAIN][SENSOR_TOTAL_GENERAL_TOKEN] = total_geral_sensor
        sensors.append(total_geral_sensor)

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.debug("Sensors tokens added in hass.data")


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


class TokenTotalSensor(TokenSensor):
    _attr_name = "Total Tokens Count"

    def __init__(self, entry_id: str, agent_name: str):
        super().__init__(entry_id, agent_name)
        self._attr_unique_id = f"stackspot_token_total_count_{entry_id}"


class TokenUserSensor(TokenSensor):
    _attr_name = "User Tokens Count"

    def __init__(self, entry_id: str, agent_name: str):
        super().__init__(entry_id, agent_name)
        self._attr_unique_id = f"stackspot_token_user_count_{entry_id}"


class TokenEnrichmentSensor(TokenSensor):
    _attr_name = "Enrichment Tokens Count"

    def __init__(self, entry_id: str, agent_name: str):
        super().__init__(entry_id, agent_name)
        self._attr_unique_id = f"stackspot_token_enrichment_count_{entry_id}"


class TokenOutputSensor(TokenSensor):
    _attr_name = "Output Tokens Count"

    def __init__(self, entry_id: str, agent_name: str):
        super().__init__(entry_id, agent_name)
        self._attr_unique_id = f"stackspot_token_output_count_{entry_id}"
