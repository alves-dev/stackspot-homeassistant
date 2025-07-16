import voluptuous as vol
from homeassistant.config_entries import HANDLERS, ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    BooleanSelector
)

from .const import (
    DOMAIN,
    CONF_REALM,
    CONF_CLIENT_ID,
    CONF_CLIENT_KEY,
    CONF_AGENT_ID,
    CONF_REALM_DEFAULT,
    CONF_AGENT_NAME,
    CONF_AGENT_NAME_DEFAULT,
    CONF_HA_ENTITIES_ACCESS,
    CONF_TOKEN_RESET_INTERVAL,
    TOKEN_RESET_INTERVAL_MONTH,
    TOKEN_RESET_INTERVAL_NEVER,
    CONF_MAX_MESSAGES_HISTORY
)


@HANDLERS.register(DOMAIN)
class StackspotConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Stackspot integration."""
    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step for the user."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_AGENT_NAME],
                data={
                    CONF_AGENT_NAME: user_input[CONF_AGENT_NAME],
                    CONF_AGENT_ID: user_input[CONF_AGENT_ID],
                    CONF_REALM: user_input[CONF_REALM],
                    CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                    CONF_CLIENT_KEY: user_input[CONF_CLIENT_KEY],
                },
                options={
                    CONF_MAX_MESSAGES_HISTORY: 10,
                    CONF_HA_ENTITIES_ACCESS: False,
                    CONF_TOKEN_RESET_INTERVAL: TOKEN_RESET_INTERVAL_MONTH,
                }
            )

        data_schema = vol.Schema({
            vol.Required(CONF_AGENT_NAME, default=CONF_AGENT_NAME_DEFAULT): str,
            vol.Required(CONF_AGENT_ID): str,
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
            return self.async_create_entry(title="", data=user_input)

        max_message = vol.Required(CONF_MAX_MESSAGES_HISTORY,
                                   default=self.config_entry.options.get(CONF_MAX_MESSAGES_HISTORY, 10))

        ha_entities = vol.Required(CONF_HA_ENTITIES_ACCESS,
                                   default=self.config_entry.options.get(CONF_HA_ENTITIES_ACCESS, True))

        tokens_reset = vol.Required(CONF_TOKEN_RESET_INTERVAL,
                                    default=self.config_entry.options.get(CONF_TOKEN_RESET_INTERVAL,
                                                                          TOKEN_RESET_INTERVAL_NEVER))

        options_schema = vol.Schema({
            max_message: NumberSelector(
                NumberSelectorConfig(min=2, max=100, step=2, mode=NumberSelectorMode.SLIDER)
            ),
            ha_entities: BooleanSelector(),
            # tokens_reset: SelectSelector(
            #     SelectSelectorConfig(
            #         options=[
            #             TOKEN_RESET_INTERVAL_DAY,
            #             TOKEN_RESET_INTERVAL_MONTH,
            #             TOKEN_RESET_INTERVAL_NEVER
            #         ],
            #         multiple=False,
            #         translation_key=CONF_TOKEN_RESET_INTERVAL
            #     )
            # ),
        })

        agent_name = self.config_entry.data.get(CONF_AGENT_NAME, CONF_AGENT_NAME_DEFAULT)
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={"agent_name": agent_name},
        )
