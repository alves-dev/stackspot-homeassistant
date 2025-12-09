# Technical Reference: Prompt Variables

This document describes the variables exposed by the integration for use inside prompts and template-based configurations. 
All variables listed below are injected automatically.
---

## How to use

- Use `| tojson(indent=2)` to exit formatted.
- Use `| selectattr("labels", "contains", "label_name")` to filter the records.

**Examples:**
```
{{ all_variables | tojson(indent=2) }}

{{ exposed_entities | selectattr("labels", "contains", "label_name") | list | tojson(indent=2) }}

{{ scripts | selectattr("labels", "contains", "label_name") | list | tojson(indent=2) }}

{{ services | selectattr("domain", "equalto", "homeassistant") | list | tojson(indent=2) }}
```
---

## Variables

### `user`
- **Type:** `str`  
- **Description:** Logged-in user's name
- **Note:** This only works when the assist is called via chat in the UI
- **Available since:** `1.2.2`
- **Structure:**
```
Igor Moreira
```


### `exposed_entities`
- **Type:** `list[dict]`  
- **Description:** A list of entities exposed with their alias, [see](https://www.home-assistant.io/voice_control/voice_remote_expose_devices/)
- **Note:** Is created at the HA start and updated every 5 minutes.
- **Available since:** `1.3.0`
- **Structure:**
```json
[
  {
    "aliases": [],
    "entity_id": "todo.shopping_list",
    "labels": [],
    "name": "Shopping List"
  },
  {
    "aliases": [
      "aliase"
    ],
    "entity_id": "script.my_script",
    "labels": [
      "label_name"
    ],
    "name": "my script"
  }
]
```


### `tools`
- **Type:** `list[dict]`  
- **Description:** List the tools provided by the integration.
- **Note:** Is created at the HA start.
- **Available since:** `1.7.0`
- **Structure:**
```json
[
  {
    "description": "Obtains the state of an entity by the id",
    "name": "get_entity_state",
    "parameters": {
      "entity_id": "string"
    }
  },
  {
    "description": "Call a service on home assistant",
    "name": "call_service",
    "parameters": {
      "data": "object",
      "domain": "string",
      "service": "string"
    }
  }
]
```


### `tools_prompt`
- **Type:** `str`  
- **Description:** Prompt injected when using `Allow control` in the agent.
- **Note:** Is created at the HA start.
- **Available since:** `1.7.0`
- **Structure:**
```json
<tools_orientation>
 prompt  orientation
The expected reply format is:
<format>
{
  "tool_call": [
    {
      "identifier": "<random_identifier>",
      "name": "<nome_da_tool>",
      "parameters": "<object>"
    }
  ]
}
</format>

<tools>
  list
</tools>

</tools_orientation>
```


### `services`
- **Type:** `list[dict]`  
- **Description:** List of services
- **Note:** Is created at the HA start and updated every 5 minutes.
- **Available since:** `1.7.0`
- **Structure:**
```json
[
  {
    "domain": "notify",
    "name": "notify.notify",
    "service": "notify"
  },
  {
    "domain": "todo",
    "name": "todo.add_item",
    "service": "add_item"
  }
]
```


### `scripts`
- **Type:** `list[dict]`  
- **Description:** List of scripts.
- **Note:** 
  - Is created at the HA start and updated every 5 minutes.
  -  They are retrieved from the `scripts.yaml` file.
- **Available since:** `1.7.0`
- **Structure:**
```json
[
  {
    "aliases": [
      "aliase 1",
      "aliase 2"
    ],
    "description": "description test",
    "entity_id": "script.my_script",
    "fields": {
      "datetime": {
        "default": "2025-09-24 19:20:20",
        "selector": {
          "datetime": {}
        }
      },
      "device": {
        "name": "device",
        "selector": {
          "device": {}
        }
      },
      "value_text": {
        "name": "value text",
        "selector": {
          "text": null
        }
      }
    },
    "labels": [
      "label 1",
      "label 2"
    ],
    "name": "my script"
  }
]
```


### `all_variables`
- **Type:** `dict[dict]`  
- **Description:** Containing the **value** of all variables available through the integration
- **Note:** Is created at the HA start and updated every 5 minutes.
- **Available since:** `1.7.0`
- **Structure:**
```json
{
  "exposed_entities": [
  ],
  "tools": [
  ],
  "tools_prompt": "",
  "services": [
  ],
  "scripts": [
  ]
}
```