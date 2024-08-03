# Tic-Tac-Toe Online

## Introduction

Tic-Tac-Toe Online is a networked multiplayer version of the classic Tic-Tac-Toe game. The application consists of a server that handles user authentication, game state, and communication, and a client that allows users to log in, sign up, view profiles, join the lobby, and play the game.

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Dependencies](#dependencies)
6. [Configuration](#configuration)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)
9. [Contributors](#contributors)
10. [License](#license)

## Features

- User authentication (sign up, log in, log out)
- Profile management
- Real-time lobby with user status
- Tic-Tac-Toe gameplay with real-time updates
- User-friendly command-line interface

## Installation

### Prerequisites

Ensure you have Python 3.x installed on your system.

### Steps

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/tic-tac-toe-online.git
    cd tic-tac-toe-online
    ```

2. Install required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up the database:
    ```sh
    python setup_database.py
    ```

## Usage

### Running the Server

1. Navigate to the project directory.
2. Run the server script:
    ```sh
    python server.py
    ```

### Running the Client

1. Navigate to the project directory.
2. Run the client script:
    ```sh
    python client.py
    ```

## Dependencies

- Python 3.x
- `socket` - for networking
- `hashlib` - for hashing passwords
- `sqlite3` - for database management
- `threading` - for handling multiple connections
- `datetime` - for timestamping
- `pyfiglet` - for ASCII art in the command-line interface

## Configuration

### Server Configuration

- `HEADER`: The header size for messages.
- `PORT`: The port on which the server listens.
- `SERVER`: The server IP address.
- `FORMAT`: The format for encoding and decoding messages.
- `DISCONNECT_MESSAGE`: The message to signal disconnection.

### Client Configuration

- `HEADER`: The header size for messages.
- `PORT`: The port on which the server is listening.
- `SERVER`: The server IP address.
- `FORMAT`: The format for encoding and decoding messages.
- `DISCONNECT_MESSAGE`: The message to signal disconnection.

## Examples

### Example Usage

1. Start the server:
    ```sh
    python server.py
    ```

2. Start the client:
    ```sh
    python client.py
    ```

3. Follow the on-screen prompts to sign up, log in, join the lobby, and start playing Tic-Tac-Toe.

## Troubleshooting

### Common Issues

- **Server Not Running**: Ensure the server is running and the IP address/port is correct.
- **Database Errors**: Ensure the database is properly set up using `setup_database.py`.
- **Connection Issues**: Check firewall settings and ensure the correct IP and port are used.

## Contributors

- [Your Name](https://github.com/yourusername)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
