from __future__ import annotations

import logging
from datetime import datetime, UTC, timedelta
from typing import Literal, Optional

from homeassistant.auth.models import User
from homeassistant.components.conversation import (
    AbstractConversationAgent,
    ConversationResult,
    ConversationInput
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.entity import Entity

from . import StackSpotEntityManager
from .client.stackspot_client import StackSpotApiClient
from .const import (
    DOMAIN,
    MANAGER,
    SENSOR_USER_TOKEN,
    SENSOR_OUTPUT_TOKEN,
    SENSOR_ENRICHMENT_TOKEN,
    SENSOR_TOTAL_TOKEN,
    SECONDS_KEEP_CONVERSATION_HISTORY,
    SENSOR_TOTAL_GENERAL_TOKEN
)
from .data_utils import ContextValue, StackSpotAgentConfig, MessageRole
from .entities.token_sensor import TokenSensor
from .util import render_template

_LOGGER = logging.getLogger(__name__)


class StackSpotAgent(AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant, config: StackSpotAgentConfig) -> None:
        """Inicializa o agente com as configurações."""
        self.hass: HomeAssistant = hass
        self.manager: StackSpotEntityManager = hass.data[DOMAIN][MANAGER]
        self.config: StackSpotAgentConfig = config
        self._access_token: str | None = None
        self._expires_token: datetime | None = None
        self._history: dict[str, ContextValue] = {}
        self._api: StackSpotApiClient = StackSpotApiClient()

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return '*'

    async def async_close_session(self) -> None:
        """Fecha a sessão aiohttp."""
        if self._session and not self._session.closed:
            await self._session.close()
            _LOGGER.debug(f"aiohttp session closed for agent {self.config.agent_name}.")

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Processa a entrada do usuário e retorna a resposta."""

        # User
        user: User = await self.hass.auth.async_get_user(user_input.context.user_id)
        user_name = user.name

        # History
        await self._add_message(user_input.conversation_id, MessageRole.USER, user_input.text)
        payload = await self._get_history(user_input.conversation_id)

        # Prompt
        prompt = await self._get_prompt({'user': user_name})
        message = f'{prompt} \n {str(payload)}'

        text_response = await self._send_prompt_to_stackspot(message)
        await self._add_message(user_input.conversation_id, MessageRole.ASSISTANT, text_response)

        # Empacota a resposta para o Home Assistant
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(text_response)
        return ConversationResult(response=intent_response, conversation_id=user_input.conversation_id)

    async def process_task(self, prompt_task: str) -> str:
        # Prompt
        agent_prompt = await self._get_prompt({'user': 'unknown'})
        message = f'{agent_prompt} \n {prompt_task}'

        text_response = await self._send_prompt_to_stackspot(message)
        return text_response

    async def _get_access_token(self, force_new=False) -> str | None:
        """Obtém o token de acesso da Stackspot AI."""
        if not force_new and self._access_token and datetime.now() < self._expires_token:
            return self._access_token

        token_data = await self._api.generate_access_token(self.config.realm, self.config.client_id,
                                                           self.config.client_key)
        try:
            self._access_token = token_data.get("access_token")
            expires_in_seconds = token_data.get("expires_in")
            self._expires_token = datetime.now() + timedelta(seconds=expires_in_seconds)

            return self._access_token
        except Exception as e:
            _LOGGER.error(f"Erro ao obter token da Stackspot AI: {e}")
            return None

    async def _send_prompt_to_stackspot(self, prompt: str) -> str:
        """Envia o prompt para a Stackspot AI e retorna a resposta."""
        access_token = await self._get_access_token()
        if not access_token:
            return "Sorry, I couldn't authenticate myself with Stackspot there."

        response = await self._api.send_prompt(access_token, self.config.agent_id, prompt)
        if response.get('error', False):
            access_token = await self._get_access_token(force_new=True)
            response = await self._api.send_prompt(access_token, self.config.agent_id, prompt)

        if response.get('error', False):
            return 'Sorry, I had a problem when communicating with stackspot there.'

        await self._actions_with_response(response)
        return response.get("message", "No Stackspot Awards Ai.")

    async def _actions_with_response(self, response: dict) -> None:
        if "tokens" in response and isinstance(response["tokens"], dict):
            user_tokens = response["tokens"].get("user", 0)
            enrichment_tokens = response["tokens"].get("enrichment", 0)
            output_tokens = response["tokens"].get("output", 0)

            await self._update_token_sensors(user_tokens, enrichment_tokens, output_tokens)
        else:
            _LOGGER.debug("Resposta da StackSpot AI sem dados de tokens.")

    async def _update_token_sensors(self, user: int, enrichment: int, output: int):
        """Atualiza os sensores de tokens com os valores recebidos, somando-os."""
        total_tokens: int = user + enrichment + output
        _LOGGER.debug(f'Total tokens: {total_tokens} = user:{user} + enrichment:{enrichment} + output:{output}')
        try:
            total_general: TokenSensor = self._get_sensor_by(SENSOR_TOTAL_GENERAL_TOKEN, self.config.entry_id)
            total_sensor: TokenSensor = self._get_sensor_by(SENSOR_TOTAL_TOKEN)
            user_sensor: TokenSensor = self._get_sensor_by(SENSOR_USER_TOKEN)
            enrichment_sensor: TokenSensor = self._get_sensor_by(SENSOR_ENRICHMENT_TOKEN)
            output_sensor: TokenSensor = self._get_sensor_by(SENSOR_OUTPUT_TOKEN)

            total_general.update_native_value_adding(total_tokens)
            total_sensor.update_native_value_adding(total_tokens)
            user_sensor.update_native_value_adding(user)
            enrichment_sensor.update_native_value_adding(enrichment)
            output_sensor.update_native_value_adding(output)
        except Exception:
            _LOGGER.error('Erro ao processar tokens')

    def _get_sensor_by(self, key: str, config_id='sub-entry') -> Optional[TokenSensor]:
        if config_id == 'sub-entry':
            config_id = self.config.subentry_id

        entity: Entity = self.manager.get_entity_by(config_id, key)
        if not isinstance(entity, TokenSensor):
            _LOGGER.error(f'{key} not found valid entity!')
            return None
        return entity

    async def _get_history(self, conversation_id: str) -> dict:
        ctx: ContextValue = self._history[conversation_id]
        messages = ctx.get_history()
        return {'history': messages}

    async def _add_message(self, conversation_id: str, role: MessageRole, content: str):
        ctx: ContextValue = self._history.setdefault(conversation_id, ContextValue())
        ctx.add_message(role, content)
        ctx.trim(self.config.max_messages_history)
        _LOGGER.debug(
            f'[{self.config.agent_name}] HISTORY - context message: {len(ctx.messages)} of {self.config.max_messages_history}')
        _LOGGER.debug(f'[{self.config.agent_name}] HISTORY - all conversations: {self._history.keys()}')

        await self._cleanup()

    async def _cleanup(self):
        now = datetime.now(UTC)
        for cid, ctx in list(self._history.items()):
            if (now - ctx.last_interaction).total_seconds() > SECONDS_KEEP_CONVERSATION_HISTORY:
                del self._history[cid]
                _LOGGER.debug(f'Conversation {cid} deleted!')

    async def _get_prompt(self, variables: dict[str: any]) -> str:
        render = await render_template(self.hass, self.config.prompt, variables)
        return str(render)
