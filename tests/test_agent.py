from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientSession
from homeassistant.components.conversation import ConversationInput, ConversationResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers.intent import IntentResponse

from custom_components.stackspot.agent import StackSpotAgent


@pytest.mark.asyncio
async def test_process_retorna_resposta_valida(hass: HomeAssistant):
    agent_response : str = 'Resposta da Stackspot'

    config = {
        "realm": "meu-realm",
        "client_id": "meu-client-id",
        "client_key": "meu-client-key",
        "agent": "agent-id"
    }

    agent = StackSpotAgent(hass, config)

    # Mock do token
    agent._get_access_token = AsyncMock(return_value="fake-token")

    # Cria um mock de resposta que funciona com `async with`
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"message": agent_response})

    # Mock da session com post que suporta `async with`
    mock_session = MagicMock(spec=ClientSession)
    mock_session.post.return_value.__aenter__.return_value = mock_response
    mock_session.post.return_value.__aexit__.return_value = AsyncMock()

    agent._session = mock_session

    user_input = ConversationInput(
        text="Oi agente",
        language="pt",
        conversation_id="123",
        context=MagicMock(),
        device_id="device-test",
        agent_id="stackspot"
    )

    result : ConversationResult = await agent.async_process(user_input)

    assert isinstance(result.response, IntentResponse)
    assert result.response.speech["plain"]["speech"] == agent_response
