"""
Refactored MQTT Client with better organization.
"""
import paho.mqtt.client as mqtt
import json
import threading
from typing import Dict, List, Optional
from datetime import datetime

from .message_handlers import MessageHandlers
from .mqtt_operations import MQTTOperations
from .models import ChatRequest, Group, Message


class MQTTClient:
    """Refactored MQTT Client with separated concerns."""
    
    def __init__(self, user_id: str, broker_host: str = "localhost", broker_port: int = 1883):
        self.user_id = user_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, 
            client_id=user_id, 
            clean_session=False
        )

        # Topic definitions
        self.control_topic = f"{user_id}_Control"
        self.users_topic = "USERS"
        self.groups_topic = "GROUPS"
        
        # State management
        self.online_users = {}
        self.groups = {}
        self.active_sessions = {}
        self.pending_requests = []
        self.accepted_requests = []
        
        # Initialize handlers and operations
        self.message_handlers = MessageHandlers(self)
        self.mqtt_operations = MQTTOperations(self)
        
        # Setup client
        self._setup_client()
    
    def _setup_client(self):
        """Setup MQTT client callbacks."""
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc, props):
        """Handle MQTT connection."""
        if rc == 0:
            self.client.subscribe(self.control_topic, qos=1)
            self.client.subscribe(self.users_topic, qos=1)
            self.client.subscribe(self.groups_topic, qos=1)
            
            self.mqtt_operations.announce_online()
            self.mqtt_operations.request_users_list()
            self.mqtt_operations.request_groups_list()
        else:
            print(f"Connection failed. Code: {rc}")
    
    def _on_disconnect(self, client, userdata, flags, rc, props):
        """Handle MQTT disconnection."""
        print("Disconnected from MQTT broker")
        self.mqtt_operations.announce_offline()
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {"message": payload}
        
        if topic == self.control_topic:
            self.message_handlers.handle_control_message(data)
        elif topic == self.users_topic:
            self.message_handlers.handle_users_message(data)
        elif topic == self.groups_topic:
            self.message_handlers.handle_groups_message(data)
        elif topic in self.active_sessions:
            self.message_handlers.handle_chat_message(topic, data)
        else:
            # Check if it's a group topic
            for group_name, group_info in self.groups.items():
                if topic == f"GROUP_{group_name}":
                    self.message_handlers.handle_group_chat_message(topic, data)
                    break
    
    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            self.client.connect_async(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.mqtt_operations.announce_offline()
        self.client.loop_stop()
        self.mqtt_operations.store_subscribed_topics()
        self.client.disconnect()
    
    # Chat operations
    def request_chat(self, target_user: str) -> str:
        """Request a chat with another user."""
        from ..utils.helpers import generate_session_id
        
        session_id = generate_session_id(self.user_id, target_user)
        self.mqtt_operations.send_chat_request(target_user, session_id)
        
        print(f"\nRequest sent to user {target_user}")
        print(f"Session ID: {session_id}")
        
        return session_id
    
    def accept_chat(self, session_id: str):
        """Accept a chat request."""
        request = None
        for req in self.pending_requests:
            if req.session_id == session_id:
                request = req
                break
        
        if not request:
            print("Request not found")
            return
        
        chat_topic = session_id
        self.client.subscribe(chat_topic, qos=1)
        self.active_sessions[session_id] = chat_topic
        
        self.mqtt_operations.send_chat_accept(request.from_user, session_id, chat_topic)
        self.pending_requests.remove(request)
        
        print(f"\nChat accepted with user {request.from_user}")
        print(f"Topic: {chat_topic}")
    
    def reject_chat(self, session_id: str):
        """Reject a chat request."""
        request = None
        for req in self.pending_requests:
            if req.session_id == session_id:
                request = req
                break
        
        if not request:
            print("Request not found")
            return
        
        self.mqtt_operations.send_chat_reject(request.from_user, session_id)
        self.pending_requests.remove(request)
        
        print(f"\nChat rejected with user {request.from_user}")
    
    def send_message(self, session_id: str, message: str):
        """Send a message in a chat session."""
        if session_id not in self.active_sessions:
            print("Session not found")
            return
        
        chat_topic = self.active_sessions[session_id]
        self.mqtt_operations.send_chat_message(chat_topic, message)
    
    # Group operations
    def create_group(self, group_name: str):
        """Create a new group."""
        group_info = {
            "name": group_name,
            "leader": self.user_id,
            "members": [self.user_id],
            "created_at": datetime.now().isoformat()
        }
        
        self.mqtt_operations.publish_group_update(group_name, group_info)
        self.groups[group_name] = group_info
        
        group_topic = f"GROUP_{group_name}"
        self.client.subscribe(group_topic, qos=1)
        
        print(f"Group '{group_name}' created successfully!")
    
    def join_group(self, group_name: str):
        """Request to join a group."""
        if group_name not in self.groups:
            print("Group not found")
            return
        
        group_info = self.groups[group_name]
        leader = group_info["leader"]
        
        self.mqtt_operations.send_group_request(group_name, leader)
        print(f"Join request sent to group '{group_name}'")
    
    def accept_group_request(self, group_name: str, user_id: str):
        """Accept a group join request."""
        if group_name not in self.groups:
            print("Group not found")
            return
        
        group_info = self.groups[group_name]
        if group_info["leader"] != self.user_id:
            print("Only the leader can accept requests")
            return
        
        if user_id not in group_info["members"]:
            group_info["members"].append(user_id)
            
            self.mqtt_operations.publish_group_update(group_name, group_info)
            self.groups[group_name] = group_info
            
            group_topic = f"GROUP_{group_name}"
            self.mqtt_operations.send_group_accept(user_id, group_name, group_topic)
            
            print(f"{user_id} added to group '{group_name}'")
    
    def reject_group_request(self, group_name: str, user_id: str):
        """Reject a group join request."""
        if group_name not in self.groups:
            print("Group not found")
            return
        
        group_info = self.groups[group_name]
        if group_info["leader"] != self.user_id:
            print("Only the leader can reject requests")
            return
        
        self.mqtt_operations.send_group_reject(user_id, group_name)
        print(f"Rejected {user_id} from group '{group_name}'")
    
    def send_group_message(self, group_name: str, message: str):
        """Send a message to a group."""
        if group_name not in self.groups:
            print("Group not found")
            return
        
        group_info = self.groups[group_name]
        if self.user_id not in group_info["members"]:
            print("You are not a member of this group")
            return
        
        group_topic = f"GROUP_{group_name}"
        self.mqtt_operations.send_group_message(group_topic, group_name, message)
        print(f"Message sent to group '{group_name}': {message}")
    
    # Getters for UI
    def get_online_users(self) -> Dict[str, str]:
        """Get online users."""
        return {user: status for user, status in self.online_users.items() if status == "online"}
    
    def get_pending_requests(self) -> List[Dict]:
        """Get pending requests."""
        return [req.__dict__ if hasattr(req, '__dict__') else req for req in self.pending_requests]
    
    def get_accepted_requests(self) -> List[Dict]:
        """Get accepted requests."""
        return self.accepted_requests.copy()
    
    def get_groups(self) -> Dict[str, Dict]:
        """Get all groups."""
        return self.groups.copy()
    
    def get_active_sessions(self) -> Dict[str, str]:
        """Get active chat sessions."""
        return self.active_sessions.copy()
