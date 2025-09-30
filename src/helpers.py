import os
import sys
from typing import Optional


def clear_screen():
  os.system('clear' if os.name == 'posix' else 'cls')


def get_user_input(prompt: str) -> str:
  return input(f"{prompt}: ").strip()


def wait_for_enter():
  input("\nPress Enter to continue...")


def get_user_id_from_args() -> Optional[str]:
  if len(sys.argv) > 1:
    return sys.argv[1]
  return None


def get_broker_config() -> tuple[str, int]:
  broker_host = get_user_input("Broker host (localhost)") or "localhost"
  broker_port_str = get_user_input("Broker port (1883)") or "1883"
  
  try:
    broker_port = int(broker_port_str)
  except ValueError:
    print("Invalid port, using 1883")
    broker_port = 1883
  
  return broker_host, broker_port