import logging
from typing import Literal

from homeassistant.components.conversation import ConversationEntity, ConversationInput, ConversationResult
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .agent import StackSpotAgent
from .const import CONF_AGENT_NAME, SUBENTRY_AGENT
from .data_utils import StackSpotAgentConfig
from .util import get_device_info_agent

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Set up the StackSpot conversation entity."""
    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_AGENT:
            continue

        agent_config = StackSpotAgentConfig.from_entry(entry, subentry)

        subentry_id = subentry.subentry_id
        agent_name = subentry.data.get(CONF_AGENT_NAME)
        stackspot_agent = StackSpotAgent(hass, agent_config)
        conversation = StackSpotConversationEntity(subentry_id, agent_name, stackspot_agent)
        async_add_entities([conversation], True, config_subentry_id=subentry_id)


class StackSpotConversationEntity(ConversationEntity):
    """Representa uma entidade de conversação para StackSpot AI."""

    _attr_has_entity_name = True
    _attr_name = 'Conversation'

    def __init__(self, config_id: str, agent_name: str, agent_instance: StackSpotAgent) -> None:
        """Inicializa a entidade de conversação."""
        self._agent_name = agent_name
        self._agent_instance = agent_instance
        self._attr_unique_id = f'stackspot_conversation_{config_id}'
        self._attr_device_info = get_device_info_agent(config_id, agent_name)

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return self._agent_instance.supported_languages

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Processa a entrada do usuário e retorna a resposta."""
        _LOGGER.debug(f"CONVERSATION: agent '{self._agent_name}' -> '{user_input.text}'")

        return await self._agent_instance.async_process(user_input)

    async def async_will_remove_from_hass(self) -> None:
        """Chamado quando a entidade está prestes a ser removida."""
        await self._agent_instance.async_close_session()
