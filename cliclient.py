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
import bcrypt
import psycopg2
import base64 
from myrsa import *

HEADER_LENGTH = 10
LARGEST_PACKET_LENGTH = 1024

conn2 = psycopg2.connect(
        database="postgres", user='postgres', password='1234', host='127.0.0.1', port= '5432'
    )
conn2.autocommit =True
cursor = conn2.cursor()
def user_table(username):
    create= f'''
           
            CREATE TABLE IF NOT EXISTS {username} (
            GroupName VARCHAR ( 20 ),
            key VARCHAR(1000) 
            );
            
            
            CREATE TABLE IF NOT EXISTS {username}info(
            public_key VARCHAR (4096),
            private_key VARCHAR (4096)
            );'''
    cursor.execute(create)
class Term:
    """
    This is the implementation of the client side GUI, that interacts with the server.
    :param current_client_socket: This holds the socket object initialized with TCP anf IPv4
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
    :param add_members_widget: This is the comma separted values of the members who are to be added into the group
    :type add_members_widget: Entry
    :param join_group_name_widget: This is where the group name is inputted while joining a group
    :type join_group_name_widget: Entry
     """
    
    last_received_message = None
    
    def __init__(self,ports):
        """
        This is the constructor for the GUI class\n
        :param master: This main Tkinter Window
        :type master: Tk
        """
        # self.proxy = proxy
        self.ports = ports
        self.current_client_socket = None
        self.client_sockets = []
        # self.root = master
        # self.chat_transcript_area = None
        self.has_joined = False
        self.has_registered = False
        self.current_group = None
        self.username=""
        # self.name_widget = None
        # self.pass_widget = None
        # self.enter_text_widget = None
        # self.join_button = None
        # self.create_group_button = None
        # self.join_group_button = None
        # self.sign_up_button = None
        # self.group_name_widget = None
        # self.add_members_widget = None
        # self.join_group_name_widget = None
        # self.select_image_button = None
        self.current_index = 0
        self.current_port = None
        self.initialize_term()
        
        
    # def initialize_socket(self):
    #     """
    #     This is used to initialize the client side socket
    #     """
    #     self.current_client_socket = self.client_sockets[self.current_index] 


    def initialize_socket(self,remote_port):
        """
        This is used to initialize the client side socket
        """
        self.current_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        self.current_client_socket.connect((remote_ip, remote_port))
        # self.client_sockets.append(self.current_client_socket)


    def initialize_term(self): # GUI initializer
        """
        This is the GUI initializer
        """
        # self.root.title("Socket Chat") 
        # self.root.resizable(0, 0)
        self.current_port = self.ports[self.current_index]
        self.display_name_section()
        self.display_chat_box()
        # self.initialize_sockets()
        
        
        
    
    def listen_for_incoming_messages_in_a_thread(self):
        """
        This runs the function receive_message_from_server in a parallel thread.
        """
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.current_client_socket,))
        thread.start()
        
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
            print(filtered_msg)

            length = int(filtered_msg[1:])
            message = "".encode('utf-8')
            while length > LARGEST_PACKET_LENGTH :
                message += so.recv(LARGEST_PACKET_LENGTH)
                length -= LARGEST_PACKET_LENGTH
                
            if length > 0 :
                message += so.recv(length)
                
                
            # Receive and decode username
            if filtered_msg[0] == 'E':
                if message.decode('utf-8') == "err_0":
                    print("\nInvalid GroupName", "Either the group doesn't exist or you're not in the group!\n")
                else:
                    # self.enter_text_widget.config(state='normal')
                    if self.current_group is not None:
                        print(f'You have left {self.current_group}!' +'\n')
                        # self.chat_transcript_area.yview(END)
                    self.current_group = message.decode('utf-8')
                    print(self.current_group)
                    print(f'You have joined {self.current_group}!' +'\n')
                    # self.start_chat()
                    # self.chat_transcript_area.yview(END)
            
            elif filtered_msg[0] == 'I' :
                image = Image.open(io.BytesIO(message))
                image.show()
            elif filtered_msg[0] == 'L' :
                message=json.loads(message)
                username = self.username
                groupname = message["groupname"]
                    
                grpexistquery = f'''
                Select count(*) from {username} where GroupName = \'{groupname}\''''
                cursor.execute(grpexistquery)
                rows = cursor.fetchall()
                key = None
                if rows[0][0] == 0 :
                    key=generate_fernet()
                    key = str(key)[2:-1]
                    #print("FERNET : \n", key, str(key), len(key), len(str(key)))
                    insertkey = f'''
                    INSERT INTO {username} VALUES (\'{groupname}\', \'{key}\');
                    '''
                    cursor.execute(insertkey)
                else : 
                    privatequery = f'''
                    Select key from {username} where GroupName = 
                    \'{groupname}\'
                    '''
                    cursor.execute(privatequery)
                    key = cursor.fetchall()[0]
                    key = key[0]
                mykey=dict({})
                
                for i in message:
                    if i == "groupname" : 
                        mykey[i] = message[i]
                        continue
                    public_client=public_key_decode(message[i])
                    mykey[i]= str(public_client.encrypt(eval("b'" + key + "'"), default_pad))
                print("ERROR CHECK", mykey)
                   # print(type(public_client.encrypt(eval("b'" + key + "'"), default_pad)), mykey[i].encode())
                a = json.dumps(mykey)
                request = a.encode('utf-8')
                header = f"Q{len(request):<{HEADER_LENGTH}}".encode('utf-8')
                self.current_client_socket.send(header + request)
            
            elif filtered_msg[0] == 'Z' :
                message = json.loads(message)
                username = self.username
                # print("Received fernet key : ")
                # print(message)

                fernet_key = message["fernet_key"]
                
                pvtkeyquery = f'''
                Select private_key from {username}info;
                '''
                cursor.execute(pvtkeyquery)
                keys = cursor.fetchall()[0]
                private_key = keys[0]
                
                private_key = private_key_decode(private_key)
                fernet_key = private_key.decrypt(eval(fernet_key), default_pad)
                fernet_key = str(fernet_key)[2:-1]
                # print(fernet_key)
                # print("BEFORE INSERTION")
                insertkeyquery = f'''
                Insert into {username} (GroupName, Key) VALUES (\'{message["groupname"]}\', \'{fernet_key}\') 
                '''
                cursor.execute(insertkeyquery)

            elif filtered_msg[0] == 'J' :
                 message = message.decode('utf-8')
                #self.chat_transcript_area.tag_config('warning', foreground="green")
                 print(message +" hi"+ '\n')
                #  self.chat_transcript_area.yview(END)
            elif filtered_msg[0] == "M":
                msg = json.loads(message.decode('utf-8'))
                groupname=self.current_group
                username = self.username
                privatequery = f'''
                    Select key from {username} where GroupName = 
                    \'{groupname}\'
                    '''
                message = msg['message'].encode()
                # print(groupname)
                cursor.execute(privatequery)
                
                key = cursor.fetchall()
                # print(key)
                key = key[0][0]
                # print(key)
                key = eval("b'" + key + "'")
                # print(key)
                key = Fernet(key)
                # print(message)
                message = key.decrypt(message)
                #self.chat_transcript_area.tag_config('warning', foreground="green")
                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                print(msg["user"] +" "+message.decode('utf-8') + '\n')
                
                # self.chat_transcript_area.yview(END)
                mesg = json.dumps({'user': username, 'group_name' : groupname , 'counter' : msg['counter']}).encode('utf-8')
                message_len = len(mesg)
                acknowledgement = f"V{message_len:<{HEADER_LENGTH}}".encode(
                                'utf-8') + mesg
                self.current_client_socket.send(acknowledgement)
                     
            #self.display_chat_box()   

        print('closed!')
        so.close()


    #Requests
    #1. a - authenticate
    #2. b - recieve all users
    
    
    def start_chat(self):

        while True:
            x=int(input( "1.send chat 2.exit"))
            if x== 1:
                self.send_chat()
            if x == 2:
                return

    def display_name_section(self):
        """
        This displays the section with username, password, create and join group inside the main GUI
        """
        # frame = Frame()
        # frame.pack()

        # #username
        # Label(frame, text='Username:', font=("arial", 13,"bold")).grid(row=0,column=0,padx=5,pady=10)
        # self.name_widget = Entry(frame, width=40,font=("arial", 13))
        # self.name_widget.grid(row=0,column=1,padx=10,pady=10)
        
        # #password
        # Label(frame, text='Password:', font=("arial", 13,"bold")).grid(row=1,column=0,padx=5,pady=10)
        # self.pass_widget = Entry(frame,show="*" ,width=40,font=("arial", 13))
        # self.pass_widget.grid(row=1,column=1,padx=10,pady=10)
        
        x=int(input("\n1. TO JOIN 2. TO SIGN UP\n"))
        if x == 1:
            self.on_join()
        elif x==2:
            self.on_signup()
        
        
        # self.join_button = Button(frame, text="Join", width=10, command=self.on_join)
        # self.join_button.grid(row=0,column=2,padx=10)
        
        # self.sign_up_button = Button(frame, text="Sign Up", width=10, command=self.on_signup)
        # self.sign_up_button.grid(row=1,column=2,padx=10)


        # self.create_group_button = Button(frame, text="Create/Amend Group", width=20, command=self.display_create_group_window, state='disabled')
        # self.create_group_button.grid(row=3,column=0,padx=10)

        # self.join_group_button = Button(frame, text="Join Group", width=10, command=self.display_join_group_window, state='disabled')
        # self.join_group_button.grid(row=3,column=2,padx=10)

    def display_chat_box(self):
        """
        This displays the chatbox in the GUI
        """
    # frame = Frame()
    # Label(frame, text='Chat Box', font=("arial", 12,"bold")).grid(row=0, column=0, padx=100)
    # self.chat_transcript_area = Text(frame, width=60, height=10, font=("arial", 12))
    # scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
    # self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
    # self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
    # self.chat_transcript_area.grid(row=1,column=0, padx=10, pady=10)
    # scrollbar.grid(row =1 ,column=1,columnspan=7)

        # Label(frame, text='Enter Your Message Here!', font=("arial", 12,"bold")).grid(row =2 , column= 0, padx=100)
        # self.enter_text_widget = Text(frame, width=60,height=2 ,font=("arial", 12))
        # self.enter_text_widget.config(state='disabled')
        # self.enter_text_widget.grid(row =3 , column= 0, pady=10, padx=10)
        # self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        # self.select_image_button = Button(frame, text="Send Image", width=10, command=self.send_image, state='disabled')
        # self.select_image_button.grid(row =3 , column =1, padx=10)
        # frame.pack(side='top')
        while True : 
            x=int(input("\n1. Create Group 2. JOIN GROUP\n"))
            if x==1:
                self.display_create_group_window()
            if x==2:
                self.display_join_group_window()
                new_grp = self.current_group
                print("What is the group ?",new_grp)
                while new_grp == None : 
                    new_grp = self.current_group
                if (new_grp != None) :
                    self.start_chat()
                



    def send_image(self):
        filename = input("filename \n")
        if filename == "":
            return
        f = open(filename, 'rb')
        send = b""
        data1 = f.read()
        while data1 : 
            send += data1
            data1 = f.read(1024)
            
        img_header = f"I{len(send):<{HEADER_LENGTH}}".encode('utf-8')
        self.current_client_socket.send(img_header + send)
        self.round_robin_load_switcher()
    
    def create_group_request(self,top):
        """
        This sends a request to the server to create/amend a group and add members to it
        :param top: This is the popup window
        :type top: TopLevel
        """
        add_members_list = top[1].strip().split(',')
        remove_members_list = top[2].strip().split(',')
        

        for i in range(len(add_members_list)):
            add_members_list[i] = add_members_list[i].strip()
        for i in range(len(remove_members_list)):
            remove_members_list[i] = remove_members_list[i].strip()
        grp_head=json.dumps({"members_to_add" : add_members_list,"members_to_remove" : remove_members_list ,"groupname" : top[0]})

        request = (grp_head).encode('utf-8')
        header = f"R{len(request):<{HEADER_LENGTH}}".encode('utf-8')
        self.current_client_socket.send(header + request)
        self.round_robin_load_switcher()
        # top.destroy()
        
    
    def display_create_group_window(self):
        """
        This is the popup window that opens upon pressing the Creata/Amend Group button
        """
        # top= Toplevel(self.root)
        # top.resizable(0, 0)
        # top.title("Create/Amend a Group")
        print("Create / AMMEND GROUP")
        # print(users)
        # frame = Frame(top)
        # frame.pack()
        # Label(frame, text='Group Name:', font=("arial", 13,"bold")).grid(row=0,column=0,padx=5,pady=10)
        # self.group_name_widget = Entry(frame, width=40,font=("arial", 13))
        # self.group_name_widget.grid(row=0,column=1,padx=10,pady=10)
        grpname=input("enter grpname \n")
        Add_mem=input("Add Members(enter CSV) \n")
        Del_mem=input("Remove Members(enter CSV) \n")
        top= (grpname,Add_mem,Del_mem)
        return self.create_group_request(top)
        # #password
        # Label(frame, text='Add Members(enter CSV):', font=("arial", 13,"bold")).grid(row=1,column=0,padx=5,pady=10)
        # self.add_members_widget = Entry(frame, width=40,font=("arial", 13))
        # self.add_members_widget.grid(row=1,column=1,padx=10,pady=10)
        # Label(frame, text='Remove Members(enter CSV):', font=("arial", 13,"bold")).grid(row=2,column=0,padx=5,pady=10)
        # self.remove_members_widget = Entry(frame, width=40,font=("arial", 13))
        # self.remove_members_widget.grid(row=2,column=1,padx=10,pady=10)
        # Button(frame,width=20 ,text='Create/Amend Group', command=(lambda : self.create_group_request(top))).grid(row= 3,column = 0)
        # return
    




        # Label(top, text= "Hello World!", font=('Mistral 18 bold')).place(x=150,y=80)
    def display_join_group_window(self):
        """
        This is the popup window that opens upon clicking Join Group button
        """
        # top= Toplevel(self.root)
        # top.resizable(0, 0)
        print("Join a Group\n")
        grpname=input("enter grpname \n")
        
        # frame = Frame(top)
        # frame.pack()
        # grpname = input('grpname\n')
        # Label(frame, text='Group Name:', font=("arial", 13,"bold")).grid(row=0,column=0,padx=5,pady=10)
        # self.join_group_name_widget = Entry(frame, width=40,font=("arial", 13))
        # self.join_group_name_widget.grid(row=0,column=1,padx=10,pady=10)
        return self.join_group(grpname)
        # Button(frame, text='Join Group', command=(lambda : self.join_group(self.join_group_name_widget.get().strip(),top))).grid(row= 2,column = 0)  

    
    def join_group(self,grpname):
        """
        This sends a request to the server when a client wants to join a group
        :param grpname: This is the group name
        :type top: string
        :param top: This is the popup window
        :type top: TopLevel
        """
        request = (grpname).encode('utf-8')
        header = f"J{len(request):<{HEADER_LENGTH}}".encode('utf-8')
        self.current_client_socket.send(header + request)       
        # top.destroy()
        # self.join_group_button['text'] = 'Change Group'
        # self.select_image_button.config(state = 'normal')
        self.round_robin_load_switcher()

    def round_robin_load_switcher(self):
        print(self.current_index)
        self.current_index = (self.current_index +1)%(len(self.ports))
        self.current_client_socket= self.client_sockets[self.current_index]
        # print(self.current_index)
        # print(self.current_client_socket)
        # self.initialize_socket(self.current_port)
        # self.listen_for_incoming_messages_in_a_thread()

    def on_signup(self):
        """
        This handles the signup request to the server
        """
        user = input("enter username \n")
        password= input("enter password \n")
        if len(user) == 0 or len(password) == 0:
            print(
                "\nInvalid username/password", "The username/password field cannot be blank!\n")
            return False
        if not self.has_registered:
            self.initialize_socket(self.current_port)
            username = user
            password = password.encode('utf-8')
            salt = bcrypt.gensalt()
            pwdhash = bcrypt.hashpw(password,salt).decode('utf-8')
            print("before rsa")
            public_key, private_key, insertmsgquery = enter_my_key(username,cursor)
            print("after rsa")
            userdetails = json.dumps({'token' : 'register','user' : username, 'pass' : pwdhash, 'public_key': public_key }).encode('utf-8')
            header = f"S{len(userdetails):<{HEADER_LENGTH}}".encode('utf-8')
            self.current_client_socket.send(header + userdetails)
            code = self.current_client_socket.recv(10).decode('utf-8')

            if code == 'err_2':
                print(
                "\nInvalid username/password", "The user already exists!\n")
                return False
            else:
                print(
                "\nSuccess!", "You have successfully registered!\n")
                
            self.has_registered = True
            
            user_table(username)
            cursor.execute(insertmsgquery, (public_key, private_key))
            
            while True : 
                x=int(input("Press 1 to join chat"))
                if x == 1:
                    result = self.on_join()
                    if result : break
            
        return True

    def on_join(self):
        """
        This handles the join request to the server
        """
        user = input("enter username \n")
        password= input("enter password \n")
      
        if len(user) == 0 or len(password) == 0:
            print(
                "\nInvalid username/password", "The username/password field cannot be blank!\n")
            return False
        if not self.has_joined:
            # self.initialize_socket(self.current_port)
            
            
            
            username = user
            password = password

       
            
            userdetails = json.dumps({'token' : 'join','user' : username, 'pass' : password}).encode('utf-8')
            header = f"A{len(userdetails):<{HEADER_LENGTH}}".encode('utf-8')
            # print("here")
            # self.current_client_socket.send(header + userdetails)
            # code = self.current_client_socket.recv(10).decode('utf-8')
            # print(code)
            for port in self.ports:
                # print("here")
                # print(cs)
                self.initialize_socket(port)
                self.current_client_socket.send(header + userdetails)
                code = self.current_client_socket.recv(10).decode('utf-8')
                self.client_sockets.append(self.current_client_socket)

            
            if code == 'err_1':
                self.client_sockets = []
                print(
                "\nInvalid username/password", "If The username is not registered, try using the Sign In button!\n")
                return False
            ##get validation message
            # self.chat_transcript_area.yview(END)
            self.has_joined = True
            self.username = username
            # self.name_widget.config(state='disabled')
            # self.pass_widget.config(state='disabled')

            
            # self.create_group_button.config(state = 'normal')
            # self.join_group_button.config(state = 'normal') 

            for cs in self.client_sockets:
                self.current_client_socket = cs                
                self.listen_for_incoming_messages_in_a_thread()
           
            
            self.current_client_socket = self.client_sockets[self.current_index]
            
        return True

    def send_chat(self):
        """
        This sends the message to the server
        """
        username = self.username +": "
        message = input("\n enter message to send \n")
        data = message.strip()
        if data != "":
            message = data.encode('utf-8')
            print('\n'+username+":"+message.decode('utf-8') + '\n')
            # self.chat_transcript_area.yview(END)

            fernetkeyquery = f'''
            Select key from {username[:-2]} where GroupName = \'{self.current_group}\'
            '''
            print(self.current_group)
            cursor.execute(fernetkeyquery)
            key = cursor.fetchall()
            key = key[0][0]
            print("Send!! : ", key)
            key = eval("b'" + key + "'")
            key = Fernet(key)
            message = key.encrypt(message)
            message_header = f"M{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            self.current_client_socket.send(message_header + message)

        # self.enter_text_widget.delete(1.0, 'end')
        self.round_robin_load_switcher()
        return 'break'

    # def on_close_window(self):
    #     """
    #     This handles exiting the GUI
    #     """
    #     if messagebox.askokcancel("Quit", "Do you want to quit?"):
    #         self.root.destroy()
    #         self.current_client_socket.close()
    #         exit(0)

#the mail function 
if __name__ == '__main__':
    # proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")
    ports = [1234]
    # root = "hi"
    gui = Term( ports)
    # root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    # root.mainloop()
    # proxy.kill()p.