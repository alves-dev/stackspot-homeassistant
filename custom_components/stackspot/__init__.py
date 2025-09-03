import logging
from datetime import timedelta, datetime

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    MANAGER,
    AGENTS_KEY,
    CONF_AGENT_NAME,
    CONF_AGENT_NAME_DEFAULT,
    CONF_KS_INTERVAL_UPDATE,
    CONF_KS_INTERVAL_UPDATE_DEFAULT,
    SUBENTRY_KS,
)
from .data_utils import StackSpotLogin, KSData
from .entities.stackspot_entity_manager import StackSpotEntityManager
from .knowledge_source import ks_create, ks_update
from .sensor import TokenTotalSensor
from .util import get_list_exposed_entities

_LOGGER = logging.getLogger(__name__)

# PLATFORMS = [Platform.CONVERSATION, Platform.SENSOR, Platform.SELECT]
PLATFORMS = [Platform.CONVERSATION, Platform.SENSOR, Platform.AI_TASK]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if MANAGER not in hass.data[DOMAIN]:
        hass.data[DOMAIN][MANAGER] = StackSpotEntityManager()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await process_exposed_entities(hass)

    for subentry in entry.subentries.values():
        if subentry.subentry_type == SUBENTRY_KS:
            await process_subentry_ks(hass, entry, subentry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok


async def process_exposed_entities(hass: HomeAssistant) -> None:
    manager: StackSpotEntityManager = hass.data[DOMAIN][MANAGER]
    key = 'exposed-entities-task'

    remove_listener = manager.get_object_by(key)
    if remove_listener is not None:
        remove_listener()

    await get_list_exposed_entities(hass)
    async def task(now: datetime) -> None:
        await get_list_exposed_entities(hass)

    remove_listener = async_track_time_interval(hass, task, timedelta(minutes=5))
    manager.add_objetc(key, remove_listener)


async def process_subentry_ks(hass: HomeAssistant, entry: ConfigEntry, subentry: ConfigSubentry) -> None:
    data_token = StackSpotLogin.from_entry(entry)
    ks_data = KSData.from_entry(subentry)
    subentry_id = subentry.subentry_id
    manager: StackSpotEntityManager = hass.data[DOMAIN][MANAGER]
    key_prefix = 'ks-task_'

    await ks_create(data_token, ks_data)

    remove_listener = manager.get_object_by(key_prefix + subentry_id)
    if remove_listener is not None:
        remove_listener()

    interval: dict = subentry.data.get(CONF_KS_INTERVAL_UPDATE, CONF_KS_INTERVAL_UPDATE_DEFAULT)

    async def task(now: datetime) -> None:
        await ks_update(hass, data_token, ks_data)

    remove_listener = async_track_time_interval(hass, task,
                                                timedelta(
                                                    days=interval.get('days', 0),
                                                    hours=interval.get('hours', 0),
                                                    minutes=interval.get('minutes', 0),
                                                    seconds=interval.get('seconds', 0)
                                                )
                                                )

    manager.add_objetc(key_prefix + subentry_id, remove_listener)
