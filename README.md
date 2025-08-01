# Integration StackSpot AI with Home Assistant

![banner_dark.png](.docs/stackspot_ha_banner_dark.png)


[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alves-dev&repository=stackspot-homeassistant&category=integration)

## 📋 Changelog

See all changes in [CHANGELOG.md](./CHANGELOG.md)

### What is it
This is an integration of [Home Assistant](https://www.home-assistant.io) to connect to the [Stackspot AI](https://stackspot.com/en) platform, 
Which is a platform of AI, where you can easily create your custom agents with various different models.

### Requirement
Just have an account on the Stackspot platform: [Create Freemium Account](https://ai.stackspot.com)

### Functionality
Allows you to create multiple agents for the same account and have a control over the use of tokens.

![interaction.png](.docs/interaction.png)

### Installation
Integration can be adding via HACS, just click the following button:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alves-dev&repository=stackspot-homeassistant&category=integration)


### Settings
After adding and installing the integration, set up with:

![config.png](.docs/new_entry.png)
![new_agent.png](.docs/new_agent.png)

- `Account name` and `Agent name`: Are free text
- `realm`: For account freemium use `stackspot-freemium`
- `client_id` and `client_key`: Are credentials to access your account, and can be purchased [here](https://myaccount.stackspot.com/profile/access-token).
- `agent`: ID of the agent you want to use, [here](https://www.linkedin.com/pulse/seu-agente-de-ia-do-jeito-igor-moreira-nhu6f/) you can see how to create one.
- `Maximum number of messages in the history`: Defines how many recent messages will be kept in the history for each section
- `Prompt`: A template that becomes an additional prompt for the agent. Note that the variable `user` is provided by integration.
  - List of provided variables available:
    - `user` - Logged user name

You can have multiple agents, see:

![integration.png](.docs/integration.png)

---
### Assistant

Now you can go to `Assistants` and click `+ ADD ASSISTANT`:

[![Open your Home Assistant instance and show your voice assistants.](https://my.home-assistant.io/badges/voice_assistants.svg)](https://my.home-assistant.io/redirect/voice_assistants/)

In the listing the options will be the name of the agent + `Conversation`:

![add_asistant.png](.docs/add_asistant.png)

After created just use the shortcut `a` that the conversation interface will be opened:

![interaction.png](.docs/interaction.png)

With each interaction with the agent the tokens will be accounted for in the sensors,
and the general sensor:

![sensor_tokens.png](.docs/sensor_tokens.png)
![sensor_tokens_general.png](.docs/sensor_tokens_general.png)

### Flow

```mermaid
flowchart TD
    user_input[User input] --> history_add_input[Add input to history]
    history_add_input --> history_get[Get full history]
    history_get --> render_prompt[Render integration prompt template]
    render_prompt --> assemble_payload[Assemble payload:<br/>- Integration prompt<br/>- History<br/>- Input]
    assemble_payload --> send_to_stackspot[Send to StackSpot API]
    send_to_stackspot --> apply_stackspot_prompt

    subgraph StackSpot
        apply_stackspot_prompt[Apply StackSpot prompt + payload]
        apply_stackspot_prompt --> call_model[Call StackSpot LLM]
        call_model --> return_response[Return response]
    end

    return_response --> history_add_response[Add response to history]
    return_response --> tokens[Update token count]
    history_add_response --> user_output["Return to user (HA)"]

    style apply_stackspot_prompt fill: #ed4e2b
    style call_model fill: #ed4e2b
    style return_response fill: #ed4e2b
```

### Debug

To debug the integration, you must add the following lines to the configuration file:

```yaml
logger:
  default: info
  logs:
    custom_components.stackspot: debug
```

### Limitations

At the moment the integration is not yet able to access their entities, as well as will not be able to change status of their entities.