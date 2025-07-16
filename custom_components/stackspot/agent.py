from __future__ import annotations

import logging
from datetime import datetime, UTC

import aiohttp
from homeassistant.components.conversation import (
    AbstractConversationAgent,
    ConversationResult,
    ConversationInput
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import (
    CONF_REALM,
    CONF_CLIENT_ID,
    CONF_CLIENT_KEY,
    CONF_AGENT_ID,
    DOMAIN,
    SENSOR_TOKENS_KEY,
    SENSOR_USER_TOKEN,
    SENSOR_OUTPUT_TOKEN,
    SENSOR_ENRICHMENT_TOKEN,
    SENSOR_TOTAL_TOKEN,
    CONF_AGENT_NAME,
    SENSOR_TOTAL_GENERAL_TOKEN,
    CONF_MAX_MESSAGES_HISTORY,
    SECONDS_KEEP_CONVERSATION_HISTORY
)
from .data_utils import ContextValue
from .sensor import TokenSensor

_LOGGER = logging.getLogger(__name__)


class StackSpotAgent(AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Inicializa o agente com as configurações."""
        self.hass: HomeAssistant = hass
        self._entry = entry
        self._agent_name: str = entry.data.get(CONF_AGENT_NAME)
        self._agent_id: str = entry.data.get(CONF_AGENT_ID)
        self._realm: str = entry.data.get(CONF_REALM)
        self._client_id: str = entry.data.get(CONF_CLIENT_ID)
        self._client_key: str = entry.data.get(CONF_CLIENT_KEY)
        self._access_token: str = None  # Para armazenar o token de acesso da Stackspot
        self._session = aiohttp.ClientSession()
        self._entry_id: str = entry.entry_id
        self._history: dict[str, ContextValue] = {}

    @property
    def supported_languages(self) -> list[str]:
        return ['pt-br']

    async def async_close_session(self) -> None:
        """Fecha a sessão aiohttp."""
        if self._session and not self._session.closed:
            await self._session.close()
            _LOGGER.debug(f"aiohttp session closed for agent {self._agent_name}.")

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Processa a entrada do usuário e retorna a resposta."""

        # History
        await self._add_message(user_input.conversation_id, 'user', user_input.text)
        payload = await self._get_history(user_input.conversation_id)

        text_response = await self._send_prompt_to_stackspot(str(payload))
        await self._add_message(user_input.conversation_id, 'assistant', text_response)

        # Empacota a resposta para o Home Assistant
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(text_response)
        return ConversationResult(response=intent_response, conversation_id=user_input.conversation_id)

    async def _get_access_token(self) -> str | None:
        """Obtém o token de acesso da Stackspot AI."""
        # TODO: Validar se token ainda é valido
        if self._access_token:
            return self._access_token

        token_url = f"https://idm.stackspot.com/{self._realm}/oidc/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_key,
        }

        try:
            async with self._session.post(token_url, headers=headers, data=data) as response:
                response.raise_for_status()
                token_data = await response.json()
                self._access_token = token_data.get("access_token")
                _LOGGER.debug("Token da Stackspot AI obtido com sucesso.")
                return self._access_token
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erro ao obter token da Stackspot AI: {e}")
            return None

    async def _send_prompt_to_stackspot(self, prompt: str, retaining=False) -> str:
        """Envia o prompt para a Stackspot AI e retorna a resposta."""
        access_token = await self._get_access_token()
        if not access_token:
            return "Desculpe, não consegui me autenticar com a Stackspot AI."

        chat_url = f"https://genai-inference-app.stackspot.com/v1/agent/{self._agent_id}/chat"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "streaming": False,
            "user_prompt": prompt,
            "stackspot_knowledge": False,
            "return_ks_in_response": False,
        }

        try:
            async with self._session.post(chat_url, headers=headers, json=payload) as response:
                if response.status == 401 and retaining == False:
                    _LOGGER.info('Token expirado, removendo o atual.')
                    self._access_token = None
                    await self._send_prompt_to_stackspot(prompt, retaining=True)

                response.raise_for_status()
                response_data = await response.json()
                await self._actions_with_response(response_data)
                return response_data.get("message", "Nenhuma resposta da Stackspot AI.")
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erro ao enviar prompt para Stackspot AI: {e}")
            return "Desculpe, tive um problema ao me comunicar com a Stackspot AI."

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

        if DOMAIN not in self.hass.data:
            _LOGGER.warning("DOMAIN key not initialized in hass.data. Cannot update.")
            return

        total_general: TokenSensor = self.hass.data[DOMAIN].get(SENSOR_TOTAL_GENERAL_TOKEN, 0)
        total_general.update_native_value_adding(total_tokens)

        if (self._entry_id not in self.hass.data[DOMAIN]
                or SENSOR_TOKENS_KEY not in self.hass.data[DOMAIN][self._entry_id]):
            _LOGGER.warning("Token sensors not initialized in hass.data. Cannot update.")
            return

        total_sensor: TokenSensor = self.hass.data[DOMAIN][self._entry_id][SENSOR_TOKENS_KEY].get(
            SENSOR_TOTAL_TOKEN)
        total_sensor.update_native_value_adding(total_tokens)

        user_sensor: TokenSensor = self.hass.data[DOMAIN][self._entry_id][SENSOR_TOKENS_KEY].get(SENSOR_USER_TOKEN)
        user_sensor.update_native_value_adding(user)

        enrichment_sensor: TokenSensor = self.hass.data[DOMAIN][self._entry_id][SENSOR_TOKENS_KEY].get(
            SENSOR_ENRICHMENT_TOKEN)
        enrichment_sensor.update_native_value_adding(enrichment)

        output_sensor: TokenSensor = self.hass.data[DOMAIN][self._entry_id][SENSOR_TOKENS_KEY].get(
            SENSOR_OUTPUT_TOKEN)
        output_sensor.update_native_value_adding(output)

    async def _get_history(self, conversation_id: str) -> dict:
        ctx: ContextValue = self._history[conversation_id]
        messages = ctx.get_history()
        return {'history': messages}

    async def _add_message(self, conversation_id: str, role: str, content: str):
        ctx: ContextValue = self._history.setdefault(conversation_id, ContextValue())
        ctx.add_message(role, content)
        ctx.trim(self._entry.options.get(CONF_MAX_MESSAGES_HISTORY))
        _LOGGER.debug(
            f'HISTORY - len: {len(ctx.messages)} | all conversations: {self._history.keys()}')

        await self._cleanup()

    async def _cleanup(self):
        now = datetime.now(UTC)
        for cid, ctx in list(self._history.items()):
            if (now - ctx.last_interaction).total_seconds() > SECONDS_KEEP_CONVERSATION_HISTORY:
                del self._history[cid]
                _LOGGER.debug(f'Conversation {cid} deleted!')
