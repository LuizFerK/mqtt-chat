import os
import sys
from typing import Dict, List
from mqtt_client import MQTTClient


class ChatUI:
    def __init__(self, mqtt_client: MQTTClient):
        self.mqtt_client = mqtt_client
        self.running = True
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
    
    def print_menu(self):
        print("\nMenu:")
        print("1. List online users")
        print("2. Request chat")
        print("3. Manage chat requests")
        print("4. Active chat")
        print("5. Manage groups")
        print("6. Debug information")
        print("7. Exit")
    
    def print_groups_menu(self):
        print("\nGroups:")
        print("1. List groups")
        print("2. Create new group")
        print("3. Request group join")
        print("4. Manage group requests")
        print("5. Group chat")
        print("6. Back to menu")
    
    def get_user_input(self, prompt: str) -> str:
        return input(f"{prompt}: ").strip()
    
    def wait_for_enter(self):
        input("\nPress Enter to continue...")
    
    def list_online_users(self):
        self.clear_screen()
        self.print_header()
        
        print("\nOnline users:")
        
        online_users = self.mqtt_client.get_online_users()
        
        if not online_users:
            print("No online users found")
        else:
            for user_id, status in online_users.items():
                if user_id != self.mqtt_client.user_id:
                    print(f"{user_id} - {status}")
        
        self.wait_for_enter()
    
    def request_chat(self):
        self.clear_screen()
        self.print_header()
        
        print("\nRequest chat:")
        
        online_users = self.mqtt_client.get_online_users()
        available_users = [user for user in online_users.keys() if user != self.mqtt_client.user_id]
        
        if not available_users:
            print("No online users available for chat")
            self.wait_for_enter()
            return
        
        print("Available users:")
        for i, user in enumerate(available_users, 1):
            print(f"{i}. {user}")
        
        try:
            choice = int(self.get_user_input("\nChoose user number"))
            if 1 <= choice <= len(available_users):
                target_user = available_users[choice - 1]
                session_id = self.mqtt_client.request_chat(target_user)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        self.wait_for_enter()
    
    def manage_chat_requests(self):
        self.clear_screen()
        self.print_header()
        
        pending_requests = self.mqtt_client.get_pending_requests()
        
        if not pending_requests:
            print("No pending requests")
            self.wait_for_enter()
            return
        
        print("\nPending requests:")
        for i, request in enumerate(pending_requests, 1):
            print(f"{i}. From user: {request['from']}")
            print(f"   Session: {request['session_id']}")
            print(f"   Time: {request['timestamp']}")
            print()
        
        try:
            choice = int(self.get_user_input("Choose request number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(pending_requests):
                request = pending_requests[choice - 1]
                session_id = request['session_id']
                from_user = request['from']
                
                print(f"\nRequest from user {from_user}")
                print(f"Session: {session_id}")
                
                action = self.get_user_input("Accept? (y/n)")
                if action.lower() in ['y', 'yes']:
                    self.mqtt_client.accept_chat(session_id)
                else:
                    self.mqtt_client.reject_chat(session_id)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        self.wait_for_enter()
    
    def active_chat(self):
        self.clear_screen()
        self.print_header()
        
        print("\nActive chat:")
        
        active_sessions = self.mqtt_client.get_active_sessions()
        
        if not active_sessions:
            print("No active chat sessions")
            self.wait_for_enter()
            return
        
        for i, (session_id, topic) in enumerate(active_sessions.items(), 1):
            print(f"{i}. Session: {session_id}")
            print(f"   Topic: {topic}")
            print()
        
        try:
            choice = int(self.get_user_input("Choose session number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(active_sessions):
                session_id = list(active_sessions.keys())[choice - 1]
                self._chat_interface(session_id)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        self.wait_for_enter()
    
    def _chat_interface(self, session_id: str):
        print(f"\nChat - Session: {session_id}")
        print("Type 'exit' to go back to menu")
        print("Message: ", end="")
        
        while True:
            message = input().strip()
            if message.lower() in ['exit', 'quit']:
                break
            
            if message.strip():
                self.mqtt_client.send_message(session_id, message)
    
    def list_groups(self):
        self.clear_screen()
        self.print_header()
        
        print("\nGroups:")
        
        groups = self.mqtt_client.get_groups()
        
        if not groups:
            print("No groups found")
        else:
            for group_name, group_info in groups.items():
                print(f"{group_name}")
                print(f"   Leader: {group_info['leader']}")
                print(f"   Members: {', '.join(group_info['members'])}")
                print(f"   Created: {group_info['created_at']}")
                print()
        
        self.wait_for_enter()
    
    def create_group(self):
        self.clear_screen()
        self.print_header()
        
        print("\nCreate new group:")
        
        group_name = self.get_user_input("Group name")
        
        if not group_name:
            print("Group name cannot be empty")
            self.wait_for_enter()
            return
        
        if group_name in self.mqtt_client.get_groups():
            print("Group already exists")
            self.wait_for_enter()
            return
        
        self.mqtt_client.create_group(group_name)
        self.wait_for_enter()
    
    def join_group(self):
        self.clear_screen()
        self.print_header()
        
        print("\nRequest group join:")
        
        groups = self.mqtt_client.get_groups()
        
        if not groups:
            print("No groups available")
            self.wait_for_enter()
            return
        
        # Filter out groups where user is already a member
        available_groups = []
        for group_name, group_info in groups.items():
            if (self.mqtt_client.user_id not in group_info["members"] and 
                group_info["leader"] != self.mqtt_client.user_id):
                available_groups.append(group_name)
        
        if not available_groups:
            print("No groups available to join (you are already a member of all groups)")
            self.wait_for_enter()
            return
        
        print("Available groups:")
        for i, group_name in enumerate(available_groups, 1):
            print(f"{i}. {group_name}")
        
        try:
            choice = int(self.get_user_input("Choose group number"))
            if 1 <= choice <= len(available_groups):
                group_name = available_groups[choice - 1]
                self.mqtt_client.join_group(group_name)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        self.wait_for_enter()
    
    def manage_group_requests(self):
        self.clear_screen()
        self.print_header()
        
        print("\nManage group requests:")
        
        # Get groups where current user is the leader
        groups = self.mqtt_client.get_groups()
        leader_groups = []
        
        for group_name, group_info in groups.items():
            if group_info['leader'] == self.mqtt_client.user_id:
                leader_groups.append(group_name)
        
        if not leader_groups:
            print("You are not a leader of any group")
            self.wait_for_enter()
            return
        
        print("Your groups (as leader):")
        for i, group_name in enumerate(leader_groups, 1):
            print(f"{i}. {group_name}")
        
        try:
            choice = int(self.get_user_input("Choose group number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(leader_groups):
                group_name = leader_groups[choice - 1]
                self._handle_group_requests_for_group(group_name)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        self.wait_for_enter()
    
    def _handle_group_requests_for_group(self, group_name: str):
        self.clear_screen()
        self.print_header()
        
        print(f"\nGroup requests for '{group_name}':")
        
        # Get pending requests for this group
        group_requests = []
        for request in self.mqtt_client.pending_requests:
            if (request.get('group_name') == group_name and 
                request.get('from') != self.mqtt_client.user_id):
                group_requests.append(request)
        
        if not group_requests:
            print("No pending requests for this group")
            self.wait_for_enter()
            return
        
        print("Pending requests:")
        for i, request in enumerate(group_requests, 1):
            print(f"{i}. {request['from']} - {request['timestamp']}")
        
        try:
            choice = int(self.get_user_input("Choose request number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(group_requests):
                request = group_requests[choice - 1]
                self._process_group_request(group_name, request)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
    
    def _process_group_request(self, group_name: str, request: dict):
        from_user = request['from']
        
        print(f"\nRequest from: {from_user}")
        print(f"Group: {group_name}")
        
        action = self.get_user_input("Accept? (y/n)")
        if action.lower() in ['y', 'yes']:
            self.mqtt_client.accept_group_request(group_name, from_user)
            # Remove from pending requests
            self.mqtt_client.pending_requests = [
                req for req in self.mqtt_client.pending_requests 
                if not (req.get('from') == from_user and req.get('group_name') == group_name)
            ]
            print(f"Accepted {from_user} into group '{group_name}'")
        else:
            self.mqtt_client.reject_group_request(group_name, from_user)
            # Remove from pending requests
            self.mqtt_client.pending_requests = [
                req for req in self.mqtt_client.pending_requests 
                if not (req.get('from') == from_user and req.get('group_name') == group_name)
            ]
            print(f"Rejected {from_user} from group '{group_name}'")
    
    def group_chat(self):
        self.clear_screen()
        self.print_header()
        
        print("\nGroup chat:")
        
        groups = self.mqtt_client.get_groups()
        user_groups = []
        
        for group_name, group_info in groups.items():
            if self.mqtt_client.user_id in group_info['members']:
                user_groups.append(group_name)
        
        if not user_groups:
            print("You are not a member of any group")
            self.wait_for_enter()
            return
        
        print("Your groups:")
        for i, group_name in enumerate(user_groups, 1):
            print(f"{i}. {group_name}")
        
        try:
            choice = int(self.get_user_input("Choose group number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(user_groups):
                group_name = user_groups[choice - 1]
                self._group_chat_interface(group_name)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        self.wait_for_enter()
    
    def _group_chat_interface(self, group_name: str):
        print(f"\nGroup Chat: {group_name}")
        print("Type 'exit' to go back to menu")
        print("Message: ", end="")
        
        while True:
            message = input().strip()
            if message.lower() in ['exit', 'quit']:
                break
            
            if message.strip():
                self.mqtt_client.send_group_message(group_name, message)
    
    def show_debug_info(self):
        self.clear_screen()
        self.print_header()
        
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
        
        self.wait_for_enter()
    
    def run(self):
        while self.running:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            try:
                choice = int(self.get_user_input("Choose an option"))
                
                if choice == 1:
                    self.list_online_users()
                elif choice == 2:
                    self.request_chat()
                elif choice == 3:
                    self.manage_chat_requests()
                elif choice == 4:
                    self.active_chat()
                elif choice == 5:
                    self._handle_groups_menu()
                elif choice == 6:
                    self.show_debug_info()
                elif choice == 7:
                    self.running = False
                else:
                    print("Invalid option")
                    self.wait_for_enter()
                    
            except ValueError:
                print("Please enter a valid number")
                self.wait_for_enter()
            except KeyboardInterrupt:
                print("\n\nShutting down application...")
                self.running = False
        
        self.mqtt_client.disconnect()
        print("XOXO bye bye!")
    
    def _handle_groups_menu(self):
        while True:
            self.clear_screen()
            self.print_header()
            self.print_groups_menu()
            
            try:
                choice = int(self.get_user_input("Choose an option:"))
                
                if choice == 1:
                    self.list_groups()
                elif choice == 2:
                    self.create_group()
                elif choice == 3:
                    self.join_group()
                elif choice == 4:
                    self.manage_group_requests()
                elif choice == 5:
                    self.group_chat()
                elif choice == 6:
                    break
                else:
                    print("Invalid option")
                    self.wait_for_enter()
                    
            except ValueError:
                print("Please enter a valid number")
                self.wait_for_enter()
