import threading
import socket
import queue
import tkinter as tk
from tkinter import scrolledtext
import os
import ssl  


host = '192.168.126.190'  
port = 55556

server_running = True
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

clients = []
nicknames = []


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('example.crt', 'example.key')  

server_ssl = ssl_context.wrap_socket(server, server_side=True)



message_queue = queue.Queue()

def handle_disconnect(client):
    if client in clients:
        clients.remove(client)
        client.close()
        nickname = nicknames[clients.index(client)]
        nicknames.remove(nickname)
        broadcast(f'{nickname} left the chat'.encode('ascii'))

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except socket.error:
            
            handle_disconnect(client)

files_folder = 'FILES'
os.makedirs(files_folder, exist_ok=True)

def handle(client):
    global files_folder

    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            if message == '/list_files':
                print("Received /list_files command") 
                files_list = os.listdir(files_folder)
                print(f"Files in {files_folder}: {files_list}") 
                files_str = "\n".join(files_list)
                client.send(files_str.encode('utf-8'))
            elif message.startswith('FILE:'):
                
                file_data = client.recv(1024)
                file_name, file_content = file_data.split(b'\n', 1)
                file_name = file_name.decode('utf-8')

                broadcast(f'{nicknames[clients.index(client)]} sent a file: {file_name}'.encode('ascii'))

               
                file_path = os.path.join(files_folder, file_name)
                with open(file_path, 'wb') as file:
                    file.write(file_content)

                broadcast(f'{nicknames[clients.index(client)]}\'s file {file_name} received'.encode('ascii'))
            elif message.startswith('/download:'):
                
                try:
                    file_number = int(message.split(':', 1)[1])
                    files_list = os.listdir(files_folder)
                    if 0 < file_number <= len(files_list):
                        file_name = files_list[file_number - 1]
                        file_path = os.path.join(files_folder, file_name)
                        with open(file_path, 'rb') as file:
                            file_data = file.read()
                        client.send(file_data)
                    else:
                        client.send("Invalid file number.".encode('utf-8'))
                except ValueError:
                    client.send("Invalid file number.".encode('utf-8'))
            else:
                
                broadcast(message.encode('utf-8'))
        except socket.error as e:
            print("An error occurred:", e)
            handle_disconnect(client)
            break



def receive():
    while server_running:
        try:
            client, address = server_ssl.accept()
            message_queue.put(f"connected with {str(address)}")

            client.send('YOU HAVE ENTERED THE CHAT SERVER -'.encode('ascii'))
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
        except socket.error as e:
            print("An error occurred:", e)


def start_server():
    global server_running
    server_running = True
    server_thread = threading.Thread(target=receive)
    server_thread.start()
    message_queue.put("Server is listening")

def stop_server():
    global server_running
    server_running = False
    server_ssl.close()  
    message_queue.put("Server stopped")

def create_gui():
    root = tk.Tk()
    root.title("Chat Server")

    output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
    output_text.pack(padx=10, pady=10)

    start_button = tk.Button(root, text="Start Server", command=start_server)
    start_button.pack(pady=5)

    stop_button = tk.Button(root, text="Stop Server", command=stop_server)
    stop_button.pack(pady=5)

    
    def update_gui():
        while not message_queue.empty():
            message = message_queue.get()
            output_text.insert(tk.END, message + '\n')
        root.after(100, update_gui)  

    update_gui()  

    root.mainloop()

if __name__ == "__main__":
    create_gui()