from dataclasses import dataclass, field
from datetime import datetime, UTC, timezone
from enum import StrEnum
from typing import List

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import STATE_UNKNOWN

from custom_components.stackspot.const import (
    CONF_AGENT_ID,
    CONF_AGENT_NAME,
    CONF_CLIENT_ID,
    CONF_REALM,
    CONF_CLIENT_KEY,
    CONF_AGENT_MAX_MESSAGES_HISTORY,
    CONF_AGENT_PROMPT,
    CONF_AGENT_PROMPT_DEFAULT,
    CONF_KS_NAME,
    CONF_KS_SLUG,
    CONF_KS_TEMPLATE,
    CONF_KS_TEMPLATE_DEFAULT,
)


class MessageRole(StrEnum):
    """Role of a chat message."""

    #SYSTEM = "system"  # prompt
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    role: MessageRole
    content: str


@dataclass
class ContextValue:
    messages: List[Message] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, role: MessageRole, content: str) -> None:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self.last_interaction = datetime.now(UTC)

    def get_history(self) -> list[dict]:
        return [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in self.messages
        ]

    def trim(self, max_messages: int) -> None:
        if not isinstance(self.messages, list):
            return

        while len(self.messages) > max_messages:
            self.messages.pop(0)


@dataclass(frozen=True)
class StackSpotAgentConfig:
    """Dataclass para a configuração de um agente StackSpot."""
    entry_id: str
    subentry_id: str
    agent_name: str
    agent_id: str
    realm: str
    client_id: str
    client_key: str
    max_messages_history: int
    prompt: str

    @classmethod
    def from_entry(cls, entry: ConfigEntry, subentry: ConfigSubentry) -> "StackSpotAgentConfig":
        return cls(
            entry_id=entry.entry_id,
            subentry_id=subentry.subentry_id,
            agent_name=subentry.data[CONF_AGENT_NAME],
            agent_id=subentry.data[CONF_AGENT_ID],
            realm=entry.data[CONF_REALM],
            client_id=entry.data[CONF_CLIENT_ID],
            client_key=entry.data[CONF_CLIENT_KEY],
            max_messages_history=int(subentry.data.get(CONF_AGENT_MAX_MESSAGES_HISTORY, 10)),
            prompt=subentry.data.get(CONF_AGENT_PROMPT, CONF_AGENT_PROMPT_DEFAULT)
        )

    @classmethod
    def from_entry_for_task(cls, entry: ConfigEntry, subentry: ConfigSubentry) -> "StackSpotAgentConfig":
        return cls(
            entry_id=entry.entry_id,
            subentry_id=subentry.subentry_id,
            agent_name=subentry.data[CONF_AGENT_NAME],
            agent_id=subentry.data[CONF_AGENT_ID],
            realm=entry.data[CONF_REALM],
            client_id=entry.data[CONF_CLIENT_ID],
            client_key=entry.data[CONF_CLIENT_KEY],
            max_messages_history=0,
            prompt=subentry.data.get(CONF_AGENT_PROMPT, CONF_AGENT_PROMPT_DEFAULT)
        )


@dataclass(frozen=True)
class StackSpotLogin:
    """Dataclass para request token StackSpot."""
    realm: str
    client_id: str
    client_key: str

    @classmethod
    def from_entry(cls, entry: ConfigEntry) -> "StackSpotLogin":
        return cls(
            realm=entry.data[CONF_REALM],
            client_id=entry.data[CONF_CLIENT_ID],
            client_key=entry.data[CONF_CLIENT_KEY]
        )


@dataclass(frozen=True)
class KSData:
    subentry_id: str
    name: str
    slug: str
    template: str

    @classmethod
    def from_entry(cls, subentry: ConfigSubentry) -> "KSData":
        return cls(
            subentry_id=subentry.subentry_id,
            name=subentry.data.get(CONF_KS_NAME, STATE_UNKNOWN),
            slug=subentry.data.get(CONF_KS_SLUG, STATE_UNKNOWN),
            template=subentry.data.get(CONF_KS_TEMPLATE, CONF_KS_TEMPLATE_DEFAULT),
        )
