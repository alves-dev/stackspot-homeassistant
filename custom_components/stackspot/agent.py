from __future__ import annotations

import logging

import aiohttp
from homeassistant.components.conversation import (
    AbstractConversationAgent,
    ConversationResult,
    ConversationInput
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import (
    CONF_REALM,
    CONF_CLIENT_ID,
    CONF_CLIENT_KEY,
    CONF_AGENT
)

_LOGGER = logging.getLogger(__name__)


class StackSpotAgent(AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        """Inicializa o agente com as configurações."""
        self.hass = hass
        self._realm = config.get(CONF_REALM)
        self._client_id = config.get(CONF_CLIENT_ID)
        self._client_key = config.get(CONF_CLIENT_KEY)
        self._agent_id = config.get(CONF_AGENT)
        self._access_token = None  # Para armazenar o token de acesso da Stackspot
        self._session = aiohttp.ClientSession()  # Sessão HTTP para reutilizar conexões

    @property
    def supported_languages(self) -> list[str]:
        """Retorna os idiomas suportados por este agente."""
        return ["pt"]

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Processa a entrada do usuário e retorna a resposta."""

        # O texto bruto que o usuário falou/digitou
        comando = user_input.text.lower()
        _LOGGER.debug(f"Agente recebeu o comando: '{comando}'")

        resposta = await self._send_prompt_to_stackspot(user_input.text)

        # Empacota a resposta para o Home Assistant
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(resposta)
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
                    await self._send_prompt_to_stackspot(self, prompt, retaining=True)
                response.raise_for_status()
                response_data = await response.json()
                return response_data.get("message", "Nenhuma resposta da Stackspot AI.")
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erro ao enviar prompt para Stackspot AI: {e}")
            return "Desculpe, tive um problema ao me comunicar com a Stackspot AI."
