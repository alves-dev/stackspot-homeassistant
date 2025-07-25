import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    MANAGER,
    AGENTS_KEY,
    CONF_AGENT_NAME,
    CONF_AGENT_NAME_DEFAULT
)
from .entities.stackspot_entity_manager import StackSpotEntityManager
from .sensor import TokenTotalSensor

_LOGGER = logging.getLogger(__name__)

# PLATFORMS = [Platform.CONVERSATION, Platform.SENSOR, Platform.SELECT]
PLATFORMS = [Platform.CONVERSATION, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if MANAGER not in hass.data[DOMAIN]:
        hass.data[DOMAIN][MANAGER] = StackSpotEntityManager()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok


# TODO: não faz sentido se não conseguir migrar do 1 para o 2
async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle migration of a config entry."""
    if entry.version == 1:
        new_data = {**entry.data, CONF_AGENT_NAME: CONF_AGENT_NAME_DEFAULT}
        return hass.config_entries.async_update_entry(entry, data=new_data)
    return entry
