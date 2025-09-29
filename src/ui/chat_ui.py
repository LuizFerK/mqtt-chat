"""
Main Chat UI class with organized menu system.
"""
from typing import Dict, List, Any
from ..utils.helpers import clear_screen, get_user_input, wait_for_enter
from .menu_handlers import MenuHandlers
from .group_handlers import GroupHandlers


class ChatUI:
    """Main Chat UI with organized menu system."""
    
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.running = True
        self.menu_handlers = MenuHandlers(mqtt_client)
        self.group_handlers = GroupHandlers(mqtt_client)
    
    def print_header(self):
        """Print the application header."""
        print("MQTT Chat")
        print(f"User: {self.mqtt_client.user_id}")
    
    def print_main_menu(self):
        """Print the main menu options."""
        print("\nMenu:")
        print("1. List online users")
        print("2. Request chat")
        print("3. Manage chat requests")
        print("4. Active chat")
        print("5. Manage groups")
        print("6. Debug information")
        print("7. Exit")
    
    def print_groups_menu(self):
        """Print the groups submenu."""
        print("\nGroups:")
        print("1. List groups")
        print("2. Create new group")
        print("3. Request group join")
        print("4. Manage group requests")
        print("5. Group chat")
        print("6. Back to menu")
    
    def handle_main_menu(self, choice: int):
        """Handle main menu selection."""
        if choice == 1:
            self.menu_handlers.list_online_users()
        elif choice == 2:
            self.menu_handlers.request_chat()
        elif choice == 3:
            self.menu_handlers.manage_chat_requests()
        elif choice == 4:
            self.menu_handlers.active_chat()
        elif choice == 5:
            self._handle_groups_menu()
        elif choice == 6:
            self.menu_handlers.show_debug_info()
        elif choice == 7:
            self.running = False
        else:
            print("Invalid option")
            wait_for_enter()
    
    def handle_groups_menu(self, choice: int):
        """Handle groups menu selection."""
        if choice == 1:
            self.group_handlers.list_groups()
        elif choice == 2:
            self.group_handlers.create_group()
        elif choice == 3:
            self.group_handlers.join_group()
        elif choice == 4:
            self.group_handlers.manage_group_requests()
        elif choice == 5:
            self.group_handlers.group_chat()
        elif choice == 6:
            return False  # Go back to main menu
        else:
            print("Invalid option")
            wait_for_enter()
        return True  # Stay in groups menu
    
    def _handle_groups_menu(self):
        """Handle the groups submenu loop."""
        while True:
            clear_screen()
            self.print_header()
            self.print_groups_menu()
            
            try:
                choice = int(get_user_input("Choose an option:"))
                
                if not self.handle_groups_menu(choice):
                    break  # Go back to main menu
                    
            except ValueError:
                print("Please enter a valid number")
                wait_for_enter()
    
    def run(self):
        """Main application loop."""
        while self.running:
            clear_screen()
            self.print_header()
            self.print_main_menu()
            
            try:
                choice = int(get_user_input("Choose an option"))
                self.handle_main_menu(choice)
                    
            except ValueError:
                print("Please enter a valid number")
                wait_for_enter()
            except KeyboardInterrupt:
                print("\n\nShutting down application...")
                self.running = False
        
        self.mqtt_client.disconnect()
        print("XOXO bye bye!")
