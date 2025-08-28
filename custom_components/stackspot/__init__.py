import logging
from datetime import timedelta, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    MANAGER,
    AGENTS_KEY,
    CONF_AGENT_NAME,
    CONF_AGENT_NAME_DEFAULT
)
from .entities.stackspot_entity_manager import StackSpotEntityManager
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

    async def task(now: datetime) -> None:
        await get_list_exposed_entities(hass)

    remove_listener = async_track_time_interval(hass, task, timedelta(minutes=5))
    manager.add_objetc(key, remove_listener)
