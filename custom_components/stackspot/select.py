import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import StackSpotEntityManager
from .const import (
    DOMAIN,
    SELECT_RESET_INTERVAL_ENTITY,
    TOKEN_RESET_INTERVAL_DAY,
    TOKEN_RESET_INTERVAL_MONTH,
    TOKEN_RESET_INTERVAL_NEVER, MANAGER, )
from .util import get_device_general

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Set up the select entities."""
    entry_id = entry.entry_id
    entities = []
    manager: StackSpotEntityManager = hass.data[DOMAIN][MANAGER]

    reset_interval_select = TokenResetIntervalSelect(entry_id)
    manager.add_entity(entry_id, SELECT_RESET_INTERVAL_ENTITY, reset_interval_select)
    entities.append(reset_interval_select)

    async_add_entities(entities, update_before_add=True)


class TokenResetIntervalSelect(SelectEntity, RestoreEntity):
    """Select entity for token reset interval."""

    _attr_has_entity_name = True
    _attr_name = "Tokens reset interval"
    _attr_icon = "mdi:calendar-sync"

    _attr_options = [
        TOKEN_RESET_INTERVAL_DAY,
        TOKEN_RESET_INTERVAL_MONTH,
        TOKEN_RESET_INTERVAL_NEVER,
    ]

    def __init__(self, config_id: str):
        self._attr_unique_id = f'stackspot_select_token_reset_interval_{config_id}'
        self._attr_device_info = get_device_general(config_id)

        # Inicializa o valor selecionado com base nas opções da integração
        self._attr_current_option = TOKEN_RESET_INTERVAL_NEVER
        _LOGGER.debug(f"Select entity initialized with option: {self._attr_current_option}")

    async def async_added_to_hass(self) -> None:
        """This method is called by the Home Assistant when the entity is added"""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state != STATE_UNKNOWN:
            try:
                self._attr_current_option = last_state.state
            except ValueError:
                _LOGGER.warning(
                    f"Could not convert persisted state '{last_state.state}'")
        else:
            _LOGGER.debug("Não foi possivel carrager o valor")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._attr_options:
            _LOGGER.warning(f"Invalid option '{option}' for Token Reset Interval Select.")
            return

        self._attr_current_option = option
        self.schedule_update_ha_state()
        _LOGGER.debug(f"Token Reset Interval set to: {option}")
