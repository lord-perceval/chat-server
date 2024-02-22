import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import random

class ChatClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("Chat Client")

        self.chat_history = scrolledtext.ScrolledText(master, state='disabled')
        self.chat_history.pack(expand=True, fill='both')

        self.entry_field = tk.Entry(master)
        self.entry_field.pack(expand=True, fill='x')

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack()

        self.user_color = self.generate_random_color()  # Unique color for the user
        self.connect_to_server()

    def connect_to_server(self):
        self.nickname = input("Choose a nickname: ")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '192.168.1.101'  # Update with server IP
        self.port = 55556
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(self.nickname.encode('utf-8'))

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def send_message(self):
        message = self.entry_field.get()
        if message:
        # Prefix the message with the nickname
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
            sender, msg = message.split(':', 1)

            # Use a unique color for each user in the GUI
            user_color = self.generate_random_color()
            self.chat_history.tag_configure(user_color, foreground=user_color)
            
            self.chat_history.configure(state='normal')
            self.chat_history.insert('end', f"{sender}: {msg}\n", user_color)
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

def main():
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
