#!/usr/bin/env python3

import os
import sys
import time
from src.core.mqtt_client import MQTTClient
from src.ui.chat_ui import ChatUI
from src.utils.helpers import validate_user_id


def main():
    """Main application entry point."""
    os.system('clear' if os.name == 'posix' else 'cls')
    print("Starting MQTT Chat...")
    
    # Get user ID
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        user_id = input("Enter your user ID: ").strip()
        if not user_id:
            print("User ID cannot be empty")
            return
    
    # Validate user ID
    if not validate_user_id(user_id):
        print("Invalid user ID. Please use only letters, numbers, and underscores.")
        return
    
    # Get broker configuration
    broker_host = input("Broker host (localhost): ").strip() or "localhost"
    broker_port = input("Broker port (1883): ").strip() or "1883"
    
    try:
        broker_port = int(broker_port)
    except ValueError:
        print("Invalid port, using 1883")
        broker_port = 1883
    
    print(f"\nConnecting to broker {broker_host}:{broker_port}...")
    
    # Initialize MQTT client
    mqtt_client = MQTTClient(user_id, broker_host, broker_port)
    
    if not mqtt_client.connect():
        print("Failed to connect to MQTT broker")
        print("Make sure the broker is running:")
        print("   docker-compose up -d")
        return
    
    # Initialize and run UI
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