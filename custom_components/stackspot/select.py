import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    SELECT_RESET_INTERVAL_ENTITY,
    TOKEN_RESET_INTERVAL_DAY,
    TOKEN_RESET_INTERVAL_MONTH,
    TOKEN_RESET_INTERVAL_NEVER,
)
from .util import get_device_general

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the select entities."""
    entities = []

    if SELECT_RESET_INTERVAL_ENTITY not in hass.data[DOMAIN]:
        reset_interval_select = TokenResetIntervalSelect()
        hass.data[DOMAIN][SELECT_RESET_INTERVAL_ENTITY] = reset_interval_select
        entities.append(reset_interval_select)

    async_add_entities(entities, update_before_add=True)
    _LOGGER.debug("Select entities added in hass.data")


class TokenResetIntervalSelect(SelectEntity):
    """Select entity for token reset interval."""

    _attr_has_entity_name = True
    _attr_name = "Intervalo de Reset de Tokens"  # Nome amigável que aparecerá na UI
    _attr_icon = "mdi:calendar-sync"  # Um ícone legal para a entidade

    _attr_options = [
        TOKEN_RESET_INTERVAL_DAY,
        TOKEN_RESET_INTERVAL_MONTH,
        TOKEN_RESET_INTERVAL_NEVER,
    ]

    def __init__(self):
        # Define o unique_id para a entidade
        self._attr_unique_id = 'stackspot_select_token_reset_interval'
        self._attr_device_info = get_device_general()

        # Inicializa o valor selecionado com base nas opções da integração
        self._attr_current_option = TOKEN_RESET_INTERVAL_NEVER
        _LOGGER.debug(f"Select entity initialized with option: {self._attr_current_option}")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._attr_options:
            _LOGGER.warning(f"Invalid option '{option}' for Token Reset Interval Select.")
            return

        self._attr_current_option = option
        self.schedule_update_ha_state()
        _LOGGER.debug(f"Token Reset Interval set to: {option}")
