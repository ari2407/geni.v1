"""Bounded, scoped agent discussion bus; no recursive autonomous loops."""
from __future__ import annotations
from dataclasses import dataclass
from collections import deque

@dataclass(frozen=True)
class Message:
    sender: str
    channel: str
    content: str

class DiscussionBus:
    def __init__(self, max_messages: int = 1000):
        self.messages = deque(maxlen=max_messages)

    def publish(self, sender: str, channel: str, content: str) -> None:
        if not sender or not channel or not content or len(content) > 4000:
            raise ValueError("invalid discussion message")
        self.messages.append(Message(sender, channel, content))

    def read(self, channel: str, limit: int = 20) -> list[Message]:
        if limit < 1: raise ValueError("limit must be positive")
        return [message for message in self.messages if message.channel == channel][-limit:]
