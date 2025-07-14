import voluptuous as vol
from homeassistant import config_entries

from .const import (
    INTEGRATION_NAME,
    DOMAIN,
    CONF_REALM,
    CONF_CLIENT_ID,
    CONF_CLIENT_KEY,
    CONF_AGENT_ID,
    CONF_REALM_DEFAULT,
    CONF_AGENT_NAME,
    CONF_AGENT_NAME_DEFAULT
)


@config_entries.HANDLERS.register(DOMAIN)
class StackspotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=INTEGRATION_NAME,
                data={
                    CONF_AGENT_NAME: user_input[CONF_AGENT_NAME],
                    CONF_AGENT_ID: user_input[CONF_AGENT_ID],
                    CONF_REALM: user_input[CONF_REALM],
                    CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                    CONF_CLIENT_KEY: user_input[CONF_CLIENT_KEY],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_AGENT_NAME, description={"suggested_value": CONF_AGENT_NAME_DEFAULT}): str,
                vol.Required(CONF_AGENT_ID): str,
                vol.Required(CONF_REALM, default=CONF_REALM_DEFAULT): str,
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_KEY): str,
            }),
            errors=errors,
        )
