from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType

from .const import DOMAIN, INTEGRATION_NAME


def get_device_info(entry_id: str, name: str) -> DeviceInfo:
    device_identifier = f'{entry_id}_{name}'
    return DeviceInfo(
        identifiers={(DOMAIN, device_identifier)},
        name=name,
        manufacturer=INTEGRATION_NAME,
        entry_type=DeviceEntryType.SERVICE
    )


def get_device_general() -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, 'stackspot_global_device')},
        name='Stackspot AI - Config',
        manufacturer=INTEGRATION_NAME,
        entry_type=DeviceEntryType.SERVICE
    )
