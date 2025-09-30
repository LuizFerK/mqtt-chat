from typing import Dict, List


def print_header(user_id: str):
  print("MQTT Chat")
  print(f"User: {user_id}")


def print_menu():
  print("\nMenu:")
  print("1. List users")
  print("2. Request chat")
  print("3. Manage chat requests")
  print("4. Active chat")
  print("5. Manage groups")
  print("6. Debug information")
  print("7. Exit")


def print_groups_menu():
  print("\nGroups:")
  print("1. List groups")
  print("2. Create new group")
  print("3. Request group join")
  print("4. Manage group requests")
  print("5. Group chat")
  print("6. Back to menu")


def print_users(users: Dict[str, str], current_user: str):
  print("\nUsers:")
  
  if not users:
    print("No users found")
  else:
    for user_id, status in users.items():
      if user_id != current_user:
        print(f"{user_id} - {status}")


def print_available_users(available_users: List[str]):
  print("Available users:")
  for i, user in enumerate(available_users, 1):
    print(f"{i}. {user}")


def print_pending_requests(pending_requests: List[Dict]):
  print("\nPending requests:")
  for i, request in enumerate(pending_requests, 1):
    print(f"{i}. From user: {request['from']}")
    print(f"   Session: {request['session_id']}")
    print(f"   Time: {request['timestamp']}")
    print()


def print_active_sessions(active_sessions: Dict[str, str]):
  print("\nActive chat:")
  
  if not active_sessions:
    print("No active chat sessions")
  else:
    for i, (session_id, topic) in enumerate(active_sessions.items(), 1):
      print(f"{i}. Session: {session_id}")
      print(f"   Topic: {topic}")
      print()


def print_groups(groups: Dict[str, Dict]):
  print("\nGroups:")
  
  if not groups:
    print("No groups found")
  else:
    for group_name, group_info in groups.items():
      print(f"{group_name}")
      if isinstance(group_info, dict):
        print(f"   Leader: {group_info['leader']}")
        print(f"   Members: {', '.join(group_info['members'])}")
        print(f"   Created: {group_info['created_at']}")
      else:
        print(f"   Info: {group_info}")
      print()


def print_debug_info(mqtt_client):
  print("\nDebug information:")
  
  print("Users and status:")
  for user, status in mqtt_client.users.items():
    print(f"  {user}: {status}")
  
  print("\nPending requests:")
  pending = mqtt_client.get_pending_requests()
  if pending:
    for req in pending:
      print(f"  From: {req['from']} - Session: {req['session_id']}")
  else:
    print("  No pending requests")
  
  print("\nAccepted requests:")
  accepted = mqtt_client.get_accepted_requests()
  if accepted:
    for req in accepted:
      print(f"  Session: {req['session_id']} - Topic: {req['chat_topic']}")
  else:
    print("  No accepted requests")
  
  print("\nActive sessions:")
  sessions = mqtt_client.get_active_sessions()
  if sessions:
    for session_id, topic in sessions.items():
      print(f"  {session_id} -> {topic}")
  else:
    print("  No active sessions")
  
  print("\nGroups:")
  groups = mqtt_client.get_groups()
  if groups:
    for name, info in groups.items():
      print(f"  {name}")
      print(f"     Leader: {info['leader']}")
      print(f"     Members: {len(info['members'])}")
  else:
    print("  No groups")