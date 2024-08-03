import socket
import hashlib
import sqlite3
import threading
from datetime import datetime

HEADER = 64
PORT = 5050
#SERVER = socket.gethostbyname(socket.gethostname())
#SERVER = "192.168.170.1"
SERVER = "10.1.23.48"
ADDR = (SERVER,PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def hash_password(password):
    # Hash the password using a secure hash function (e.g., SHA-256)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def update_user_status(username, ip_address, port_no, status, crsr):
    # Update the user status in the UserStatus table
    crsr.execute("INSERT OR REPLACE INTO UserStatus (username, ip_address, port_no, status) VALUES (?, ?, ?, ?)",
                 (username, ip_address, port_no, status))

def login(conn, msg, crsr, conn_local, addr):
    # Extract username and password from the message
    _, username, password = msg.split()

    # Check if the username is already logged in
    crsr.execute("SELECT * FROM UserStatus WHERE username=? AND status='Online'", (username,))
    logged_in_user = crsr.fetchone()

    if logged_in_user:
        conn.send(f"User '{username}' is already logged in. Please choose a different username.".encode(FORMAT))
        return None  # Return None if the user is already logged in

    # Hash the received password for comparison with the stored hash
    hashed_password = hash_password(password)

    # Check if the username and password match an entry in the database
    crsr.execute("SELECT * FROM Users WHERE username=? AND password=?", (username, hashed_password))
    user_data = crsr.fetchone()

    if user_data:
        update_user_status(username, addr[0], addr[1], 'Online', crsr)
        conn_local.commit()
        conn.send("Login successful!".encode(FORMAT))
        return username  # Return the username after successful login
    else:
        conn.send("Invalid username or password.".encode(FORMAT))
        return None  # Return None if login is unsuccessful


def signup(conn, msg, crsr, conn_local):
    _, new_username, new_password = msg.split()

    # Hash the received password before storing it in the database
    hashed_password = hash_password(new_password)

    # Check if the username already exists in the database
    crsr.execute("SELECT * FROM Users WHERE username=?", (new_username,))
    existing_user = crsr.fetchone()

    if not existing_user:
        # Insert the new user into the database
        join_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        crsr.execute("INSERT INTO Users (username, password, joining_date) VALUES (?, ?, ?)",
                     (new_username, hashed_password, join_date))
        conn_local.commit()
        conn.send("Signup successful!".encode(FORMAT))
    else:
        conn.send("Username already exists. Please choose a different one.".encode(FORMAT))

def logout(username, crsr):
    try:
        crsr.execute("DELETE FROM UserStatus WHERE username=?", (username,))
    except sqlite3.Error as e:
        print(f"Error deleting entry for {username} from UserStatus table: {e}")

def user_data(crsr, username):
    crsr.execute("SELECT username, joining_date FROM Users WHERE username = ?", (username,))
    return crsr.fetchall()

def send_user_data(conn, profile_data):
    profile_msg = "PROFILE "
    for username, joining_date in profile_data:
        profile_msg += f"{username} {joining_date}"
    #print(profile_msg)
    conn.send(profile_msg.encode(FORMAT))

def get_users(crsr, username):
    crsr.execute("SELECT username, status FROM UserStatus WHERE username != ?", (username,))
    return crsr.fetchall()    

def send_lobby_users(conn, lobby_users):
    lobby_msg = "LOBBY "
    for user, status in lobby_users:
        lobby_msg += f"{user}({status}), "
    conn.send(lobby_msg.encode(FORMAT) + b'\n')

def game_request(sender,msg, connected_clients):
    receiver = msg.split()[1]
    target_conn = connected_clients.get(receiver)
    if target_conn:
        # Forward the message to the target client
        target_conn.send(f"MESSAGE {sender}: {msg}".encode(FORMAT))
        return receiver # Opponent
    else:
        print(f"User {receiver} is not currently connected.")
        return None

def game_accept(sender,msg, connected_clients):
    parts = msg.split()
    receiver = next((part for part in parts[1:] if part), None)  
    receiver=receiver.strip('[').strip(',')[1:-1]
    # Check if the receiver is in connected_clients
    if receiver in connected_clients:
        target_conn = connected_clients[receiver]
        # Forward the message to the target client
        target_conn.send(f"MESSAGE Request Accepted by {sender}".encode(FORMAT))
        return receiver # opponent
    else:
        print(f"User {receiver} is not currently connected.")
        return None

def move_sender(oppo, msg, connected_clients):
    #print(oppo)
    target_conn = connected_clients[oppo]
    target_conn.send(msg.encode(FORMAT))

def handle_client(conn, addr,connected_clients):
    print(f"[NEW CONNECTION] {addr} connected.")

    # Inform the client about the connection
    conn.send("Connected to the server.\n".encode(FORMAT))
    
    conn_local = sqlite3.connect("User.db")
    crsr = conn_local.cursor()

    connected = True
    username = None
    opponent = None

    try:
        while connected:
            # Receive the message length first
            msg_length = conn.recv(HEADER).decode(FORMAT)
            
            if not msg_length:
                break

            # Check if the received message is the login, signup, logout command ,.....
            if str(msg_length).startswith('LOGIN') or str(msg_length).startswith('SIGNUP') or str(msg_length).startswith('LOGOUT') or str(msg_length).startswith('LOBBY') or str(msg_length).startswith('ENTER_LOBBY') or str(msg_length).startswith('LEAVE_LOBBY') or str(msg_length).startswith('GAME_REQUEST') or str(msg_length).startswith('REQUEST_ACCEPTED') or str(msg_length).startswith('ENTER_GAME') or str(msg_length).startswith('LEAVE_GAME') or str(msg_length).startswith('MOVE') or str(msg_length).startswith('PROFILE'):
                msg = msg_length
            else:
                # Receive the actual message using the determined length
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)

            if msg == DISCONNECT_MESSAGE:
                print(f"[DISCONNECTED] {addr[0]}")
                if username:
                    logout(username, crsr)
                    conn_local.commit()
                connected = False

            elif msg.startswith('LOGIN'):
                username = login(conn, msg, crsr, conn_local, addr)
                connected_clients[username] = conn
            
            elif msg.startswith('LOGOUT'):
                if username:
                    logout(username, crsr)
                    conn_local.commit()
                    del connected_clients[username]
                    username = None
                else:
                    conn.send("Not logged in. No action taken.".encode(FORMAT))
                
            elif msg.startswith('SIGNUP'):
                signup(conn, msg, crsr, conn_local)
            
            elif msg.startswith('PROFILE'):
                profile_data = user_data(crsr, username)
                #print("Fetch: ",profile_data)
                send_user_data(conn,profile_data)
            
            elif msg.startswith('LOBBY'):
                # Display the lobby users to the client
                lobby_users = get_users(crsr, username)
                send_lobby_users(conn, lobby_users)

            elif msg.startswith('ENTER_LOBBY'):
                update_user_status(username, addr[0], addr[1], 'InLobby', crsr)
                conn_local.commit()

            elif msg.startswith('LEAVE_LOBBY'):
                update_user_status(username, addr[0], addr[1], 'Online', crsr)
                conn_local.commit()

            elif msg.startswith('GAME_REQUEST'):
                opponent = game_request(username, msg, connected_clients)

            elif msg.startswith('REQUEST_ACCEPTED'):
                opponent = game_accept(username, msg, connected_clients)
            
            elif msg.startswith('MOVE'):
                move_sender(opponent, msg, connected_clients)

            elif msg.startswith('ENTER_GAME'):
                update_user_status(username, addr[0], addr[1], 'InGame', crsr)
                conn_local.commit()
            
            elif msg.startswith('LEAVE_GAME'):
                update_user_status(username, addr[0], addr[1], 'InLobby', crsr)
                conn_local.commit()
            else:
                conn.send("Invalid command.".encode(FORMAT))
    
    except ConnectionResetError:
        print(f"[DISCONNECTED] {addr[0]} (Forcefully closed by Client)")
        if username:
            logout(username, crsr)
            conn_local.commit()
            del connected_clients[username]
    finally:
        conn_local.commit()
        crsr.close()
        conn_local.close()
        conn.close()

def start():
    connected_clients = {}
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        connected_clients[addr] = conn
        thread = threading.Thread(target=handle_client, args=(conn, addr, connected_clients))
        thread.start()

print("[Starting] server is starting...")
start()