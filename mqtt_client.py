import paho.mqtt.client as mqtt
import json
import time
import threading
from typing import Dict, List, Callable, Optional
from datetime import datetime


class MQTTClient:
    def __init__(self, user_id: str, broker_host: str = "localhost", broker_port: int = 1883):
        self.user_id = user_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5, client_id=user_id)

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
        
        # Callbacks
        self.message_callbacks = {}
        self.control_callbacks = {}
        
        # Setup client
        self._setup_client()
    
    def _setup_client(self):
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc, props):
        if rc == 0:
            self.client.subscribe(self.control_topic)
            self.client.subscribe(self.users_topic)
            self.client.subscribe(self.groups_topic)
            
            self._announce_online()
            
            self._request_users_list()
            self._request_groups_list()
        else:
            print(f"Connection failed. Code: {rc}")
    
    def _on_disconnect(self, client, userdata, flags, rc, props):
        print("Disconnected from MQTT broker")
        self._announce_offline()
    
    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {"message": payload}
        
        if topic == self.control_topic:
            self._handle_control_message(data)
        elif topic == self.users_topic:
            self._handle_users_message(data)
        elif topic == self.groups_topic:
            self._handle_groups_message(data)
        elif topic in self.active_sessions:
            self._handle_chat_message(topic, data)
        else:
            for group_name, group_info in self.groups.items():
                if topic == f"GROUP_{group_name}":
                    self._handle_group_chat_message(topic, data)
                    break
    
    def _handle_control_message(self, data):
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
    
    def _handle_chat_request(self, data):
        from_user = data.get("from")
        session_id = data.get("session_id")
        
        request = {
            "from": from_user,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        self.pending_requests.append(request)
        print(f"\n\nNew chat request from user {from_user}")
        print(f"Session ID: {session_id}\n")
    
    def _handle_chat_accept(self, data):
        session_id = data.get("session_id")
        chat_topic = data.get("chat_topic")
        
        self.accepted_requests.append({
            "session_id": session_id,
            "chat_topic": chat_topic,
            "timestamp": datetime.now().isoformat()
        })
        
        self.client.subscribe(chat_topic)
        self.active_sessions[session_id] = chat_topic
        
        print(f"\n\nChat accepted! Topic: {chat_topic}")
    
    def _handle_chat_reject(self, data):
        session_id = data.get("session_id")
        print(f"\nChat rejected for session: {session_id}")
    
    def _handle_users_message(self, data):
        message_type = data.get("type")
        
        if message_type == "status_update":
            user_id = data.get("user_id")
            status = data.get("status")
            self.online_users[user_id] = status
        elif message_type == "users_list":
            users = data.get("users", {})
            self.online_users.update(users)
        elif message_type == "request_users_list":
            requesting_user = data.get("from")
            if requesting_user != self.user_id:
                response = {
                    "type": "status_update",
                    "user_id": self.user_id,
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                }
                self.client.publish(self.users_topic, json.dumps(response))
    
    def _handle_groups_message(self, data):
        message_type = data.get("type")
        
        if message_type == "group_update":
            group_name = data.get("group_name")
            group_info = data.get("group_info")
            self.groups[group_name] = group_info
        elif message_type == "groups_list":
            groups = data.get("groups", {})
            self.groups.update(groups)
    
    def _handle_chat_message(self, topic, data):
        from_user = data.get("from")
        message = data.get("message")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        print(f"[{timestamp}] {from_user}: {message}")
    
    def _handle_group_chat_message(self, topic, data):
        from_user = data.get("from")
        message = data.get("message")
        group_name = data.get("group_name")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        print(f"\n[{timestamp}] {group_name} - {from_user}: {message}")
    
    def connect(self):
        try:
            properties=mqtt.Properties(mqtt.PacketTypes.CONNECT)
            properties.SessionExpiryInterval=240
            self.client.connect_async(self.broker_host, self.broker_port, clean_start=True, properties=properties, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        self._store_subscribed_topics()
        self._announce_offline()
        self.client.loop_stop()
        self.client.disconnect()
    
    def _announce_online(self):
        message = {
            "type": "status_update",
            "user_id": self.user_id,
            "status": "online",
            "timestamp": datetime.now().isoformat()
        }
        self.client.publish(self.users_topic, json.dumps(message))
    
    def _announce_offline(self):
        message = {
            "type": "status_update",
            "user_id": self.user_id,
            "status": "offline",
            "timestamp": datetime.now().isoformat()
        }
        self.client.publish(self.users_topic, json.dumps(message))
    
    def _request_users_list(self):
        message = {
            "type": "request_users_list",
            "from": self.user_id
        }
        self.client.publish(self.users_topic, json.dumps(message))
        time.sleep(1)
    
    def _request_groups_list(self):
        message = {
            "type": "request_groups_list",
            "from": self.user_id
        }
        self.client.publish(self.groups_topic, json.dumps(message))
    
    def request_chat(self, target_user: str) -> str:
        session_id = f"{self.user_id}_{target_user}_{int(time.time())}"
        
        message = {
            "type": "chat_request",
            "from": self.user_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        target_control_topic = f"{target_user}_Control"
        self.client.publish(target_control_topic, json.dumps(message))

        print(f"\nRequest sent to user {target_user}")
        print(f"Session ID: {session_id}")
        
        return session_id
    
    def accept_chat(self, session_id: str):
        request = None
        for req in self.pending_requests:
            if req["session_id"] == session_id:
                request = req
                break
        
        if not request:
            print("Request not found")
            return
        
        chat_topic = session_id
        self.client.subscribe(chat_topic)
        self.active_sessions[session_id] = chat_topic
        
        from_user = request["from"]
        message = {
            "type": "chat_accept",
            "session_id": session_id,
            "chat_topic": chat_topic,
            "timestamp": datetime.now().isoformat()
        }
        
        target_control_topic = f"{from_user}_Control"
        self.client.publish(target_control_topic, json.dumps(message))
        
        self.pending_requests.remove(request)
        
        print(f"\nChat accepted with user {from_user}")
        print(f"Topic: {chat_topic}")
    
    def reject_chat(self, session_id: str):
        request = None
        for req in self.pending_requests:
            if req["session_id"] == session_id:
                request = req
                break
        
        if not request:
            print("Request not found")
            return
        
        from_user = request["from"]
        message = {
            "type": "chat_reject",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        target_control_topic = f"{from_user}_Control"
        self.client.publish(target_control_topic, json.dumps(message))
        
        self.pending_requests.remove(request)
        
        print(f"\nChat rejected with user {from_user}")
    
    def send_message(self, session_id: str, message: str):
        if session_id not in self.active_sessions:
            print("Session not found")
            return
        
        chat_topic = self.active_sessions[session_id]
        
        data = {
            "from": self.user_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(chat_topic, json.dumps(data))
    
    def create_group(self, group_name: str):
        group_info = {
            "name": group_name,
            "leader": self.user_id,
            "members": [self.user_id],
            "created_at": datetime.now().isoformat()
        }
        
        message = {
            "type": "group_update",
            "group_name": group_name,
            "group_info": group_info
        }
        
        self.client.publish(self.groups_topic, json.dumps(message))
        self.groups[group_name] = group_info
        
        group_topic = f"GROUP_{group_name}"
        self.client.subscribe(group_topic)
        
        print(f"Group '{group_name}' created successfully!")
    
    def join_group(self, group_name: str):
        if group_name not in self.groups:
            print("Group not found")
            return
        
        group_info = self.groups[group_name]
        leader = group_info["leader"]
        
        message = {
            "type": "group_request",
            "group_name": group_name,
            "from": self.user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        leader_control_topic = f"{leader}_Control"
        self.client.publish(leader_control_topic, json.dumps(message))
        
        print(f"Join request sent to group '{group_name}'")
    
    def accept_group_request(self, group_name: str, user_id: str):
        if group_name not in self.groups:
            print("Group not found")
            return
        
        group_info = self.groups[group_name]
        if group_info["leader"] != self.user_id:
            print("Only the leader can accept requests")
            return
        
        if user_id not in group_info["members"]:
            group_info["members"].append(user_id)
            
            message = {
                "type": "group_update",
                "group_name": group_name,
                "group_info": group_info
            }
            
            self.client.publish(self.groups_topic, json.dumps(message))
            self.groups[group_name] = group_info
            
            accept_message = {
                "type": "group_accept",
                "group_name": group_name,
                "timestamp": datetime.now().isoformat()
            }
            
            user_control_topic = f"{user_id}_Control"
            self.client.publish(user_control_topic, json.dumps(accept_message))
            
            print(f"{user_id} added to group '{group_name}'")
    
    def send_group_message(self, group_name: str, message: str):
        if group_name not in self.groups:
            print("Group not found")
            return
        
        group_info = self.groups[group_name]
        if self.user_id not in group_info["members"]:
            print("You are not a member of this group")
            return
        
        group_topic = f"GROUP_{group_name}"
        
        data = {
            "from": self.user_id,
            "group_name": group_name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(group_topic, json.dumps(data))
        print(f"Message sent to group '{group_name}': {message}")
    
    def get_online_users(self) -> Dict[str, str]:
        return {user: status for user, status in self.online_users.items() if status == "online"}
    
    def get_pending_requests(self) -> List[Dict]:
        return self.pending_requests.copy()
    
    def get_accepted_requests(self) -> List[Dict]:
        return self.accepted_requests.copy()
    
    def get_groups(self) -> Dict[str, Dict]:
        return self.groups.copy()
    
    def get_active_sessions(self) -> Dict[str, str]:
        return self.active_sessions.copy()
    
    def _store_subscribed_topics(self):
        subscribed_topics = []
        
        # Add active chat sessions
        for session_id, topic in self.active_sessions.items():
            subscribed_topics.append({
                "type": "chat",
                "session_id": session_id,
                "topic": topic
            })
        
        # Add group subscriptions
        for group_name, group_info in self.groups.items():
            if self.user_id in group_info.get("members", []):
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
            
            self.client.publish(self.control_topic, json.dumps(message), retain=True)
            print(f"Stored {len(subscribed_topics)} subscribed topics")
    
    def _handle_subscribed_topics(self, data):
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
                    self.client.subscribe(topic)
                    self.active_sessions[session_id] = topic
                    print(f"Resubscribed to chat: {session_id}")
            
            elif topic_type == "group":
                group_name = topic_info.get("group_name")
                topic = topic_info.get("topic")
                if group_name and topic:
                    self.client.subscribe(topic)
                    print(f"Resubscribed to group: {group_name}")