import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import HANDLERS, ConfigFlow, ConfigEntry, ConfigSubentryFlow, \
    SubentryFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode, TemplateSelector
)

from .const import (
    DOMAIN,
    CONF_ACCOUNT,
    CONF_ACCOUNT_DEFAULT,
    CONF_REALM,
    CONF_REALM_DEFAULT,
    CONF_CLIENT_ID,
    CONF_CLIENT_KEY,
    CONF_AGENT_NAME,
    CONF_AGENT_NAME_DEFAULT,
    CONF_AGENT_ID,
    CONF_AGENT_MAX_MESSAGES_HISTORY,
    SUBENTRY_AGENT,
    CONF_AGENT_PROMPT,
    CONF_AGENT_PROMPT_DEFAULT
)

_LOGGER = logging.getLogger(__name__)


@HANDLERS.register(DOMAIN)
class StackspotConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Stackspot integration."""
    VERSION = 1

    @classmethod
    @callback
    def async_get_supported_subentry_types(
            cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {
            SUBENTRY_AGENT: AgentSubentryFlow
        }

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step for the user."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_ACCOUNT],
                data={
                    CONF_ACCOUNT: user_input[CONF_ACCOUNT],
                    CONF_REALM: user_input[CONF_REALM],
                    CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                    CONF_CLIENT_KEY: user_input[CONF_CLIENT_KEY],
                }
            )

        data_schema = vol.Schema({
            vol.Required(CONF_ACCOUNT, default=CONF_ACCOUNT_DEFAULT): str,
            vol.Required(CONF_REALM, default=CONF_REALM_DEFAULT): str,
            vol.Required(CONF_CLIENT_ID): str,
            vol.Required(CONF_CLIENT_KEY): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get the options flow for this handler."""
        return StackspotOptionsFlowHandler()


class StackspotOptionsFlowHandler(OptionsFlow):
    """Handles options flow for the Stackspot integration."""

    def __init__(self) -> None:
        """Initialize options flow."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                title=user_input[CONF_ACCOUNT],
                data={
                    CONF_ACCOUNT: user_input[CONF_ACCOUNT],
                    CONF_REALM: user_input[CONF_REALM],
                    CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                    CONF_CLIENT_KEY: user_input[CONF_CLIENT_KEY],
                },
            )

            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self.config_entry.entry_id)
            )

            return self.async_create_entry(title="", data={})

        current_data = self.config_entry.data

        data_schema = self.add_suggested_values_to_schema(
            vol.Schema({
                vol.Required(CONF_ACCOUNT): str,
                vol.Required(CONF_REALM): str,
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_KEY): str
            }),
            current_data
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            description_placeholders={
                "account_name": current_data.get(CONF_ACCOUNT, 'Account')
            }
        )


# async def async_configure_later(hass: HomeAssistant, entry_id: str) -> None:
#     await asyncio.sleep(1)
#     await hass.config_entries.async_reload(entry_id)


def _get_schema_subentry_agent() -> vol.Schema:
    max_message = vol.Required(CONF_AGENT_MAX_MESSAGES_HISTORY, default=10)
    prompt = vol.Optional(CONF_AGENT_PROMPT, default=CONF_AGENT_PROMPT_DEFAULT)

    return vol.Schema({
        vol.Required(CONF_AGENT_NAME, default=CONF_AGENT_NAME_DEFAULT): str,
        vol.Required(CONF_AGENT_ID): str,
        max_message: NumberSelector(
            NumberSelectorConfig(min=2, max=100, step=2, mode=NumberSelectorMode.SLIDER)
        ),
        prompt: TemplateSelector()
    })


class AgentSubentryFlow(ConfigSubentryFlow):
    """Flow para adicionar agentes individuais."""

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            _LOGGER.debug("Subentry data: %s", user_input)
            new_entry = self.async_create_entry(title=user_input[CONF_AGENT_ID], data=user_input)
            # self.hass.async_create_task(async_configure_later(self.hass, self._entry_id))
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self._entry_id)
            )
            return new_entry

        return self.async_show_form(
            step_id="user",
            data_schema=_get_schema_subentry_agent()
        )

    async def async_step_reconfigure(
            self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle reconfigure step for an existing agent."""

        if user_input is not None:
            _LOGGER.debug("Subentry data (reconfigure): %s", user_input)

            result = self.async_update_and_abort(
                self._get_entry(),
                self._get_reconfigure_subentry(),
                data=user_input,
                title=user_input[CONF_AGENT_ID]
            )

            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self._entry_id)
            )

            return result

        current_data = self._get_reconfigure_subentry().data

        data_schema = self.add_suggested_values_to_schema(
            _get_schema_subentry_agent(),
            current_data
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=data_schema,
            description_placeholders={
                "agent_name": current_data.get(CONF_AGENT_NAME, "Agent")
            }
        )
