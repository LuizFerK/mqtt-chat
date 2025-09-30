#!/usr/bin/env python3

import sys
from src.client import MQTTClient
from src.ui import ChatUI
from src.helpers import (
  clear_screen, get_user_input, get_user_id_from_args, get_broker_config
)


def main():
  clear_screen()
  print("Starting MQTT Chat...")
  
  user_id = get_user_id_from_args()
  if not user_id:
    user_id = get_user_input("Enter your user ID")
    if not user_id:
      print("User ID cannot be empty")
      return
  
  broker_host, broker_port = get_broker_config()
  
  print(f"\nConnecting to broker {broker_host}:{broker_port}...")
  
  mqtt_client = MQTTClient(user_id, broker_host, broker_port)
  
  if not mqtt_client.connect():
    print("Failed to connect to MQTT broker")
    print("Make sure the broker is running:")
    print("   docker-compose up -d")
    return
  
  ui = ChatUI(mqtt_client)
  
  try:
    ui.run()
  except KeyboardInterrupt:
    print("\n\nShutting down application...")
    mqtt_client.disconnect()
  except Exception as e:
    print(f"\nUnexpected error: {e}")
    mqtt_client.disconnect()


if __name__ == "__main__":
  main()