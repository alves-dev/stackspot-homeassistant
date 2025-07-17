import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
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
from .entities.token_sensor import TokenSensor
from .util import get_device_general

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
        total_geral_sensor = TokenGeneralTotalSensor()
        hass.data[DOMAIN][SENSOR_TOTAL_GENERAL_TOKEN] = total_geral_sensor
        sensors.append(total_geral_sensor)

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.debug("Sensors tokens added in hass.data")


class TokenGeneralTotalSensor(SensorEntity, RestoreEntity):
    _attr_has_entity_name = True  # Use o name abaixo como nome da entidade
    _attr_name = "Tokens Totais Geral"  # Nome da entidade na UI
    _attr_unique_id = 'stackspot_global_total_general_tokens'
    _attr_native_unit_of_measurement = "tokens"
    _attr_icon = "mdi:counter"  # Ícone para o sensor global

    def __init__(self):
        self._attr_native_value = 0  # Valor inicial
        self._attr_device_info = get_device_general()


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
