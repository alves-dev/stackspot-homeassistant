import logging

from homeassistant.core import HomeAssistant

from . import StackSpotEntityManager, MANAGER
from .client.stackspot_client import StackSpotApiClient
from .const import TEMPLATE_KEY_EXPOSED_ENTITIES, DOMAIN, SENSOR_KS_LAST_UPDATE
from .data_utils import StackSpotLogin, KSData
from .sensor import KSDateTimeSensor
from .util import render_template

_LOGGER = logging.getLogger(__name__)


async def ks_create(data_token: StackSpotLogin, data: KSData) -> bool:
    api = StackSpotApiClient()
    access_token = await api.generate_access_token(data_token.realm, data_token.client_id, data_token.client_key)
    data = await api.create_knowledge_sources(access_token['access_token'], data.name, data.slug)

    return data is None or not data.get('error', False)


async def ks_update(hass: HomeAssistant, data_token: StackSpotLogin, data: KSData) -> None:
    api = StackSpotApiClient()
    token_response = await api.generate_access_token(data_token.realm, data_token.client_id, data_token.client_key)
    access_token = token_response['access_token']

    await api.clear_objects_knowledge_sources(access_token, data.slug)

    manager: StackSpotEntityManager = hass.data[DOMAIN][MANAGER]
    variables = {
        TEMPLATE_KEY_EXPOSED_ENTITIES: manager.get_object_by(TEMPLATE_KEY_EXPOSED_ENTITIES)
    }
    content: str = await render_template(hass, data.template, variables)

    response = await api.add_content_knowledge_sources(access_token, data.slug, str(content))

    if response is None or not response.get('error', False):
        _LOGGER.info(f'KS {data.slug} content has been updated')
        sensor: KSDateTimeSensor = manager.get_entity_by(data.subentry_id, SENSOR_KS_LAST_UPDATE)
        await sensor.async_set_datetime()
    else:
        _LOGGER.error(f'KS {data.slug} content has not been updated')
