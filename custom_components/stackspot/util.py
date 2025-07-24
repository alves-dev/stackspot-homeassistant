from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType

from .const import DOMAIN, INTEGRATION_NAME


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
