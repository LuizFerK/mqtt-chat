"""
Menu handlers for different UI operations.
"""
from typing import List, Dict, Any
from ..utils.helpers import (
    clear_screen, get_user_input, wait_for_enter, 
    display_list_with_numbers, get_choice_from_list,
    format_group_info, format_user_status
)


class MenuHandlers:
    """Handles different menu operations."""
    
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
    
    def list_online_users(self):
        """Display list of online users."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nOnline users:")
        
        online_users = self.mqtt_client.get_online_users()
        
        if not online_users:
            print("No online users found")
        else:
            for user_id, status in online_users.items():
                if user_id != self.mqtt_client.user_id:
                    print(format_user_status(user_id, status))
        
        wait_for_enter()
    
    def request_chat(self):
        """Handle chat request."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nRequest chat:")
        
        online_users = self.mqtt_client.get_online_users()
        available_users = [user for user in online_users.keys() if user != self.mqtt_client.user_id]
        
        if not available_users:
            print("No online users available for chat")
            wait_for_enter()
            return
        
        display_list_with_numbers(available_users, "Available users")
        
        try:
            choice = get_choice_from_list(available_users, "\nChoose user number")
            target_user = available_users[choice]
            session_id = self.mqtt_client.request_chat(target_user)
        except (ValueError, IndexError):
            print("Invalid option")
        
        wait_for_enter()
    
    def manage_chat_requests(self):
        """Handle chat request management."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        pending_requests = self.mqtt_client.get_pending_requests()
        
        if not pending_requests:
            print("No pending requests")
            wait_for_enter()
            return
        
        print("\nPending requests:")
        for i, request in enumerate(pending_requests, 1):
            print(f"{i}. From user: {request['from']}")
            print(f"   Session: {request['session_id']}")
            print(f"   Time: {request['timestamp']}")
            print()
        
        try:
            choice = int(get_user_input("Choose request number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(pending_requests):
                request = pending_requests[choice - 1]
                session_id = request['session_id']
                from_user = request['from']
                
                print(f"\nRequest from user {from_user}")
                print(f"Session: {session_id}")
                
                action = get_user_input("Accept? (y/n)")
                if action.lower() in ['y', 'yes']:
                    self.mqtt_client.accept_chat(session_id)
                else:
                    self.mqtt_client.reject_chat(session_id)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        wait_for_enter()
    
    def active_chat(self):
        """Handle active chat sessions."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nActive chat:")
        
        active_sessions = self.mqtt_client.get_active_sessions()
        
        if not active_sessions:
            print("No active chat sessions")
            wait_for_enter()
            return
        
        for i, (session_id, topic) in enumerate(active_sessions.items(), 1):
            print(f"{i}. Session: {session_id}")
            print(f"   Topic: {topic}")
            print()
        
        try:
            choice = int(get_user_input("Choose session number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(active_sessions):
                session_id = list(active_sessions.keys())[choice - 1]
                self._chat_interface(session_id)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        wait_for_enter()
    
    def _chat_interface(self, session_id: str):
        """Handle chat interface."""
        print(f"\nChat - Session: {session_id}")
        print("Type 'exit' to go back to menu")
        print("Message: ", end="")
        
        while True:
            message = input().strip()
            if message.lower() in ['exit', 'quit']:
                break
            
            if message.strip():
                self.mqtt_client.send_message(session_id, message)
    
    def show_debug_info(self):
        """Display debug information."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nDebug information:")
        
        print("Users and status:")
        for user, status in self.mqtt_client.online_users.items():
            print(f"  {user}: {status}")
        
        print("\nPending requests:")
        pending = self.mqtt_client.get_pending_requests()
        if pending:
            for req in pending:
                print(f"  From: {req['from']} - Session: {req['session_id']}")
        else:
            print("  No pending requests")
        
        print("\nAccepted requests:")
        accepted = self.mqtt_client.get_accepted_requests()
        if accepted:
            for req in accepted:
                print(f"  Session: {req['session_id']} - Topic: {req['chat_topic']}")
        else:
            print("  No accepted requests")
        
        print("\nActive sessions:")
        sessions = self.mqtt_client.get_active_sessions()
        if sessions:
            for session_id, topic in sessions.items():
                print(f"  {session_id} -> {topic}")
        else:
            print("  No active sessions")
        
        print("\nGroups:")
        groups = self.mqtt_client.get_groups()
        if groups:
            for name, info in groups.items():
                print(f"  {name}")
                print(f"     Leader: {info['leader']}")
                print(f"     Members: {len(info['members'])}")
        else:
            print("  No groups")
        
        wait_for_enter()
