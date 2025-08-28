import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from . import StackSpotEntityManager
from .const import (
    DOMAIN,
    SENSOR_USER_TOKEN,
    SENSOR_ENRICHMENT_TOKEN,
    SENSOR_OUTPUT_TOKEN,
    SENSOR_TOTAL_TOKEN,
    SENSOR_TOTAL_GENERAL_TOKEN,
    SUBENTRY_AGENT,
    MANAGER,
    SUBENTRY_AI_TASK,
    SUBENTRY_KS,
    CONF_KS_SLUG, CONF_KS_NAME, SENSOR_KS_LAST_UPDATE,
)
from .entities.token_sensor import TokenSensor
from .util import get_device_general, get_device_info_ks

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    entry_id = entry.entry_id
    entities = []
    manager: StackSpotEntityManager = hass.data[DOMAIN][MANAGER]

    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_AGENT and subentry.subentry_type != SUBENTRY_AI_TASK:
            continue

        subentry_id = subentry.subentry_id
        agent_name = subentry.data.get('agent_name')

        total_sensor = TokenTotalSensor(subentry_id, agent_name)
        user_sensor = TokenUserSensor(subentry_id, agent_name)
        enrichment_sensor = TokenEnrichmentSensor(subentry_id, agent_name)
        output_sensor = TokenOutputSensor(subentry_id, agent_name)

        sensors = [total_sensor, user_sensor, enrichment_sensor, output_sensor]
        async_add_entities(sensors, True, config_subentry_id=subentry_id)

        manager.add_entity(subentry_id, SENSOR_TOTAL_TOKEN, total_sensor)
        manager.add_entity(subentry_id, SENSOR_USER_TOKEN, user_sensor)
        manager.add_entity(subentry_id, SENSOR_ENRICHMENT_TOKEN, enrichment_sensor)
        manager.add_entity(subentry_id, SENSOR_OUTPUT_TOKEN, output_sensor)

    total_geral_sensor = TokenGeneralTotalSensor(entry_id)
    manager.add_entity(entry_id, SENSOR_TOTAL_GENERAL_TOKEN, total_geral_sensor)
    entities.append(total_geral_sensor)

    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_KS:
            continue

        subentry_id = subentry.subentry_id
        sensor_datetime = KSDateTimeSensor(subentry_id, subentry.data.get(CONF_KS_SLUG),
                                           subentry.data.get(CONF_KS_NAME))
        async_add_entities([sensor_datetime], True, config_subentry_id=subentry_id)
        manager.add_entity(subentry_id, SENSOR_KS_LAST_UPDATE, sensor_datetime)

    async_add_entities(entities, update_before_add=True)
    _LOGGER.debug("Sensors tokens added in hass.data")


class TokenGeneralTotalSensor(TokenSensor):
    _attr_name = "Tokens Total General"

    def __init__(self, config_id: str):
        super().__init__(config_id, None)
        self._attr_device_info = get_device_general(config_id)
        self._attr_unique_id = f'stackspot_global_total_general_tokens_{config_id}'


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


class KSDateTimeSensor(SensorEntity, RestoreEntity):
    """Sensor somente leitura para armazenar uma data/hora."""

    _attr_has_entity_name = True
    _attr_name = "Last Update"
    _attr_icon = "mdi:clock"
    _attr_should_poll = False
    _attr_device_class = "timestamp"

    def __init__(self, entry_id: str, slug: str, name: str):
        self._attr_unique_id = f"{entry_id}_ks_last_update"
        self._attr_native_value: datetime | None = None
        self._attr_device_info = get_device_info_ks(entry_id, slug, name)

    async def async_set_datetime(self):
        """Atualiza a data/hora do sensor."""
        self._attr_native_value = dt_util.utcnow()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Restaura último valor após reinício do HA."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is None or last_state.state in ("unknown", "unavailable"):
            _LOGGER.warning("Não foi possível restaurar datetime anterior")
            return

        restored = dt_util.parse_datetime(last_state.state)
        if restored is None:
            _LOGGER.warning("Não foi possível converter a data")
            return

        self._attr_native_value = restored
