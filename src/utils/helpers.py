"""
Utility functions for the MQTT Chat application.
"""
import os
import time
from typing import List, Dict, Any
from datetime import datetime


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def get_user_input(prompt: str) -> str:
    """Get user input with a prompt."""
    return input(f"{prompt}: ").strip()


def wait_for_enter():
    """Wait for user to press Enter."""
    input("\nPress Enter to continue...")


def generate_session_id(user_id: str, target_user: str) -> str:
    """Generate a unique session ID."""
    return f"{user_id}_{target_user}_{int(time.time())}"


def format_timestamp(timestamp: datetime) -> str:
    """Format a datetime object as a readable string."""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def validate_user_id(user_id: str) -> bool:
    """Validate that a user ID is not empty and contains valid characters."""
    if not user_id or not user_id.strip():
        return False
    # Basic validation - no spaces, special characters that might cause issues
    return not any(char in user_id for char in [' ', '\t', '\n', '\r'])


def display_list_with_numbers(items: List[str], title: str = "Items") -> None:
    """Display a list of items with numbers for selection."""
    if not items:
        print(f"No {title.lower()} available")
        return
    
    print(f"{title}:")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item}")


def get_choice_from_list(items: List[str], prompt: str = "Choose an option") -> int:
    """Get user choice from a numbered list."""
    while True:
        try:
            choice = int(get_user_input(prompt))
            if 1 <= choice <= len(items):
                return choice - 1  # Return 0-based index
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def format_group_info(group_name: str, group_info: Dict[str, Any]) -> str:
    """Format group information for display."""
    return f"{group_name}\n   Leader: {group_info['leader']}\n   Members: {', '.join(group_info['members'])}\n   Created: {group_info['created_at']}"


def format_user_status(user_id: str, status: str) -> str:
    """Format user status for display."""
    return f"{user_id} - {status}"
