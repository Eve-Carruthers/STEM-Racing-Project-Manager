"""
A lightweight in‑memory chat system.

This class provides a minimal approximation of the chat functionality
described in the project report.  It supports creating channels and
posting messages, and storing simple metadata.  In a production system
this would be replaced by integration with a dedicated chat service or
websocket‑based chat server.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class ChatMessage:
    channel: str
    author: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class ChatSystem:
    """Manage channels and messages for project communication."""

    def __init__(self) -> None:
        self.channels: Dict[str, List[ChatMessage]] = {}

    def create_channel(self, name: str) -> None:
        """Create a new channel if it does not already exist."""
        if name not in self.channels:
            self.channels[name] = []

    def post_message(self, channel: str, author: str, content: str) -> None:
        """Post a message to a channel.  The channel must exist."""
        if channel not in self.channels:
            raise ValueError(f"Channel '{channel}' does not exist")
        message = ChatMessage(channel=channel, author=author, content=content)
        self.channels[channel].append(message)

    def get_messages(self, channel: str, limit: int | None = None) -> List[ChatMessage]:
        """Retrieve messages from a channel.  If ``limit`` is provided, return
        only the most recent messages up to that limit.
        """
        if channel not in self.channels:
            raise ValueError(f"Channel '{channel}' does not exist")
        messages = self.channels[channel]
        if limit is None or limit >= len(messages):
            return messages[:]
        else:
            return messages[-limit:]