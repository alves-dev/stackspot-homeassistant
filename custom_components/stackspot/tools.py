import json
import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

_tool_call_example: dict = {
    "tool_call": [
        {
            "identifier": "<random_identifier>",
            "name": "<nome_da_tool>",
            "parameters": "<object>"
        }
    ]
}

_tools_orientation: str = """
<tools_orientation>
Whenever possible, use Tools to get real data from the environment.
If the user asks a question or request that requires Home Assistant information, you should decide which Tool to use.
A TOOL can be called several times at the same time, use <random_identifier> to identify the result later.
If no Tool is necessary, respond only in natural language.
The expected reply format is:

<format>
{{tool_call_example}}
</format>

<tools>
{{tools}}
</tools>

</tools_orientation>
"""


@dataclass
class ToolInput:
    identifier: str
    name: str
    parameters: dict


@dataclass
class ToolResult:
    identifier: str
    success: bool
    result: dict

    @classmethod
    def of_success(cls, identifier: str, result: dict) -> "ToolResult":
        return ToolResult(identifier, True, result)

    @classmethod
    def of_fail(cls, identifier: str, result: dict) -> "ToolResult":
        return ToolResult(identifier, False, result)

    def to_dict(self) -> dict:
        return {
            "identifier": self.identifier,
            "success": self.success,
            "result": self.result
        }


class Tool:
    """LLM Tool base class."""

    name: str
    description: str
    parameters: dict

    @abstractmethod
    async def async_call(self, hass: HomeAssistant, tool_input: ToolInput) -> ToolResult:
        """Call the tool."""
        raise NotImplementedError

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class EntityStateTool(Tool):
    name = "get_entity_state"
    description = "Obtains the state of an entity by the id"
    parameters = {
        "entity_id": "string"
    }

    async def async_call(self, hass: HomeAssistant, tool_input: ToolInput) -> ToolResult:
        state = hass.states.get(tool_input.parameters['entity_id'])
        if state:
            entity = {
                "entity_id": tool_input.parameters['entity_id'],
                "state": state.state,
                "attributes": state.attributes,
            }
            return ToolResult.of_success(tool_input.identifier, entity)

        return ToolResult.of_fail(tool_input.identifier, {})


class CallServiceTool(Tool):
    name = "call_service"
    description = "Call a service on home assistant"
    parameters = {
        "domain": "string",
        "service": "string",
        "data": "object"
    }

    async def async_call(self, hass: HomeAssistant, tool_input: ToolInput) -> ToolResult:
        try:
            await hass.services.async_call(
                tool_input.parameters["domain"],
                tool_input.parameters["service"],
                tool_input.parameters.get("data", {}),
                blocking=True,
            )
            return ToolResult.of_success(tool_input.identifier, {"status": "ok"})
        except Exception as e:
            return ToolResult.of_fail(tool_input.identifier, {"error": str(e)})


class GetTodoItemsTool(Tool):
    name = "get_todo_items"
    description = "Get items from a Home Assistant to-do list. Possible status: ['needs_action', 'completed']"
    parameters = {
        "entity_id": "string",
        "status": ["string"]
    }

    async def async_call(self, hass: HomeAssistant, tool_input: ToolInput) -> ToolResult:
        entity_id = tool_input.parameters.get("entity_id")
        status = tool_input.parameters.get("status", ["needs_action"])

        if not entity_id:
            return ToolResult.of_fail(tool_input.identifier, {"error": "Missing required field: entity_id"})

        try:
            result = await hass.services.async_call(
                "todo",
                "get_items",
                {
                    "entity_id": entity_id,
                    "status": status,
                },
                blocking=True,
                return_response=True,
            )

            return ToolResult.of_success(tool_input.identifier, {"items": result})
        except Exception as e:
            return ToolResult.of_fail(tool_input.identifier, {"error": str(e)})


_tools: list[dict] = [EntityStateTool().to_dict(), CallServiceTool().to_dict(), GetTodoItemsTool().to_dict()]
TOOLS_CLASS: dict[str, type[Tool]] = {
    EntityStateTool.name: EntityStateTool,
    CallServiceTool.name: CallServiceTool,
    GetTodoItemsTool.name: GetTodoItemsTool,
}

PROMPT_TOOLS: str = (_tools_orientation
                     .replace("{{tools}}", json.dumps(_tools, indent=2, ensure_ascii=False))
                     .replace("{{tool_call_example}}", json.dumps(_tool_call_example, indent=2, ensure_ascii=False))
                     )


async def process_response_tools(hass: HomeAssistant, response: str) -> dict:
    tools: Optional[List[ToolInput]] = _parse_tool_response(response)
    if not tools:
        return {"tools": False}

    results: list[dict] = []
    for tool_input in tools:
        cls: type(Tool) = TOOLS_CLASS[tool_input.name]
        result: ToolResult = await cls().async_call(hass, tool_input)
        results.append(result.to_dict())

    result_content: str = json.dumps(results, indent=2, ensure_ascii=False)
    return {
        "tools": True,
        "content": result_content
    }


def _parse_tool_response(response: str) -> Optional[List[ToolInput]]:
    """
    Valida e converte a resposta do LLM em uma lista de ToolInput.
    Retorna None se a resposta não for um JSON válido ou não tiver tool_call.
    """
    if not response:
        return None

    # Tenta extrair apenas o JSON entre { ... }
    try:
        start = response.index("{")
        end = response.rindex("}") + 1
        json_str = response[start:end]
    except ValueError:
        return None

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return None

    tool_calls = data.get("tool_call")
    if not isinstance(tool_calls, list):
        return None

    results: List[ToolInput] = []
    for call in tool_calls:
        identifier = call.get("identifier")
        name = call.get("name")
        params = call.get("parameters", {})

        if not identifier or not name:
            continue

        results.append(
            ToolInput(
                identifier=identifier,
                name=name,
                parameters=params if isinstance(params, dict) else {}
            )
        )

    return results if results else None
