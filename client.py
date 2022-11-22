import io
from tkinter import Tk,Toplevel ,Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox, Checkbutton, IntVar #Tkinter Python Module for GUI  
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import socket #Sockets for network connection
import threading # for multiple proccess 
import json
import pickle
import numpy as np


HEADER_LENGTH = 10


class GUI:
    """
    This is the implementation of the client side GUI, that interacts with the server.
    :param client_socket: This holds the socket object initialized with TCP anf IPv4
    :type client: socket
    :param root: This is the main Tkinter window
    :type root: Tk
    :param chat_transcript_area: This is the box in the GUI where the chat appears
    :type chat_transcript_area: Text
    :param has_joined: This is a variable indicating whether the client has connected to the server.
    :type has_joined: bool
    :param has_registered: This is a variable indicating whether the client has been registered in the server side database
    :type has_registered: bool
    :param current_group: This indicates the current group the user is in
    :type current_group:  string
    :param name_widget: This is the Tkinter widget that takes the username input
    :type name_widget: Entry
    :param pass_widget: This is the Tkinter widget that takes the password input
    :type pass_widget: Entry
    :param enter_text_widget: This is the Tkinter widget that takes the chat message from the user
    :type enter_text_widget: Entry
    :param join_button: On pressing this button the user gets connected to the server
    :type join_button: Button
    :param create_group_button: This allows the client to create/amend any group(if it exists)
    :type create_group_button: Button
    :param join_group_button: This allows the client to join any group they it is already a member
    :type join_group_button: Button
    :param sign_up_button: This allows the client to resgiter their username into the server
    :type sign_up_button: Button
    :param group_name_widget: This is where the group name is inputted while creating a group
    :type group_name_widget: Entry
    :param members_widget: This is the comma separted values of the members who are to be added into the group
    :type members_widget: Entry
    :param join_group_name_widget: This is where the group name is inputted while joining a group
    :type join_group_name_widget: Entry
     """
    
    last_received_message = None
    
    def __init__(self, master):
        """
        This is the constructor for the GUI class\n
        :param master: This main Tkinter Window
        :type master: Tk
        """
        # self.proxy = proxy
        self.client_socket = None
        self.root = master
        self.chat_transcript_area = None
        self.has_joined = False
        self.has_registered = False
        self.current_group = None
        self.name_widget = None
        self.pass_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.create_group_button = None
        self.join_group_button = None
        self.sign_up_button = None
        self.group_name_widget = None
        self.members_widget = None
        self.join_group_name_widget = None
        self.select_image_button = None
        self.initialize_gui()
        

    def initialize_socket(self):
        """
        This is used to initialize the client side socket
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        remote_port = 1234 #TCP port
        self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server

    def initialize_gui(self): # GUI initializer
        """
        This is the GUI initializer
        """
        self.root.title("Socket Chat") 
        self.root.resizable(0, 0)
        self.display_name_section()
        self.display_chat_box()
        
        
        
    
    def listen_for_incoming_messages_in_a_thread(self):
        """
        This runs the function receive_message_from_server in a parallel thread.
        """
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,)) # Create a thread for the send and receive in same time 
        thread.start()
        
    #function to recieve msg



    def receive_message_from_server(self, so):
        """
        This is used to recieve and handle all kinds of messages/responses from the server
        :param so: This is the client socket object
        :type so: socket
        """
        while True:

            header = so.recv(HEADER_LENGTH+1)

            
            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(header):
                self.chat_transcript_area.insert('end','Connection closed by the server' + '\n')
                break
                # print('Connection closed by the server')
                # sys.exit()

            filtered_msg = header.decode('utf-8').strip()

            length = int(filtered_msg[1:])


            message = so.recv(length)
            # Receive and decode username
            if filtered_msg[0] == 'R':
                self.users = eval(message.decode('utf-8'))
                continue
            elif filtered_msg[0] == 'E':
                if message.decode('utf-8') == "err_0":
                    messagebox.showerror("Invalid GroupName", "Either the group doesn't exist or you're not in the group!")
                else:
                    self.enter_text_widget.config(state='normal')
                    if self.current_group is not None:
                        self.chat_transcript_area.insert('end',f'You have left {self.current_group}!' +'\n')
                        self.chat_transcript_area.yview(END)
                    self.current_group = message.decode('utf-8')
                    self.chat_transcript_area.insert('end',f'You have joined {self.current_group}!' +'\n')
                    self.chat_transcript_area.yview(END)
            
            elif filtered_msg[0] == 'I' :
                image = Image.open(io.BytesIO(message))
                image.show()

            else:
                
                self.chat_transcript_area.tag_config('warning', foreground="green")
                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                if ":" in message.decode('utf-8'):
                    self.chat_transcript_area.insert('end',message.decode('utf-8') + '\n')
                    self.chat_transcript_area.yview(END)
                else:
                    self.chat_transcript_area.insert('end',message.decode('utf-8') + '\n','warning')
                    self.chat_transcript_area.yview(END)

        print('closed!')
        so.close()


    #Requests
    #1. a - authenticate
    #2. b - recieve all users

    def display_name_section(self):
        """
        This displays the section with username, password, create and join group inside the main GUI
        """
        frame = Frame()
        frame.pack()

        #username
        Label(frame, text='Username:', font=("arial", 13,"bold")).grid(row=0,column=0,padx=5,pady=10)
        self.name_widget = Entry(frame, width=40,font=("arial", 13))
        self.name_widget.grid(row=0,column=1,padx=10,pady=10)
        
        #password
        Label(frame, text='Password:', font=("arial", 13,"bold")).grid(row=1,column=0,padx=5,pady=10)
        self.pass_widget = Entry(frame, width=40,font=("arial", 13))
        self.pass_widget.grid(row=1,column=1,padx=10,pady=10)


        
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join)
        self.join_button.grid(row=0,column=2,padx=10)
        
        self.sign_up_button = Button(frame, text="Sign Up", width=10, command=self.on_signup)
        self.sign_up_button.grid(row=1,column=2,padx=10)


        self.create_group_button = Button(frame, text="Create/Amend Group", width=20, command=self.display_create_group_window, state='disabled')
        self.create_group_button.grid(row=3,column=0,padx=10)

        self.join_group_button = Button(frame, text="Join Group", width=10, command=self.display_join_group_window, state='disabled')
        self.join_group_button.grid(row=3,column=2,padx=10)

    def display_chat_box(self):
        """
        This displays the chatbox in the GUI
        """
        frame = Frame()
        Label(frame, text='Chat Box', font=("arial", 12,"bold")).grid(row=0, column=0, padx=100)
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("arial", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.grid(row=1,column=0, padx=10, pady=10)
        scrollbar.grid(row =1 ,column=1,columnspan=7)

        Label(frame, text='Enter Your Message Here!', font=("arial", 12,"bold")).grid(row =2 , column= 0, padx=100)
        self.enter_text_widget = Text(frame, width=60,height=2 ,font=("arial", 12))
        self.enter_text_widget.config(state='disabled')
        self.enter_text_widget.grid(row =3 , column= 0, pady=10, padx=10)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        self.select_image_button = Button(frame, text="Send Image", width=10, command=self.send_image, state='disabled')
        self.select_image_button.grid(row =3 , column =1, padx=10)
        frame.pack(side='top')

    # def display_chat_entry_box(self): 
    #     """
    #     This displays the chat entry box inside the GUI
    #     """  
    #     # frame = Frame()
        
    #     # frame.pack(side='bottom')

    def send_image(self):
        filename = askopenfilename()
        if filename == "":
            return
        f = open(filename, 'rb')
        send = b""
        data1 = f.read()
        while data1 : 
            send += data1
            data1 = f.read(1024)
            
        img_header = f"I{len(send):<{HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(img_header + send)


    def display_create_group_window(self):
        """
        This is the popup window that opens upon pressing the Creata/Amend Group button
        """
        
        
        top= Toplevel(self.root)
        top.resizable(0, 0)
        top.title("Create/Amend a Group")

        
        # print(users)
        
        
        frame = Frame(top)
        frame.pack()
   
        
        
        Label(frame, text='Group Name:', font=("arial", 13,"bold")).grid(row=0,column=0,padx=5,pady=10)
        self.group_name_widget = Entry(frame, width=40,font=("arial", 13))
        self.group_name_widget.grid(row=0,column=1,padx=10,pady=10)
        
        #password
        Label(frame, text='Members(enter CSV):', font=("arial", 13,"bold")).grid(row=1,column=0,padx=5,pady=10)
        self.members_widget = Entry(frame, width=40,font=("arial", 13))
        self.members_widget.grid(row=1,column=1,padx=10,pady=10)
        
        Button(frame,width=20 ,text='Create/Amend Group', command=(lambda : self.create_group_request(top))).grid(row= 2,column = 0)
       
      
        return
    
    def create_group_request(self,top):
        """
        This sends a request to the server to create/amend a group and add members to it
        :param top: This is the popup window
        :type top: TopLevel
        """
        members_list = self.members_widget.get().strip().split(',')
        
        

        for i in range(len(members_list)):
            members_list[i] = members_list[i].strip()

        grp_head=json.dumps({"members" : members_list, "groupname" : self.group_name_widget.get().strip()})

        request = (grp_head).encode('utf-8')
        header = f"R{len(request):<{HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(header + request)

        top.destroy()



        # Label(top, text= "Hello World!", font=('Mistral 18 bold')).place(x=150,y=80)
    def display_join_group_window(self):
        """
        This is the popup window that opens upon clicking Join Group button
        """
        top= Toplevel(self.root)
        top.resizable(0, 0)
        top.title("Join a Group")
       
        
        frame = Frame(top)
        frame.pack()
   
        Label(frame, text='Group Name:', font=("arial", 13,"bold")).grid(row=0,column=0,padx=5,pady=10)
        self.join_group_name_widget = Entry(frame, width=40,font=("arial", 13))
        self.join_group_name_widget.grid(row=0,column=1,padx=10,pady=10)
     
        Button(frame, text='Join Group', command=(lambda : self.join_group(self.join_group_name_widget.get().strip(),top))).grid(row= 2,column = 0)  

        
    def join_group(self,grpname,top):
        """
        This sends a request to the server when a client wants to join a group
        :param grpname: This is the group name
        :type top: string
        :param top: This is the popup window
        :type top: TopLevel
        """
        request = (grpname).encode('utf-8')
        header = f"J{len(request):<{HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(header + request)   
        top.destroy()
        self.join_group_button['text'] = 'Change Group'
        self.select_image_button.config(state = 'normal')


    def on_signup(self):
        """
        This handles the signup request to the server
        """
        if len(self.name_widget.get()) == 0 or len(self.pass_widget.get()) == 0:
            messagebox.showerror(
                "Invalid username/password", "The username/password field cannot be blank!")
            return
        if not self.has_registered:
            self.initialize_socket()
            
     
            username = self.name_widget.get()
            password = self.pass_widget.get()
            
            userpass = ("register_"+username+"_"+password).encode('utf-8')
            header = f"S{len(userpass):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(header + userpass)
            code = self.client_socket.recv(10).decode('utf-8')

            if code == 'err_2':
                messagebox.showerror(
                "Invalid username/password", "The user already exists!")
            else:
                messagebox.showinfo(
                "Success!", "You have successfully registered!")
            self.has_registered = True
    
    def on_join(self):
        """
        This handles the join request to the server
        """
        if len(self.name_widget.get()) == 0 or len(self.pass_widget.get()) == 0:
            messagebox.showerror(
                "Invalid username/password", "The username/password field cannot be blank!")
            return
        if not self.has_joined:
            self.initialize_socket()
            
            
            
            username = self.name_widget.get()
            password = self.pass_widget.get()
            
            userpass = ("join_"+username+"_"+password).encode('utf-8')
            header = f"A{len(userpass):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(header + userpass)
            code = self.client_socket.recv(10).decode('utf-8')

            if code == 'err_1':
                messagebox.showerror(
                "Invalid username/password", "If The username is not registered, try using the Sign In button!")
                return
            ##get validation message


            # self.chat_transcript_area.insert('end','You have joined the server!' + '\n')
            self.chat_transcript_area.yview(END)
            self.has_joined = True
            self.name_widget.config(state='disabled')
            self.pass_widget.config(state='disabled')

            self.create_group_button.config(state = 'normal')
            self.join_group_button.config(state = 'normal') 
            self.listen_for_incoming_messages_in_a_thread()
        

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        """
        This sends the message to the server
        """
        username = self.name_widget.get().strip() +": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        if data != "":
            message = data.encode('utf-8')
            self.chat_transcript_area.insert('end', username+message.decode('utf-8') + '\n')
            self.chat_transcript_area.yview(END)
            message_header = f"M{len(message.decode('utf-8')):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header + message)

        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        """
        This handles exiting the GUI
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)

#the mail function 
if __name__ == '__main__':
    # proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
    # proxy.kill()