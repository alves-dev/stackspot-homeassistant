import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.helpers.template import Template

from . import StackSpotEntityManager
from .const import DOMAIN, INTEGRATION_NAME, MANAGER, TEMPLATE_KEY_EXPOSED_ENTITIES

_LOGGER = logging.getLogger(__name__)


def get_device_info_agent(entry_id: str, name: str) -> DeviceInfo:
    device_identifier = f'stackspot_agent_device_{entry_id}'
    return DeviceInfo(
        identifiers={(DOMAIN, device_identifier)},
        name=name,
        manufacturer=INTEGRATION_NAME,
        entry_type=DeviceEntryType.SERVICE
    )


def get_device_general(entry_id: str) -> DeviceInfo:
    device_identifier = f'stackspot_general_device_{entry_id}'
    return DeviceInfo(
        identifiers={(DOMAIN, device_identifier)},
        name='Config',
        manufacturer=INTEGRATION_NAME,
        entry_type=DeviceEntryType.SERVICE
    )


async def render_template(hass: HomeAssistant, template_str: str, variables: dict = None) -> Any:
    tpl = Template(template_str, hass)
    return tpl.async_render(variables or {})


async def get_list_exposed_entities(hass: HomeAssistant) -> list[dict]:
    registry = entity_registry.async_get(hass)

    exposed_entities = []
    for entity_id, entry in registry.entities.items():
        if entry.options.get('conversation', {}).get('should_expose', False):
            exposed_entities.append(entry)

    list_dict = []
    for entity in exposed_entities:
        list_dict.append({
            'entity_id': entity.entity_id,
            'name': entity.as_partial_dict.get('original_name', ''),
            'aliases': list(entity.aliases)
        })

    manager: StackSpotEntityManager = hass.data[DOMAIN][MANAGER]
    manager.add_objetc(TEMPLATE_KEY_EXPOSED_ENTITIES, list_dict)
    _LOGGER.info('Expose entities in manager updated!')

    return list_dict
