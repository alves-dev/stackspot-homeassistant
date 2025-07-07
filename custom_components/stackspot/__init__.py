import logging

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .agent import StackSpotAgent
from .const import (
    CONF_REALM,
    CONF_CLIENT_ID,
    CONF_CLIENT_KEY,
    CONF_AGENT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura o agente a partir de uma entrada de configuração."""

    config_data = {
        CONF_REALM: entry.data.get(CONF_REALM),
        CONF_CLIENT_ID: entry.data.get(CONF_CLIENT_ID),
        CONF_CLIENT_KEY: entry.data.get(CONF_CLIENT_KEY),
        CONF_AGENT: entry.data.get(CONF_AGENT),
    }
    conversation.async_set_agent(hass, entry, StackSpotAgent(hass, config_data))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descarrega uma entrada de configuração."""
    return True