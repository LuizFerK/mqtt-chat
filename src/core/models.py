"""
Data models for the MQTT Chat application.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class User:
    """Represents a user in the system."""
    user_id: str
    status: str = "offline"
    last_seen: Optional[datetime] = None


@dataclass
class ChatRequest:
    """Represents a chat request between users."""
    from_user: str
    session_id: str
    timestamp: datetime
    request_type: str = "chat"  # "chat" or "group"
    group_name: Optional[str] = None


@dataclass
class ChatSession:
    """Represents an active chat session."""
    session_id: str
    chat_topic: str
    participants: List[str]
    created_at: datetime
    is_group: bool = False
    group_name: Optional[str] = None


@dataclass
class Group:
    """Represents a chat group."""
    name: str
    leader: str
    members: List[str]
    created_at: datetime
    topic: str


@dataclass
class Message:
    """Represents a chat message."""
    from_user: str
    content: str
    timestamp: datetime
    session_id: Optional[str] = None
    group_name: Optional[str] = None


@dataclass
class MQTTMessage:
    """Represents an MQTT message with metadata."""
    topic: str
    payload: str
    qos: int = 1
    retain: bool = False
