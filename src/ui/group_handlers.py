"""
Group-related UI handlers.
"""
from typing import List, Dict, Any
from ..utils.helpers import (
    clear_screen, get_user_input, wait_for_enter, 
    display_list_with_numbers, get_choice_from_list,
    format_group_info
)


class GroupHandlers:
    """Handles group-related UI operations."""
    
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
    
    def list_groups(self):
        """Display list of groups."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nGroups:")
        
        groups = self.mqtt_client.get_groups()
        
        if not groups:
            print("No groups found")
        else:
            for group_name, group_info in groups.items():
                print(format_group_info(group_name, group_info))
        
        wait_for_enter()
    
    def create_group(self):
        """Handle group creation."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nCreate new group:")
        
        group_name = get_user_input("Group name")
        
        if not group_name:
            print("Group name cannot be empty")
            wait_for_enter()
            return
        
        if group_name in self.mqtt_client.get_groups():
            print("Group already exists")
            wait_for_enter()
            return
        
        self.mqtt_client.create_group(group_name)
        wait_for_enter()
    
    def join_group(self):
        """Handle group join request."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nRequest group join:")
        
        groups = self.mqtt_client.get_groups()
        
        if not groups:
            print("No groups available")
            wait_for_enter()
            return
        
        # Filter out groups where user is already a member
        available_groups = []
        for group_name, group_info in groups.items():
            if (self.mqtt_client.user_id not in group_info["members"] and 
                group_info["leader"] != self.mqtt_client.user_id):
                available_groups.append(group_name)
        
        if not available_groups:
            print("No groups available to join (you are already a member of all groups)")
            wait_for_enter()
            return
        
        display_list_with_numbers(available_groups, "Available groups")
        
        try:
            choice = get_choice_from_list(available_groups, "Choose group number")
            group_name = available_groups[choice]
            self.mqtt_client.join_group(group_name)
        except (ValueError, IndexError):
            print("Invalid option")
        
        wait_for_enter()
    
    def manage_group_requests(self):
        """Handle group request management."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nManage group requests:")
        
        # Get groups where current user is the leader
        groups = self.mqtt_client.get_groups()
        leader_groups = []
        
        for group_name, group_info in groups.items():
            if group_info['leader'] == self.mqtt_client.user_id:
                leader_groups.append(group_name)
        
        if not leader_groups:
            print("You are not a leader of any group")
            wait_for_enter()
            return
        
        display_list_with_numbers(leader_groups, "Your groups (as leader)")
        
        try:
            choice = int(get_user_input("Choose group number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(leader_groups):
                group_name = leader_groups[choice - 1]
                self._handle_group_requests_for_group(group_name)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        wait_for_enter()
    
    def _handle_group_requests_for_group(self, group_name: str):
        """Handle group requests for a specific group."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print(f"\nGroup requests for '{group_name}':")
        
        # Get pending requests for this group
        group_requests = []
        for request in self.mqtt_client.pending_requests:
            if (request.get('group_name') == group_name and 
                request.get('from') != self.mqtt_client.user_id):
                group_requests.append(request)
        
        if not group_requests:
            print("No pending requests for this group")
            wait_for_enter()
            return
        
        display_list_with_numbers(
            [f"{req['from']} - {req['timestamp']}" for req in group_requests],
            "Pending requests"
        )
        
        try:
            choice = int(get_user_input("Choose request number (0 to go back)"))
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
        """Process a group request (accept/reject)."""
        from_user = request['from']
        
        print(f"\nRequest from: {from_user}")
        print(f"Group: {group_name}")
        
        action = get_user_input("Accept? (y/n)")
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
        """Handle group chat."""
        clear_screen()
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
        
        print("\nGroup chat:")
        
        groups = self.mqtt_client.get_groups()
        user_groups = []
        
        for group_name, group_info in groups.items():
            if self.mqtt_client.user_id in group_info['members']:
                user_groups.append(group_name)
        
        if not user_groups:
            print("You are not a member of any group")
            wait_for_enter()
            return
        
        display_list_with_numbers(user_groups, "Your groups")
        
        try:
            choice = int(get_user_input("Choose group number (0 to go back)"))
            if choice == 0:
                return
            elif 1 <= choice <= len(user_groups):
                group_name = user_groups[choice - 1]
                self._group_chat_interface(group_name)
            else:
                print("Invalid option")
        except ValueError:
            print("Please enter a valid number")
        
        wait_for_enter()
    
    def _group_chat_interface(self, group_name: str):
        """Handle group chat interface."""
        print(f"\nGroup Chat: {group_name}")
        print("Type 'exit' to go back to menu")
        print("Message: ", end="")
        
        while True:
            message = input().strip()
            if message.lower() in ['exit', 'quit']:
                break
            
            if message.strip():
                self.mqtt_client.send_group_message(group_name, message)
