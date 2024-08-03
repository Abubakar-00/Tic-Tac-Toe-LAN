import getpass
import select
import socket
import hashlib
import time
import sys
import threading
import pyfiglet
import os

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
#SERVER = "192.168.170.1"
#SERVER = "10.96.0.78"
#SERVER = "10.1.29.181"
#SERVER = "10.1.23.48"
SERVER = "10.1.23.48"
ADDR = (SERVER,PORT)
MSG_RCV = None

last_message_time = time.time()
msg_lock = threading.Lock() # Initialize a lock
terminate_thread = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

# ali, umer
# ali123, umer123

def profile():
    os.system('cls')
    tic_tac_toe_printer()
    print("--------------------------------------------------------")
    send("PROFILE REQUEST")
    response = client.recv(2048).decode(FORMAT)
    response = response.split()
    username = response[1]
    join_date = response[2]

    #print("Personal Profile")
    print("\t\tUsername: ",username)
    print("\t\tJoining Date: ",join_date)
    
    #print("Total Games played:")
    #print("Win/s:")
    #print("Losse/s:")
    #print("Draw/s:")
    print("\n")
    input("Press any key to go back.....")

def display_lobby(response):
    users = response.strip().split(', ')
    users_in_lobby = [user for user in users if "InLobby" in user]
    users_in_game = [user for user in users if "InGame" in user]
    user_list = users_in_lobby + users_in_game

    ascii_banner = pyfiglet.figlet_format("LOBBY")
    print(ascii_banner)
    #print("\n{:^40}".format("Lobby"))
    print("-" * 40)
    print("{:<5} | {:<20} | {:<10}".format("NO.", "Username", "Status"))
    print("-" * 40)

    for i, user in enumerate(user_list, start=1):
        username, status = user.split('(')
        status = status.rstrip('),')
        if username.startswith("LOBBY "):
            username = username[6:]
        print("{:<5} | {:<20} | {:<10}".format(i, username, status))
    print("-" * 40)

##############      GAME CODE
def sum(a, b, c ):
    return a + b + c

def printBoard(xState, zState):
    zero = 'X' if xState[0] else ('O' if zState[0] else 0)
    one = 'X' if xState[1] else ('O' if zState[1] else 1)
    two = 'X' if xState[2] else ('O' if zState[2] else 2)
    three = 'X' if xState[3] else ('O' if zState[3] else 3)
    four = 'X' if xState[4] else ('O' if zState[4] else 4)
    five = 'X' if xState[5] else ('O' if zState[5] else 5)
    six = 'X' if xState[6] else ('O' if zState[6] else 6)
    seven = 'X' if xState[7] else ('O' if zState[7] else 7)
    eight = 'X' if xState[8] else ('O' if zState[8] else 8)
    tic_tac_toe_printer()
    print("--------------------------------------------------------")
    print(f"\n\t\t{zero} | {one} | {two} ")
    print(f"\t\t--|---|---")
    print(f"\t\t{three} | {four} | {five} ")
    print(f"\t\t--|---|---")
    print(f"\t\t{six} | {seven} | {eight} ")

def checkDraw(xState, zState):
    # Check if the board is full and no player has won
    return all(xState[i] or zState[i] for i in range(9))

def checkWin(xState, zState):
    wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for win in wins:
        if(sum(xState[win[0]], xState[win[1]], xState[win[2]]) == 3):
            print("\t\tX Won the match")
            return 1
        if(sum(zState[win[0]], zState[win[1]], zState[win[2]]) == 3):
            print("\t\tO Won the match")
            return 0
    return -1

def receive():
    try:
        # Set a timeout for the recv operation (e.g., 100 seconds)
        client.settimeout(100)
        
        # Receive the message from the server
        message = client.recv(2048).decode(FORMAT)
        #print(message)
        return message
    except socket.timeout:
        print("Timed out while waiting for a message from the server.")
        return None
    finally:
        # Reset the timeout to avoid affecting other parts of the code
        client.settimeout(None)

def game(checker_sender_receiver):
    xState = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    zState = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    turn = 1  # 1 for X and 0 for O

    while True:
        os.system('cls')
        printBoard(xState, zState)

        if checker_sender_receiver == 0:
            if turn == 1:
                print("\n\t\tX's turn. Waiting for X's move...")
                rcv_msg = int(receive().split()[1])  # Receive X's move from the server
                value = rcv_msg
                xState[value] = 1

            else:
                value = None
                while value is None or not (0 <= value <= 8 and xState[value] == 0 and zState[value] == 0):
                    try:
                        value = int(input("\n\t\tPlease enter a value: "))
                    except ValueError:
                        print("\n\t\tInvalid input. Please enter a single number between 0 and 8.")
                        value = None
                        continue

                zState[value] = 1
                message = f"MOVE {value}"
                send(message)  # Send O's move to the server
                
        else:
            if turn == 1:
                value = None
                while value is None or not (0 <= value <= 8 and xState[value] == 0 and zState[value] == 0):
                    try:
                        value = int(input("\n\t\tPlease enter a value: "))
                    except ValueError:
                        print("\n\t\tInvalid input. Please enter a single number between 0 and 8.")
                        value = None
                        continue

                xState[value] = 1
                message = f"MOVE {value}"
                send(message)  # Send X's move to the server
                

            else:
                print("\n\t\tO's turn. Waiting for O's move...")
                rcv_msg = int(receive().split()[1])  # Receive O's move from the server
                value = rcv_msg
                
                zState[value] = 1
                #print(f"Received O's move: {value}")

        cwin = checkWin(xState, zState)
        if cwin != -1:
            print("\t\tMatch over")
            input("\n\t\tPress any key to go back........")
            os.system('cls')
            break
        
        if checkDraw(xState, zState):
            print("\t\tIt's a draw!")
            input("\n\t\tPress any key to go back........")
            break


        turn = 1 - turn  # Alternate turns

############## 

def request_lobby_list():
    send("LOBBY MSG")

def send_request(response, user_selected):
    # unpack response
    users = response.strip().split(', ')
    users_in_lobby = [user for user in users if "InLobby" in user]
    users_in_game = [user for user in users if "InGame" in user]
    user_list = users_in_lobby
    
    selected_users = []
    for i, user in enumerate(user_list, start=1):
        username, status = user.split('(')
        status = status.rstrip('),')
        if username.startswith("LOBBY "):
            username = username[6:]
        selected_users.append((i, username.strip(), status.strip()))

    # Check if user_selected matches any tuple in selected_users
    selected_username = None
    for i, username, status in selected_users:
        if i == user_selected:
            if status == "InLobby":
                selected_username = username
                st = f"GAME_REQUEST {selected_username}"
                send(st) # Request sended here
                print(f"Request Sent to: {selected_username}")
                return 1
            elif status == "InGame":
                print("Player in Game, Can't send Request")
                return 0
    
    # If no match is found
    print("Player not in list!!!")
    return 0

def receive_messages(stop_event,pause_event):
    global MSG_RCV

    while not stop_event.is_set():
        if not pause_event.is_set():
            try:
                # Set a timeout for the recv operation
                if not stop_event.is_set():
                    client.settimeout(1)
                    message = client.recv(2048).decode(FORMAT)

                    if message:                
                        with msg_lock: # Acquire the lock before updating the shared resource (MSG_RCV)
                            MSG_RCV = message
                        time.sleep(10)  # Pause receiving messages for 10 seconds
                        with msg_lock: # Acquire the lock before updating the shared resource (MSG_RCV)
                            MSG_RCV = None  # Reset MSG_RCV to None after 10 seconds

            except socket.timeout: # Handle the timeout exception (no data received)
                with msg_lock:
                    MSG_RCV = None

            finally: # Check if the socket is still open before setting the timeout
                if not client._closed:
                    client.settimeout(1)

            time.sleep(0.3)  # Sleep for 1 second to avoid busy-waiting

def Lobby():
    os.system('cls')
    send("ENTER_LOBBY MSG")
    request_lobby_list()
    response = client.recv(2048).decode(FORMAT)
    display_lobby(response)

    time.sleep(0.3)
    global terminate_thread
    stop_event = threading.Event()
    pause_event = threading.Event()

    receive_thread = threading.Thread(target=receive_messages, args=(stop_event,pause_event))
    receive_thread.start()


    receive_caller = None # Will save request for 10 sec after time it will be again none
    
    refresh_timer = 5
    start_time = time.time()

    flag = True
    while flag:
        elapsed_time = time.time() - start_time
        remaining_time = max(0, refresh_timer - elapsed_time)

        # Acquire the lock before accessing the shared resource (MSG_RCV)
        with msg_lock:
            receive_caller = MSG_RCV

        print("\n")
        print(f"\nNext lobby refresh available in {int(remaining_time)} seconds.")

        print("1. Refresh Lobby List & Check Any Request")
        print("2. Request to Play")
        
        if receive_caller != None:
            print(receive_caller) # request to play print
            print("3. To accept request")
            print("0. Back to Main Menu")
        else:
            print("0. Back to Main Menu")
            print("\nNO Request Received")
            print("\n")

        try:
            choice = int(input("Enter Choice: "))
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue

        if choice == 1 and elapsed_time >= refresh_timer:
            os.system('cls')
            request_lobby_list()
            pause_event.set()  # Set the event to pause the thread
            response = client.recv(2048).decode(FORMAT)
            pause_event.clear()
            display_lobby(response)
            time.sleep(0.3)
            start_time = time.time()  # Reset the timer after refreshing

        
        elif choice == 2:  # For send request
            flag_inside_send = True
            pause_event.set()  # Set the event to pause the thread
            while flag_inside_send:
                print("\n0. Back To Lobby")
                try:
                    user_choice = int(input("Enter Player No: "))  # Used a different variable name to avoid conflict
                except ValueError:
                    print("Invalid input. Please enter a valid Player No.")
                    continue

                request_sender = send_request(response, user_choice)
                if request_sender == 1:
                    start_time = time.time()

                    flag_inside_send_2 = True
                    while flag_inside_send_2:
                        readable, _, _ = select.select([client], [], [], 1)  # Check for readability every 1 second

                        if readable:
                            message = client.recv(2048).decode(FORMAT)
                            if message:
                                print("Request Accepted!!!")
                                wait = 1
                                send("ENTER_GAME MSG")
                                game(wait)
                                send("LEAVE_GAME MSG")
                                #break
                                flag_inside_send = flag_inside_send_2= False
                        elif time.time() - start_time > 12: 
                            print("No Response from the receiver!!")
                            break
                elif user_choice == 0:
                    flag_inside_send = False  # Back to the main menu
                else:
                    print("Player Doesn't exist on Lobby List!!!\n")
            pause_event.clear()


        elif choice == 3: # Accepted request
            pause_event.set()  # Set the event to pause the thread
            if receive_caller != None:
                # Receiver will send a acceptence msg # "MESSAGE ali: GAME_REQUEST umer" # Grab ali
                requester = receive_caller.split()[1].split(":")
                #print("The one who send the request: ",requester)
                send(f"REQUEST_ACCEPTED {requester}")
                print("REQUEST ACCEPTED")
                print("\n")
                make_move = 0
                send("ENTER_GAME MSG")
                game(make_move)
                send("LEAVE_GAME MSG")
            else:
                print("\nNO Request Received")
            pause_event.clear()
                
        elif choice == 0:
            send("LEAVE_LOBBY MSG")
            flag = False
            terminate_thread = True
            stop_event.set()

        else:
            print("Invalid choice. Please try again.")
    stop_event.set()
    receive_thread.join()

def login():
    os.system('cls')
    print("\n\n\t\t      LOGIN SECTION")
    print("--------------------------------------------------------")
    flag = True
    while flag:
        username = input("\t\tEnter the username: ").strip().replace(" ", "")
        password = getpass.getpass("\t\tEnter the password: ").strip().replace(" ", "")

        hashed_password = hash_password(password)
        login_msg = f"LOGIN {username} {hashed_password}"
        send(login_msg)

        response = client.recv(2048).decode(FORMAT)
        print(response)

        if response == "Login successful!":
            flag_inside_1 = True
            while flag_inside_1:
                os.system('cls')
                tic_tac_toe_printer()
                print("--------------------------------------------------------")
                print("\t\t1. Open Profile")
                print("\t\t2. Open Lobby")
                print("\t\t0. Logout Account")
                print("--------------------------------------------------------")

                try:
                    choice = int(input("\t\tEnter Choice: "))
                except ValueError:
                    print("\t\tInvalid input. Please enter a valid number.")
                    continue
                if choice == 1:
                    profile()

                elif choice == 2: # -> further game section
                    Lobby()

                elif choice == 0:
                    send("LOGOUT")
                    print("\t\tLogged out successfully.")
                    flag = flag_inside_1 = False
                else:
                    print("\t\tEnter the right choice")

        else:
            try:
                choice = int(input("\n\t\tPress 0 to login again or Press any other key to go back to the main menu: "))
            except ValueError:
                print("\t\tInvalid input. Please enter a valid number.")
                continue

            if choice == 0:
                continue
            else:
                flag = False

def signup():
    os.system('cls')
    flag = True
    while flag:
        print("\n\n\t\t      SIGNUP SECTION")
        print("--------------------------------------------------------")
        print("\n**Spacing will be removed both in username and password automatically!")
        username = input("\n\t\tEnter the username: ").strip().replace(" ", "")
        password = input("\t\tEnter the password: ").strip().replace(" ", "")

        hashed_password = hash_password(password)
        signup_msg = f"SIGNUP {username} {hashed_password}"

        send(signup_msg)

        response = client.recv(2048).decode(FORMAT)
        print("\n")
        print(response)

        if response == "Signup successful!":
            input("\t\tPress any key to go back..........")
            flag = False
        elif response == "\t\t*Username already exists. Please choose a different one.":
            flag_inside = True
            while flag_inside:
                try:
                    choice = int(input("\n\t\tPress 0 to Signup again or Press any other no. to go back to the main menu: "))
                except ValueError:
                    print("\t\tInvalid input. Please enter a valid number.")
                    continue

                if choice == 0:
                    continue
                else:
                    flag = flag_inside = False


def send(msg):
    message = msg.encode(FORMAT)
    msg_lenght = len(message)
    send_lenght = str(msg_lenght).encode(FORMAT)
    send_lenght += b' ' * (HEADER-len(send_lenght))
    client.send(send_lenght)
    client.send(message)

def tic_tac_toe_printer():
    ascii_banner = pyfiglet.figlet_format("TIC TAC TOE")
    print(ascii_banner)

def client_driver():
    flag = True
    while flag:
        
        tic_tac_toe_printer()
        print("--------------------------------------------------------")
        print("\t\t1. Login")
        print("\t\t2. Signup")
        print("\t\t0. Close")
        print("--------------------------------------------------------")

        try:
            choice = int(input("\t\tEnter Choice: "))

            if choice == 1:
                login()
            elif choice == 2:
                signup()
            elif choice == 0:
                send(DISCONNECT_MESSAGE)
                print("\t\tDisconnected From the server")
                flag = False
            else:
                print("\t\tWrong Choice. Please enter a valid number.")
            os.system('cls')

        except ValueError:
            print("\t\tInvalid input. Please enter a valid number.")

        except KeyboardInterrupt:
            send(DISCONNECT_MESSAGE)
            print("\n\t\tDisconnected from the server")
            flag = False
            sys.exit()

try:
    client.connect(ADDR)
    initial_msg = client.recv(2048).decode(FORMAT)
    print(initial_msg)

    client_driver()
    
except ConnectionRefusedError:
    print("Unable to connect to the server. Please make sure the server is running.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the client socket in any case
    client.close()