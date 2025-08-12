import json
import logging
from json import JSONDecodeError

from homeassistant.components.ai_task import AITaskEntity, AITaskEntityFeature, GenDataTask, GenDataTaskResult
from homeassistant.components.conversation import ChatLog
from homeassistant.components.ollama.entity import OllamaBaseLLMEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import llm
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.json import json_loads
from voluptuous_openapi import convert

from custom_components.stackspot.agent import StackSpotAgent
from custom_components.stackspot.const import SUBENTRY_AI_TASK
from custom_components.stackspot.data_utils import StackSpotAgentConfig
from custom_components.stackspot.util import get_device_info_agent

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback, ) -> None:
    """Set up AI Task entities."""
    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_AI_TASK:
            continue

        agent_config = StackSpotAgentConfig.from_entry_for_task(entry, subentry)

        subentry_id = subentry.subentry_id
        agent_name = subentry.data.get('agent_name')
        stackspot_agent = StackSpotAgent(hass, agent_config)

        task = StackSportAiTaskEntity(subentry_id, agent_name, stackspot_agent)
        async_add_entities([task], config_subentry_id=subentry.subentry_id)


class StackSportAiTaskEntity(AITaskEntity, OllamaBaseLLMEntity):
    """AI Task entity."""

    _attr_has_entity_name = True
    _attr_name = 'StackSpot AI Task'

    _attr_supported_features = (
        AITaskEntityFeature.GENERATE_DATA
    )

    def __init__(self, config_id: str, agent_name: str, agent_instance: StackSpotAgent) -> None:
        """Inicializa a entidade de conversação."""
        self._agent_name = agent_name
        self._agent_instance = agent_instance
        self._attr_unique_id = f'stackspot_task_{config_id}'
        self._attr_device_info = get_device_info_agent(config_id, agent_name)

    async def _async_generate_data(self, task: GenDataTask, chat_log: ChatLog) -> GenDataTaskResult:
        """Handle a generate data task."""
        chat_prompt = json.dumps(
            [{"role": e.role, "content": e.content} for e in chat_log.content],
            ensure_ascii=False
        )
        prompt_task = f'Chat history:\n{chat_prompt}'

        if task.structure:
            output_format = convert(task.structure, custom_serializer=llm.selector_serializer)
            prompt_task = \
                f"""
            {prompt_task}\n
            The return must be a valid json in the following informed structure, do not return anything more outside of it:
            {output_format}
            """

        text = await self._agent_instance.process_task(prompt_task)

        if not task.structure:
            return GenDataTaskResult(conversation_id=chat_log.conversation_id, data=text)

        try:
            data = json_loads(text)
        except JSONDecodeError as err:
            _LOGGER.error(
                "Failed to parse JSON response: %s. Response: %s",
                err,
                text,
            )
            raise HomeAssistantError("Error with  structured response") from err

        return GenDataTaskResult(conversation_id=chat_log.conversation_id, data=data)
