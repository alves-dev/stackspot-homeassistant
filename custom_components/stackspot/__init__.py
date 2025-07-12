import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .agent import StackSpotAgent
from .const import (
    CONF_REALM,
    CONF_CLIENT_ID,
    CONF_CLIENT_KEY,
    CONF_AGENT,
    DOMAIN,
    SENSOR_TOKENS_KEY,
    AGENTS_KEY
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ['conversation', 'sensor']


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        hass.data[DOMAIN][AGENTS_KEY] = {}

    entry_id = entry.entry_id

    config_data = {
        CONF_REALM: entry.data.get(CONF_REALM),
        CONF_CLIENT_ID: entry.data.get(CONF_CLIENT_ID),
        CONF_CLIENT_KEY: entry.data.get(CONF_CLIENT_KEY),
        CONF_AGENT: entry.data.get(CONF_AGENT),
        'entry_id': entry_id
    }

    stackspot_agent_instance = StackSpotAgent(hass, config_data)
    hass.data[DOMAIN][AGENTS_KEY][entry_id] = stackspot_agent_instance

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        if entry.entry_id in hass.data[DOMAIN][AGENTS_KEY]:
            await hass.data[DOMAIN][AGENTS_KEY][entry.entry_id].async_close_session()
            del hass.data[DOMAIN][AGENTS_KEY][entry.entry_id]
        if not hass.data[DOMAIN][AGENTS_KEY]:
            del hass.data[DOMAIN]

    return unload_ok
