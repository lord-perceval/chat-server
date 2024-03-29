import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, ttk
import socket
import threading
import random
import datetime
import os
import ssl

class ChatClientGUI:
    
    def __init__(self, master):
        self.master = master
        master.title("Chat Client")

        self.chat_history = scrolledtext.ScrolledText(master, state='disabled')
        self.chat_history.pack(expand=True, fill='both')

        self.entry_field = tk.Entry(master)
        self.entry_field.pack(expand=True, fill='x')
        self.entry_field.bind('<Return>', lambda event: self.send_message()) # Bind Enter key to send_message

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack()

        # Add a button for requesting the file list
        self.list_files_button = tk.Button(master, text="List Files", command=self.request_file_list)
        self.list_files_button.pack()

        # Add an emoji button
        self.emoji_button = tk.Button(master, text="😊", command=self.show_emoji_picker)
        self.emoji_button.pack()

        self.user_colors = {} # Dictionary to map nicknames to colors
        self.nickname = simpledialog.askstring("Nickname", "Enter your nickname:")
        self.connect_to_server()
        

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.host = '192.168.126.190'  # Update with your server IP or domain
            self.port = 55556

            # Create an SSL context
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # Wrap the client socket with the SSL context
            self.client_socket = ssl_context.wrap_socket(self.client_socket, server_hostname=self.host)
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
                file_name = os.path.basename(file_path)  # Extract file name from the path
                file_data = f'FILE:{file_name}\n'.encode('utf-8') + file.read()
                self.client_socket.send(file_data)
        except Exception as e:
            print("An error occurred while sending the file:", e)
            self.display_message("Failed to send the file. Please try again.")

    def send_message(self):
        message = self.entry_field.get()

        if message.startswith('/file'):
            file_path = message.split(' ', 1)[1]
            self.send_file(file_path)
        elif message.startswith('/download'):
            try:
                # Check if the message contains a space and has a second element
                parts = message.split(' ', 1)
                if len(parts) > 1:
                    file_number = int(parts[1])
                    self.client_socket.send(f'/download:{file_number}'.encode('utf-8'))
                else:
                    self.display_message("Invalid command format. Please use '/download: <number>'")
            except ValueError:
                self.display_message("Invalid file number. Please enter a valid number.")
        elif message:
            full_message = f"{self.nickname}: {message}"
            self.client_socket.send(full_message.encode('utf-8'))
            self.display_message(full_message) # Display the message locally

        self.entry_field.delete(0, tk.END)
               
        
    
    def receive(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith('/download:'):
                    file_data = self.client_socket.recv(1024) # Assuming the file data is sent immediately after the command
                    file_path = 'downloaded_file.txt' # You might want to generate a unique file name or use the file name sent by the server
                    with open(file_path, 'wb') as file:
                        file.write(file_data)
                    self.display_message(f"File downloaded successfully to {file_path}")
                elif not message.startswith(self.nickname + ':'):
                    self.display_message(message)
            except Exception as e:
                print("An error occurred:", e)
                self.client_socket.close()
                break
                
    
    def request_file_list(self):
        try:
            self.client_socket.send('/list_files'.encode('utf-8'))
            files_list = self.client_socket.recv(1024).decode('utf-8')
            # Split the received string into a list of file names
            files = files_list.split('\n')
            # Enumerate the list and format each file name with a number
            formatted_files = [f"{i+1}. {file}" for i, file in enumerate(files) if file]
            # Join the formatted file names with newlines and display the message
            self.display_message("Files in 'FILES' folder:\n" + "\n".join(formatted_files))
        except Exception as e:
            print("An error occurred while requesting the file list:", e)
            self.display_message("Failed to retrieve the file list. Please try again.")
    
    def display_message(self, message):
        self.master.after(0, self._display_message, message)  # Schedule GUI update in the main thread

    def _display_message(self, message):
        try:
            sender, msg = message.split(':', 1)

            if sender not in self.user_colors:
                user_color = self.generate_random_color()
                self.user_colors[sender] = user_color
                self.chat_history.tag_configure(user_color, foreground=user_color)

            user_color = self.user_colors[sender]
            self.chat_history.configure(state='normal')
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Center the timestamp and display the message
            centered_timestamp = f"{timestamp:^{len(msg) + len(sender) + 2}}"

            # Insert the centered timestamp
            self.chat_history.insert('end', f"{centered_timestamp}\n", user_color)
            self.chat_history.tag_add(user_color, 'end-2c', 'end-1c')

            # Insert the message without attempting to center it
            self.chat_history.insert('end', f"{sender}: {msg}\n", user_color)
            self.chat_history.tag_add(user_color, 'end-2c', 'end-1c')

            self.chat_history.configure(state='disabled')
            self.chat_history.see('end')
        except ValueError:
            self.chat_history.configure(state='normal')
            self.chat_history.insert('end', message + '\n')
            self.chat_history.configure(state='disabled')
            self.chat_history.see('end')

    def generate_random_color(self):
        return '#%02x%02x%02x' % (random.randint(0,  255), random.randint(0,  255), random.randint(0,  255))

    def show_emoji_picker(self):
        emoji_window = tk.Toplevel(self.master)
        emoji_window.title("Emoji Picker")
        
        emoji_frame = tk.Frame(emoji_window)
        emoji_frame.pack(fill=tk.BOTH, expand=True)

        emoji_scroll = ttk.Scrollbar(emoji_frame, orient=tk.VERTICAL)
        emoji_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        emoji_list = tk.Listbox(emoji_frame, yscrollcommand=emoji_scroll.set)
        emoji_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        emojis = ["😊", "😂", "😍", "👍", "👋", "🎉", "🙌", "🥳", "🤔", "😎", "👀", "❤️", "💡", "✨"]  # Add more emojis as needed

        for emoji in emojis:
            emoji_list.insert(tk.END, emoji)
        
        emoji_scroll.config(command=emoji_list.yview)

        emoji_list.bind("<<ListboxSelect>>", lambda event: self.insert_selected_emoji(emoji_list.get(tk.ACTIVE)))

    def insert_selected_emoji(self, emoji):
        self.entry_field.insert(tk.END, emoji)

def main():
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Bind the closing event
    root.mainloop()

if __name__ == "__main__":
    main()

