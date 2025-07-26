from dataclasses import dataclass, field
from datetime import datetime, UTC, timezone
from typing import Literal, List

from homeassistant.config_entries import ConfigEntry, ConfigSubentry

from custom_components.stackspot.const import CONF_AGENT_ID, CONF_AGENT_NAME, CONF_CLIENT_ID, CONF_REALM, \
    CONF_CLIENT_KEY, CONF_AGENT_MAX_MESSAGES_HISTORY


@dataclass
class Message:
    role: Literal["user", "assistant", "system"]
    content: str


@dataclass
class ContextValue:
    messages: List[Message] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, role: Literal["user", "assistant", "system"], content: str) -> None:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self.last_interaction = datetime.now(UTC)

    def get_history(self) -> list[dict]:
        return [
            {
                "role": msg.role,
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

    @classmethod
    def from_entry(cls, entry: ConfigEntry, subentry: ConfigSubentry) -> "StackSpotAgentConfig":
        return cls(
            entry_id=entry.entry_id,
            subentry_id=subentry.subentry_id,
            agent_id=subentry.data[CONF_AGENT_ID],
            agent_name=subentry.data[CONF_AGENT_NAME],
            max_messages_history=int(subentry.data.get(CONF_AGENT_MAX_MESSAGES_HISTORY, 10)),
            realm=entry.data[CONF_REALM],
            client_id=entry.data[CONF_CLIENT_ID],
            client_key=entry.data[CONF_CLIENT_KEY]
        )
