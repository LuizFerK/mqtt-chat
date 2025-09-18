# MQTT Chat Application

A chat application based on the MQTT protocol developed in Python.

## Features

- **One-to-one communication**: Private chat between users
- **Group communication**: Group chat with leader system
- **Status management**: Online/offline users
- **Control system**: Control topics for each user
- **Session negotiation**: Chat request/acceptance system
- **User-friendly interface**: Text menu with all options

## Architecture

### Components
- **MQTT Broker**: Eclipse Mosquitto (via Docker)
- **MQTT Client**: paho-mqtt
- **Interface**: Terminal/text
- **Language**: Python 3

### MQTT Topics

#### Control Topics
- `USERS`: User status (online/offline)
- `GROUPS`: Group information
- `{ID}_Control`: Control topic for each user

#### Chat Topics
- `{ID1}_{ID2}_{timestamp}`: Individual chat between two users
- `GROUP_{name}`: Group chat

## Prerequisites

- Python 3.7+
- Docker and Docker Compose
- Linux (as specified)

## Installation

### Option 1: Using Nix (Recommended)

1. **Clone or download the project**
2. **Enter the development environment**:
   ```bash
   nix develop
   ```

3. **Start everything at once**:
   ```bash
   nix run .#start-all
   ```

### Option 2: Manual Installation

1. **Clone or download the project**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the MQTT broker**:
   ```bash
   docker-compose up -d
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

**Note**: Option 1 (Nix) is recommended as it manages all dependencies automatically.

## Available Nix Commands

With the Nix flake, you have access to the following commands:

```bash
# Broker management
nix run .#start-broker        # Start MQTT broker
nix run .#stop-broker         # Stop MQTT broker
nix run .#restart-broker      # Restart MQTT broker
nix run .#logs                # View broker logs
nix run .#status              # View broker status

# Development
nix run .#install-deps        # Check dependencies (managed by Nix)
nix run .#run-app             # Run application
nix run .#start-all           # Start everything (broker + app)
nix run .#cleanup             # Clean containers and volumes
```

### Development Environment

To enter the development environment with all available tools:

```bash
nix develop
```

This provides:
- Python 3.11
- paho-mqtt (MQTT library)
- Docker and Docker Compose
- All necessary tools

## How to Use

### Starting the Application

1. Run `python main.py`
2. Enter your user ID (must be unique)
3. Configure the broker host and port (default: localhost:1883)

### Main Menu

The application offers an interactive menu with the following options:

1. **List online users**: View all connected users
2. **Request chat**: Start a chat with another user
3. **Manage requests**: Accept/reject chat requests
4. **Active chat**: Access ongoing conversations
5. **Manage groups**: Create groups and participate in group chats
6. **Debug information**: View technical system details
7. **Exit**: Close the application

### Individual Chat Flow

1. **Request**: User A requests chat with User B
2. **Notification**: User B receives notification on topic `B_Control`
3. **Acceptance/Rejection**: User B accepts or rejects the request
4. **Topic creation**: If accepted, topic `A_B_timestamp` is created
5. **Chat**: Both users can exchange messages

### Group Flow

1. **Creation**: User creates group and becomes leader
2. **Join request**: Other users request participation
3. **Approval**: Leader approves or rejects requests
4. **Group chat**: Members can exchange messages on topic `GROUP_{name}`

## Configuration

### Docker Compose

The `docker-compose.yml` file configures:
- **Eclipse Mosquitto** on port 1883 (MQTT) and 9001 (WebSockets)
- **Configuration**: `mosquitto.conf` with anonymous connections enabled

### Environment Variables

- `BROKER_HOST`: MQTT broker host (default: localhost)
- `BROKER_PORT`: MQTT broker port (default: 1883)

## Project Structure

```
mqtt-chat/
├── main.py              # Main application
├── mqtt_client.py       # MQTT client and business logic
├── chat_ui.py          # User interface
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Broker configuration
├── mosquitto.conf      # Mosquitto configuration
├── flake.nix           # Nix flake for management
├── description.txt     # Project specification
└── README.md           # This file
```

## Debugging

The application includes a debug menu that shows:
- List of users and their status
- Pending chat requests
- Accepted requests
- Active sessions
- Detailed group information

## Security

- **Anonymous connections**: Enabled for simplicity (not recommended for production)
- **Unique IDs**: Each user must have a unique ID
- **Validation**: Application validates user input

## Limitations

- No user authentication
- No message persistence
- No message encryption
- Text-only interface

## Usage Example

### Using Nix (Recommended)

```bash
# Start everything at once
nix run .#start-all

# Or step by step:
nix run .#start-broker    # Start broker
nix run .#run-app         # Run app (in another terminal)
```

### Using Manual Installation

```bash
# Terminal 1 - User Alice
python main.py alice

# Terminal 2 - User Bob  
python main.py bob

# Alice requests chat with Bob
# Bob accepts the request
# Both can exchange messages
```

## Contributing

This is an academic project developed according to specification. For improvements:

1. Fork the project
2. Create a branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is developed for academic purposes.
