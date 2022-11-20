from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox #Tkinter Python Module for GUI  
import socket #Sockets for network connection
import threading # for multiple proccess 
import pickle
import pdb

from clientdb import *
HEADER_LENGTH = 4096

class GUI:
    client_socket = None
    last_received_message = None
    
    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.has_joined = False
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        
        self.initialize_gui()
        

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        remote_port = 1271 #TCP port
        self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server

    def initialize_gui(self): # GUI initializer
        self.root.title("Socket Chat") 
        self.root.resizable(0, 0)
        self.display_name_section()
        self.display_chat_entry_box()
        self.display_chat_box()
        
        
        
    
    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,)) # Create a thread for the send and receive in same time 
        thread.start()
    #function to recieve msg
    def receive_message_from_server(self, so):
        while True:

            header = so.recv(HEADER_LENGTH)
            print(header)
            data = pickle.loads(header)
            
            
            if data.type == "Message" :

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(data.message):
                    self.chat_transcript_area.insert('end','Connection closed by the server' + '\n')
                    break
                    # print('Connection closed by the server')
                    # sys.exit()

                # Convert header to int value
                length = int(data.message.decode('utf-8').strip())

                # Receive and decode username
                message = so.recv(length).decode('utf-8')
                message = pickle.loads(message)
                message = message.message

                self.chat_transcript_area.tag_config('warning', foreground="green")
                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                if ":" in message:
                    self.chat_transcript_area.insert('end',message + '\n')
                    self.chat_transcript_area.yview(END)
                else:
                    self.chat_transcript_area.insert('end',message + '\n','warning')
                    self.chat_transcript_area.yview(END)

        so.close()

    def receive_all_users_in_server(self):
        pass

    def display_name_section(self):
        frame = Frame()
        Label(frame, text='Enter Your Name Here! ', font=("arial", 13,"bold")).pack(side='left', pady=20)
        self.name_widget = Entry(frame, width=60,font=("arial", 13))
        self.name_widget.pack(side='left', anchor='e',  pady=15)
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join).pack(side='right',padx=5, pady=15)
        frame.pack(side='top', anchor='nw')

    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='Chat Box', font=("arial", 12,"bold")).pack(side='top', padx=270)
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("arial", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=15, pady=10)
        scrollbar.pack(side='right', fill='y',padx=1)
        frame.pack(side='left')

    def display_chat_entry_box(self):   
        frame = Frame()
        Label(frame, text='Enter Your Message Here!', font=("arial", 12,"bold")).pack(side='top', anchor='w', padx=120)
        self.enter_text_widget = Text(frame, width=50, height=10, font=("arial", 12))
        self.enter_text_widget.pack(side='left', pady=10, padx=10)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='left')

    def on_join(self):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        if not self.has_joined:
            self.initialize_socket()
            self.listen_for_incoming_messages_in_a_thread()
            
            self.name_widget.config(state='disabled')
            username = self.name_widget.get().encode('utf-8')
            username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(username_header + username)
            self.chat_transcript_area.insert('end','You have joined the server!' + '\n')
            self.chat_transcript_area.yview(END)
            self.has_joined = True
        

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        username = self.name_widget.get().strip() +": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        if data != "":
            message = data.encode('utf-8')
            self.chat_transcript_area.insert('end', username+message.decode('utf-8') + '\n')
            self.chat_transcript_area.yview(END)
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(pickle.dumps(Wrap(message_header + message,"Message")))

        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def name_request(self, name):
        W1 = Wrap(name,"check_name")
        s = pickle.dumps(W1)
        self.client_socket.send(s)


        
    
    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)

#the mail function 
if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()