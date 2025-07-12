import logging

from homeassistant.components.conversation import ConversationEntity, ConversationInput, ConversationResult
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.intent import IntentResponse

from .agent import StackSpotAgent
from .const import DOMAIN, CONF_AGENT_NAME, AGENTS_KEY
from .util import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up the StackSpot conversation entity."""
    entry_id = entry.entry_id
    agent_name = entry.data.get(CONF_AGENT_NAME)

    stackspot_agent_instance: StackSpotAgent = hass.data[DOMAIN][AGENTS_KEY].get(entry_id)

    if stackspot_agent_instance:
        async_add_entities([
            StackSpotConversationEntity(hass, entry_id, agent_name, stackspot_agent_instance)
        ], True)
        _LOGGER.debug(f"StackSpot Conversation Entity added for entry {entry_id}.")
    else:
        _LOGGER.error(f"StackSpotAgent instance not found for entry {entry_id}. Cannot set up conversation entity.")


class StackSpotConversationEntity(ConversationEntity):
    """Representa uma entidade de conversação para StackSpot AI."""

    _attr_has_entity_name = True
    _attr_name = None  # O nome será o entity_id gerado automaticamente ou definido via config_entry

    def __init__(self, hass: HomeAssistant, config_entry_id: str, agent_name: str,
                 agent_instance: StackSpotAgent) -> None:
        """Inicializa a entidade de conversação."""
        self._hass = hass
        self._config_entry_id = config_entry_id
        self._agent_name = agent_name
        self._agent_instance = agent_instance
        self._attr_unique_id = f"stackspot_conversation_{config_entry_id}"
        self._attr_device_info = get_device_info(config_entry_id, agent_name)

    @property
    def supported_languages(self) -> list[str]:
        return self._agent_instance.supported_languages

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Processa a entrada do usuário e retorna a resposta."""
        _LOGGER.debug(f"Conversation entity received input for agent {self._agent_name}: '{user_input.text}'")

        # Delega o processamento ao seu StackSpotAgent
        response_text = await self._agent_instance.send_prompt_to_stackspot(user_input.text)

        # Empacota a resposta para o Home Assistant
        intent_response = IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response_text)
        return ConversationResult(response=intent_response, conversation_id=user_input.conversation_id)

    async def async_will_remove_from_hass(self) -> None:
        """Chamado quando a entidade está prestes a ser removida."""
        await self._agent_instance.async_close_session()
