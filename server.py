import threading
import socket
import tkinter as tk
from tkinter import messagebox

host = '192.168.43.234'  # local host
port =  55556

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,  1)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat'.encode('ascii'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"connected with {str(address)}")

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        print(f'nickname of client is {nickname}')
        broadcast(f'{nickname} joined the chat'.encode('ascii'))
        client.send("connected to the server".encode('ascii'))

        thread = threading.Thread(
            target=handle,
            args=(client,)
        )
        thread.start()

def start_server():
    server_thread = threading.Thread(target=receive)
    server_thread.start()

def stop_server():
    # You'll need to implement a way to stop the server thread
    # This could involve setting a flag that the server checks to see if it should stop
    pass

def start_gui():
    # Create the main window
    root = tk.Tk()
    root.title("Chat Server Control")

    # Create a start button
    start_button = tk.Button(root, text="Start Server", command=start_server)
    start_button.pack()

    # Create a stop button
    stop_button = tk.Button(root, text="Stop Server", command=stop_server)
    stop_button.pack()

    # Run the main loop
    root.mainloop()

# Call the start_gui function to start the GUI
start_gui()