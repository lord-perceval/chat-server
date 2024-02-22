import tkinter as tk
from tkinter import scrolledtext
import socket
import threading

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

        self.connect_to_server()

    def connect_to_server(self):
        self.nickname = input("Choose a nickname: ")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '192.168.226.190'  # Update with server IP
        self.port = 55556
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(self.nickname.encode('utf-8'))

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def send_message(self):
        message = self.entry_field.get()
        if message:
            self.client_socket.send(message.encode('utf-8'))
            self.entry_field.delete(0, tk.END)

    def receive(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                # Prepend the client's nickname to the message
                message_with_nickname = f"{self.nickname}: {message}"
                self.display_message(message_with_nickname)
            except Exception as e:
                print("An error occurred:", e)
                self.client_socket.close()
                break

    def display_message(self, message):
    # Assuming the message format is 'nickname: message'
        try:
            nickname, msg = message.split(':',  1)
            self.chat_history.configure(state='normal')
            self.chat_history.insert('end', f"{nickname}: {msg}\n")
            self.chat_history.configure(state='disabled')
            self.chat_history.see('end')
        except ValueError:
        # If the message does not contain a colon, display it as is
            self.chat_history.configure(state='normal')
            self.chat_history.insert('end', message + '\n')
            self.chat_history.configure(state='disabled')
            self.chat_history.see('end')
def main():
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
