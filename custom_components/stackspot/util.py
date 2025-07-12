from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, INTEGRATION_NAME


def get_device_info(entry_id: str, agent_name: str) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name=agent_name,
        manufacturer=INTEGRATION_NAME,
    )
