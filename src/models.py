from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class ChatRequest:
  from_user: str
  session_id: str
  timestamp: str
  
  def to_dict(self) -> Dict:
    return {
      "from": self.from_user,
      "session_id": self.session_id,
      "timestamp": self.timestamp
    }
  
  @classmethod
  def from_dict(cls, data: Dict) -> 'ChatRequest':
    return cls(
      from_user=data["from"],
      session_id=data["session_id"],
      timestamp=data["timestamp"]
    )


@dataclass
class GroupRequest:
  from_user: str
  group_name: str
  session_id: str
  timestamp: str
  
  def to_dict(self) -> Dict:
    return {
      "from": self.from_user,
      "group_name": self.group_name,
      "session_id": self.session_id,
      "timestamp": self.timestamp
    }
  
  @classmethod
  def from_dict(cls, data: Dict) -> 'GroupRequest':
    return cls(
      from_user=data["from"],
      group_name=data["group_name"],
      session_id=data["session_id"],
      timestamp=data["timestamp"]
    )


@dataclass
class GroupInfo:
  name: str
  leader: str
  members: List[str]
  created_at: str
  
  def to_dict(self) -> Dict:
    return {
      "name": self.name,
      "leader": self.leader,
      "members": self.members,
      "created_at": self.created_at
    }
  
  @classmethod
  def from_dict(cls, data: Dict) -> 'GroupInfo':
    return cls(
      name=data["name"],
      leader=data["leader"],
      members=data["members"],
      created_at=data["created_at"]
    )


@dataclass
class ChatMessage:
  from_user: str
  message: str
  timestamp: str
  group_name: Optional[str] = None
  
  def to_dict(self) -> Dict:
    data = {
      "from": self.from_user,
      "message": self.message,
      "timestamp": self.timestamp
    }
    if self.group_name:
      data["group_name"] = self.group_name
    return data
  
  @classmethod
  def from_dict(cls, data: Dict) -> 'ChatMessage':
    return cls(
      from_user=data["from"],
      message=data["message"],
      timestamp=data["timestamp"],
      group_name=data.get("group_name")
    )


@dataclass
class UserStatus:
  user_id: str
  status: str
  timestamp: str
  
  def to_dict(self) -> Dict:
    return {
      "user_id": self.user_id,
      "status": self.status,
      "timestamp": self.timestamp
    }
  
  @classmethod
  def from_dict(cls, data: Dict) -> 'UserStatus':
    return cls(
      user_id=data["user_id"],
      status=data["status"],
      timestamp=data["timestamp"]
    )