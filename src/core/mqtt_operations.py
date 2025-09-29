"""
MQTT operations for publishing and subscribing to topics.
"""
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from .models import Group


class MQTTOperations:
    """Handles MQTT publishing and subscription operations."""
    
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
    
    def announce_online(self) -> None:
        """Announce that the user is online."""
        message = {
            "type": "status_update",
            "user_id": self.mqtt_client.user_id,
            "status": "online",
            "timestamp": datetime.now().isoformat()
        }
        self.mqtt_client.client.publish(
            self.mqtt_client.users_topic, 
            json.dumps(message), 
            qos=1
        )
    
    def announce_offline(self) -> None:
        """Announce that the user is offline."""
        message = {
            "type": "status_update",
            "user_id": self.mqtt_client.user_id,
            "status": "offline",
            "timestamp": datetime.now().isoformat()
        }
        self.mqtt_client.client.publish(
            self.mqtt_client.users_topic, 
            json.dumps(message), 
            qos=1
        )
    
    def request_users_list(self) -> None:
        """Request the list of online users."""
        message = {
            "type": "request_users_list",
            "from": self.mqtt_client.user_id
        }
        self.mqtt_client.client.publish(
            self.mqtt_client.users_topic, 
            json.dumps(message), 
            qos=1
        )
        time.sleep(1)  # Give time for responses
    
    def request_groups_list(self) -> None:
        """Request the list of groups."""
        message = {
            "type": "request_groups_list",
            "from": self.mqtt_client.user_id
        }
        self.mqtt_client.client.publish(
            self.mqtt_client.groups_topic, 
            json.dumps(message)
        )
    
    def send_chat_request(self, target_user: str, session_id: str) -> None:
        """Send a chat request to another user."""
        message = {
            "type": "chat_request",
            "from": self.mqtt_client.user_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        target_control_topic = f"{target_user}_Control"
        self.mqtt_client.client.publish(
            target_control_topic, 
            json.dumps(message), 
            qos=1
        )
    
    def send_chat_accept(self, from_user: str, session_id: str, chat_topic: str) -> None:
        """Send chat acceptance to the requesting user."""
        message = {
            "type": "chat_accept",
            "session_id": session_id,
            "chat_topic": chat_topic,
            "timestamp": datetime.now().isoformat()
        }
        
        target_control_topic = f"{from_user}_Control"
        self.mqtt_client.client.publish(
            target_control_topic, 
            json.dumps(message), 
            qos=1
        )
    
    def send_chat_reject(self, from_user: str, session_id: str) -> None:
        """Send chat rejection to the requesting user."""
        message = {
            "type": "chat_reject",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        target_control_topic = f"{from_user}_Control"
        self.mqtt_client.client.publish(
            target_control_topic, 
            json.dumps(message), 
            qos=1
        )
    
    def send_group_request(self, group_name: str, leader: str) -> None:
        """Send a group join request to the group leader."""
        message = {
            "type": "group_request",
            "group_name": group_name,
            "from": self.mqtt_client.user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        leader_control_topic = f"{leader}_Control"
        self.mqtt_client.client.publish(
            leader_control_topic, 
            json.dumps(message)
        )
    
    def send_group_accept(self, user_id: str, group_name: str, group_topic: str) -> None:
        """Send group request acceptance to the requesting user."""
        message = {
            "type": "group_accept",
            "group_name": group_name,
            "group_topic": group_topic,
            "timestamp": datetime.now().isoformat()
        }
        
        user_control_topic = f"{user_id}_Control"
        self.mqtt_client.client.publish(
            user_control_topic, 
            json.dumps(message)
        )
    
    def send_group_reject(self, user_id: str, group_name: str) -> None:
        """Send group request rejection to the requesting user."""
        message = {
            "type": "group_reject",
            "group_name": group_name,
            "timestamp": datetime.now().isoformat()
        }
        
        user_control_topic = f"{user_id}_Control"
        self.mqtt_client.client.publish(
            user_control_topic, 
            json.dumps(message)
        )
    
    def publish_group_update(self, group_name: str, group_info: Dict) -> None:
        """Publish group information update."""
        message = {
            "type": "group_update",
            "group_name": group_name,
            "group_info": group_info
        }
        
        self.mqtt_client.client.publish(
            self.mqtt_client.groups_topic, 
            json.dumps(message), 
            qos=1
        )
    
    def send_chat_message(self, topic: str, message: str) -> None:
        """Send a chat message to a topic."""
        data = {
            "from": self.mqtt_client.user_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.mqtt_client.client.publish(topic, json.dumps(data), qos=1)
    
    def send_group_message(self, group_topic: str, group_name: str, message: str) -> None:
        """Send a message to a group."""
        data = {
            "from": self.mqtt_client.user_id,
            "group_name": group_name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.mqtt_client.client.publish(group_topic, json.dumps(data), qos=1)
    
    def store_subscribed_topics(self) -> None:
        """Store currently subscribed topics for reconnection."""
        subscribed_topics = []
        
        # Add active chat sessions
        for session_id, topic in self.mqtt_client.active_sessions.items():
            subscribed_topics.append({
                "type": "chat",
                "session_id": session_id,
                "topic": topic
            })
        
        # Add group subscriptions
        for group_name, group_info in self.mqtt_client.groups.items():
            if self.mqtt_client.user_id in group_info.get("members", []):
                subscribed_topics.append({
                    "type": "group",
                    "group_name": group_name,
                    "topic": f"GROUP_{group_name}"
                })
        
        if subscribed_topics:
            message = {
                "type": "subscribed_topics",
                "topics": subscribed_topics,
                "timestamp": datetime.now().isoformat()
            }
            
            self.mqtt_client.client.publish(
                self.mqtt_client.control_topic, 
                json.dumps(message), 
                qos=1
            )
            print(f"Stored {len(subscribed_topics)} subscribed topics")
