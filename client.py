import tkinter as tk
from tkinter import scrolledtext, simpledialog
import socket
import threading
import random
import datetime

class ChatClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("Chat Client")

        self.chat_history = scrolledtext.ScrolledText(master, state='disabled')
        self.chat_history.pack(expand=True, fill='both')

        self.entry_field = tk.Entry(master)
        self.entry_field.pack(expand=True, fill='x')
        self.entry_field.bind('<Return>', lambda event: self.send_message())  # Bind Enter key to send_message

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack()

        self.user_colors = {}  # Dictionary to map nicknames to colors
        self.connect_to_server()

    # The rest of your class methods remain unchanged
    def connect_to_server(self):
        try:
            self.nickname = simpledialog.askstring("Nickname", "Choose a nickname:")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.host = '192.168.1.101'  # Update with server IP
            self.port = 55556
            self.client_socket.connect((self.host, self.port))
            self.client_socket.send(self.nickname.encode('utf-8'))

            self.receive_thread = threading.Thread(target=self.receive)
            self.receive_thread.start()
        except Exception as e:
            print("An error occurred during connection:", e)
            self.display_message("Failed to connect to the server. Please try again.")

    def on_closing(self):
        try:
            self.client_socket.close()
        except:
            pass  # Ignore errors when closing the socket
        self.master.destroy()

    def send_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_name = file_path.split('/')[-1]  # Extract file name from the path
                file_data = f'FILE:{file_name}\n'.encode('utf-8') + file.read()
                self.client_socket.send(file_data)
        except Exception as e:
            print("An error occurred while sending the file:", e)

    def send_message(self):
        message = self.entry_field.get()

        if message.startswith('/file'):
            # If the message starts with '/file', treat it as a file path
            file_path = message.split(' ', 1)[1]
            self.send_file(file_path)
        elif message:
            # Otherwise, treat it as a regular message
            full_message = f"{self.nickname}: {message}"
            self.client_socket.send(full_message.encode('utf-8'))
        
        self.entry_field.delete(0, tk.END)

    def receive(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.display_message(message)
            except Exception as e:
                print("An error occurred:", e)
                self.client_socket.close()
                break


    def display_message(self, message):
        try:
            sender, msg = message.split(':',   1)

            # Check if the sender's color is already known
            if sender not in self.user_colors:
                # Generate a new color for the user
                user_color = self.generate_random_color()
                self.user_colors[sender] = user_color
                self.chat_history.tag_configure(user_color, foreground=user_color)

            # Use the color associated with the sender
            user_color = self.user_colors[sender]
            self.chat_history.configure(state='normal')
            # Insert a timestamp before each message
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.chat_history.insert('end', f"{timestamp} {sender}: {msg}\n", user_color)
            self.chat_history.tag_add(user_color, 'end-2c', 'end-1c')  # Apply the tag to the inserted text
            self.chat_history.configure(state='disabled')
            self.chat_history.see('end')
        except ValueError:
            # If the message does not contain a colon, display it as is
            self.chat_history.configure(state='normal')
            self.chat_history.insert('end', message + '\n')
            self.chat_history.configure(state='disabled')
            self.chat_history.see('end')

    def generate_random_color(self):
        return '#%02x%02x%02x' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def on_closing(self):
        self.client_socket.close()
        self.master.destroy()


def main():
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Bind the closing event
    root.mainloop()

if __name__ == "__main__":
    main()