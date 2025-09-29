"""
Message handlers for different types of MQTT messages.
"""
import json
from typing import Dict, Any, List
from datetime import datetime
from .models import ChatRequest, Group, Message


class MessageHandlers:
    """Handles different types of MQTT messages."""
    
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
    
    def handle_control_message(self, data: Dict[str, Any]) -> None:
        """Handle control messages (chat requests, accepts, rejects, etc.)."""
        message_type = data.get("type")
        
        if message_type == "chat_request":
            self._handle_chat_request(data)
        elif message_type == "chat_accept":
            self._handle_chat_accept(data)
        elif message_type == "chat_reject":
            self._handle_chat_reject(data)
        elif message_type == "group_request":
            self._handle_group_request(data)
        elif message_type == "group_accept":
            self._handle_group_accept(data)
        elif message_type == "group_reject":
            self._handle_group_reject(data)
        elif message_type == "subscribed_topics":
            self._handle_subscribed_topics(data)
    
    def _handle_chat_request(self, data: Dict[str, Any]) -> None:
        """Handle incoming chat request."""
        from_user = data.get("from")
        session_id = data.get("session_id")
        
        request = ChatRequest(
            from_user=from_user,
            session_id=session_id,
            timestamp=datetime.now()
        )
        
        self.mqtt_client.pending_requests.append(request)
        print(f"\n\nNew chat request from user {from_user}")
        print(f"Session ID: {session_id}\n")
    
    def _handle_chat_accept(self, data: Dict[str, Any]) -> None:
        """Handle chat acceptance."""
        session_id = data.get("session_id")
        chat_topic = data.get("chat_topic")
        
        self.mqtt_client.accepted_requests.append({
            "session_id": session_id,
            "chat_topic": chat_topic,
            "timestamp": datetime.now().isoformat()
        })
        
        self.mqtt_client.client.subscribe(chat_topic, qos=1)
        self.mqtt_client.active_sessions[session_id] = chat_topic
        
        print(f"\n\nChat accepted! Topic: {chat_topic}")
    
    def _handle_chat_reject(self, data: Dict[str, Any]) -> None:
        """Handle chat rejection."""
        session_id = data.get("session_id")
        print(f"\nChat rejected for session: {session_id}")
    
    def _handle_group_request(self, data: Dict[str, Any]) -> None:
        """Handle group join request."""
        from_user = data.get("from")
        group_name = data.get("group_name")
        session_id = data.get("session_id")
        
        request = ChatRequest(
            from_user=from_user,
            session_id=session_id,
            timestamp=datetime.now(),
            request_type="group",
            group_name=group_name
        )
        
        self.mqtt_client.pending_requests.append(request)
        print(f"\n\nNew group request from user {from_user}")
        print(f"Group: {group_name}")
        print(f"Session ID: {session_id}\n")
    
    def _handle_group_accept(self, data: Dict[str, Any]) -> None:
        """Handle group request acceptance."""
        session_id = data.get("session_id")
        group_topic = data.get("group_topic")
        group_name = data.get("group_name")
        
        self.mqtt_client.accepted_requests.append({
            "session_id": session_id,
            "group_topic": group_topic,
            "group_name": group_name,
            "timestamp": datetime.now().isoformat()
        })
        
        self.mqtt_client.client.subscribe(group_topic, qos=1)
        self.mqtt_client.active_sessions[session_id] = group_topic
        
        print(f"\n\nGroup request accepted! Topic: {group_topic}")
        print(f"Group: {group_name}")
    
    def _handle_group_reject(self, data: Dict[str, Any]) -> None:
        """Handle group request rejection."""
        session_id = data.get("session_id")
        group_name = data.get("group_name")
        print(f"\nGroup request rejected for session: {session_id}")
        print(f"Group: {group_name}")
    
    def _handle_subscribed_topics(self, data: Dict[str, Any]) -> None:
        """Handle previously subscribed topics on reconnection."""
        topics = data.get("topics", [])
        
        if not topics:
            return
        
        print(f"\nLoading {len(topics)} previously subscribed topics...")
        
        for topic_info in topics:
            topic_type = topic_info.get("type")
            
            if topic_type == "chat":
                session_id = topic_info.get("session_id")
                topic = topic_info.get("topic")
                if session_id and topic:
                    self.mqtt_client.client.subscribe(topic, qos=1)
                    self.mqtt_client.active_sessions[session_id] = topic
                    print(f"Resubscribed to chat: {session_id}")
            
            elif topic_type == "group":
                group_name = topic_info.get("group_name")
                topic = topic_info.get("topic")
                if group_name and topic:
                    self.mqtt_client.client.subscribe(topic, qos=1)
                    print(f"Resubscribed to group: {group_name}")
    
    def handle_users_message(self, data: Dict[str, Any]) -> None:
        """Handle users topic messages."""
        message_type = data.get("type")
        
        if message_type == "status_update":
            user_id = data.get("user_id")
            status = data.get("status")
            self.mqtt_client.online_users[user_id] = status
        elif message_type == "users_list":
            users = data.get("users", {})
            self.mqtt_client.online_users.update(users)
        elif message_type == "request_users_list":
            requesting_user = data.get("from")
            if requesting_user != self.mqtt_client.user_id:
                response = {
                    "type": "status_update",
                    "user_id": self.mqtt_client.user_id,
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                }
                self.mqtt_client.client.publish(
                    self.mqtt_client.users_topic, 
                    json.dumps(response)
                )
    
    def handle_groups_message(self, data: Dict[str, Any]) -> None:
        """Handle groups topic messages."""
        message_type = data.get("type")
        
        if message_type == "group_update":
            group_name = data.get("group_name")
            group_info = data.get("group_info")
            self.mqtt_client.groups[group_name] = group_info
        elif message_type == "groups_list":
            groups = data.get("groups", {})
            self.mqtt_client.groups.update(groups)
    
    def handle_chat_message(self, topic: str, data: Dict[str, Any]) -> None:
        """Handle chat messages."""
        from_user = data.get("from")
        message = data.get("message")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        print(f"[{timestamp}] {from_user}: {message}")
    
    def handle_group_chat_message(self, topic: str, data: Dict[str, Any]) -> None:
        """Handle group chat messages."""
        from_user = data.get("from")
        message = data.get("message")
        group_name = data.get("group_name")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        print(f"\n[{timestamp}] {group_name} - {from_user}: {message}")
