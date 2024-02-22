import threading
import socket
import queue
import tkinter as tk
from tkinter import scrolledtext

# Your existing server code
host = '192.168.1.101'
port =   55556

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,   1)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

# Create a queue for messages
message_queue = queue.Queue()

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
            broadcast(f'[nickname] left the chat'.encode('ascii'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        message_queue.put(f"connected with {str(address)}")
        
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)
        
        message_queue.put(f'nickname of client is {nickname}')
        broadcast(f'{nickname} joined the chat'.encode('ascii'))
        client.send("connected to the server".encode('ascii'))
        
        thread = threading.Thread(
            target=handle,
            args=(client,)
        )
        thread.start()

# GUI code
def start_server():
    server_thread = threading.Thread(target=receive)
    server_thread.start()
    message_queue.put("Server is listening")

def stop_server():
    # Implement a way to stop the server
    pass

def create_gui():
    root = tk.Tk()
    root.title("Chat Server")

    output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
    output_text.pack(padx=10, pady=10)

    start_button = tk.Button(root, text="Start Server", command=start_server)
    start_button.pack(pady=5)

    stop_button = tk.Button(root, text="Stop Server", command=stop_server)
    stop_button.pack(pady=5)

    # Function to update the GUI with messages from the queue
    def update_gui():
        while not message_queue.empty():
            message = message_queue.get()
            output_text.insert(tk.END, message + '\n')
        root.after(100, update_gui)  # Check the queue every  100ms

    update_gui()  # Start updating the GUI

    root.mainloop()

if __name__ == "__main__":
    create_gui()