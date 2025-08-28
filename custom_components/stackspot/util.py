import logging
import re
import unicodedata
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


def get_device_info_ks(entry_id: str, slug: str, name: str) -> DeviceInfo:
    device_identifier = f'stackspot_ks_device_{entry_id}'
    return DeviceInfo(
        identifiers={(DOMAIN, device_identifier)},
        name=name,
        manufacturer=INTEGRATION_NAME,
        model="custom",
        serial_number=slug,
        configuration_url=f'https://ai.stackspot.com/knowledge-sources/{slug}?tabIndex=1',
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


def create_slug(text: str) -> str:
    """
    Cria um slug a partir de uma string.
    """
    # 1. Normaliza a string (decompondo caracteres acentuados)
    nfkd_form = unicodedata.normalize('NFKD', text)

    # 2. Remove todos os caracteres que são diacríticos (acentos, cedilhas, etc.)
    cleaned_text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    # 3. Converte para minúsculas
    text_lower = cleaned_text.lower()

    # 4. Remove caracteres indesejados e substitui espaços por hífens
    # [^a-z0-9\s-] remove tudo que não é letra, número, espaço ou hífen.
    slug = re.sub(r'[^a-z0-9\s-]', '', text_lower)

    # 5. Substitui múltiplos espaços e hífens por um único hífen e remove hífens das pontas
    slug = re.sub(r'[\s-]+', '-', slug).strip('-')

    return slug
