import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)


class StackSpotApiClient:
    def __init__(self) -> None:
        self._session = aiohttp.ClientSession()

    async def generate_access_token(self, realm: str, client_id: str, client_key: str) -> dict:
        """Obtém o token de acesso da Stackspot AI."""

        token_url = f"https://idm.stackspot.com/{realm}/oidc/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_key,
        }

        try:
            async with self._session.post(token_url, headers=headers, data=data) as response:
                response.raise_for_status()
                _LOGGER.debug("Token da Stackspot AI obtido com sucesso.")
                token_data = await response.json()
                return token_data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erro ao obter token da Stackspot AI: {e}")
            return {}

    async def send_prompt(self, access_token: str, agent_id: str, prompt: str) -> dict:
        """Envia o prompt para a Stackspot AI e retorna a resposta."""

        chat_url = f"https://genai-inference-app.stackspot.com/v1/agent/{agent_id}/chat"
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
                if response.status == 401:
                    _LOGGER.info('Token expirado')
                    return {
                        'error': True,
                        'status': 401
                    }

                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erro ao enviar prompt para Stackspot AI: {e}")
            return {
                'error': True
            }

    async def create_knowledge_sources(self, access_token: str, name: str, slug: str) -> dict:
        """Cria um knowledge-sources KS"""

        url = 'https://data-integration-api.stackspot.com/v1/knowledge-sources'
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "slug": slug,
            "name": name,
            "description": f'Description {name}',
            "type": "custom",
        }

        try:
            async with self._session.post(url, headers=headers, json=payload) as response:
                if response.status == 422:
                    _LOGGER.debug("KS already created!")
                    return {
                        'slug': slug
                    }

                response.raise_for_status()
                _LOGGER.debug("KS created!")
                response_data = await response.json()
                return response_data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erro ao criar KS no Stackspot AI: {e}")
            return {
                'error': True
            }

    async def add_content_knowledge_sources(self, access_token: str, slug: str, content: str) -> dict:
        """Cria um knowledge-sources KS"""

        url = f'https://genai-code-buddy-api.stackspot.com/v1/knowledge-sources/{slug}/custom'
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "content": content,
        }

        try:
            async with self._session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                _LOGGER.debug("KS content added!")
                response_data = await response.json()
                return response_data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erro ao adicionar content no KS no Stackspot AI: {e}")
            return {
                'error': True
            }

    async def clear_objects_knowledge_sources(self, access_token: str, slug: str):
        url = f'https://data-integration-api.stackspot.com/v1/knowledge-sources/{slug}/objects'
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with self._session.delete(url, headers=headers) as response:
                response.raise_for_status()
                _LOGGER.debug("KS objects delete!")
                response_data = await response.json()
                return response_data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erro ao tentar limpar os objetos no KS no Stackspot AI: {e}")
            return {
                'error': True
            }
