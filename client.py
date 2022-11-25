import io
from tkinter import Tk,Toplevel ,Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox, Checkbutton, IntVar #Tkinter Python Module for GUI  
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import socket #Sockets for network connection
import threading # for multiple proccess 
import json
import numpy as np
import bcrypt
import psycopg2
import random
from myrsa import *
# from load_balancer import load_balancer_round_robin
from load_balancer import cpuutil_load_balancer

HEADER_LENGTH = 10
LARGEST_PACKET_LENGTH = 1024

conn2 = psycopg2.connect(
        database="postgres", user='postgres', password='1234', host='127.0.0.1', port= '5432'
    )
conn2.autocommit =True
cursor = conn2.cursor()
def user_table(username):
    create= f'''
            DROP TABLE IF EXISTS {username} cascade;
            CREATE TABLE IF NOT EXISTS {username} (
            GroupName VARCHAR ( 20 ),
            key VARCHAR(1000) 
            );
            
            DROP TABLE IF EXISTS {username}info cascade;
            CREATE TABLE IF NOT EXISTS {username}info(
            public_key VARCHAR (4096),
            private_key VARCHAR (4096)
            );'''
    cursor.execute(create)
class GUI:
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
    
    def __init__(self, master, ports):
        """
        This is the constructor for the GUI class\n
        :param master: This main Tkinter Window
        :type master: Tk
        """
        # self.proxy = proxy
        self.ports = ports
        self.current_client_socket = None
        self.client_sockets = []
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
        self.add_members_widget = None
        self.join_group_name_widget = None
        self.select_image_button = None
        self.current_index = 0
        self.current_port = None
        self.initialize_gui()
        


    def initialize_socket(self,remote_port):
        """
        This is used to initialize the client side socket
        """
        self.current_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        self.current_client_socket.connect((remote_ip, remote_port))
        # self.client_sockets.append(self.current_client_socket)


    def initialize_gui(self): # GUI initializer
        """
        This is the GUI initializer
        """
        self.root.title("Socket Chat") 
        self.root.resizable(0, 0)
        self.display_name_section()
        self.display_chat_box()
        self.current_port = self.ports[self.current_index]
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
     
                # sys.exit()

            filtered_msg = header.decode('utf-8').strip()
   

            length = int(filtered_msg[1:])
            message = "".encode('utf-8')
            while length > LARGEST_PACKET_LENGTH:
                  message += so.recv(LARGEST_PACKET_LENGTH)
                  length -= LARGEST_PACKET_LENGTH

            if length > 0:
                message += so.recv(length)
            
            # Receive and decode username
            if filtered_msg[0] == 'E':
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
                msg = json.loads(message.decode('utf-8'))
                groupname=self.current_group
                username = self.name_widget.get()
                privatequery = f'''
                    Select key from {username} where GroupName = 
                    \'{groupname}\'
                    '''
                message = msg['message'].encode()
                cursor.execute(privatequery)
                
                key = cursor.fetchall()[0][0]
                key = eval("b'" + key + "'")
                key = Fernet(key)
             
                message = key.decrypt(message)
                #self.chat_transcript_area.tag_config('warning', foreground="green")
                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                
                mesg = json.dumps({'user': username, 'group_name' : groupname , 'counter' : msg['counter']}).encode('utf-8')
                message_len = len(mesg)
                acknowledgement = f"V{message_len:<{HEADER_LENGTH}}".encode(
                                'utf-8') + mesg
                self.current_client_socket.send(acknowledgement)

                image = Image.open(io.BytesIO(message))
                image.show()
            elif filtered_msg[0] == 'L' :
                message=json.loads(message)
                username = self.name_widget.get()
                groupname = message["groupname"]
                    
                grpexistquery = f'''
                Select count(*) from {username} where GroupName = \'{groupname}\''''
                cursor.execute(grpexistquery)
                rows = cursor.fetchall()
                key = None
                if rows[0][0] == 0 :
                    key=generate_fernet()
                    key = str(key)[2:-1]
                 
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
                
                a = json.dumps(mykey)
                request = a.encode('utf-8')
                header = f"Q{len(request):<{HEADER_LENGTH}}".encode('utf-8')
                self.current_client_socket.send(header + request)
            
            elif filtered_msg[0] == 'Z' :
                message = json.loads(message)
                username = self.name_widget.get()
           

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
              
                insertkeyquery = f'''
                Insert into {username} (GroupName, Key) VALUES (\'{message["groupname"]}\', \'{fernet_key}\') 
                '''
                cursor.execute(insertkeyquery)
            

            elif filtered_msg[0] == 'J' :
                 message = message.decode('utf-8')
                 self.chat_transcript_area.tag_config('success', foreground="green")
                 self.chat_transcript_area.insert('end',message + '\n','success')
                 self.chat_transcript_area.yview(END)
            elif filtered_msg[0] == "M":
                msg = json.loads(message.decode('utf-8'))
                groupname=self.current_group
                username = self.name_widget.get()
                privatequery = f'''
                    Select key from {username} where GroupName = 
                    \'{groupname}\'
                    '''
                message = msg['message'].encode()
     
                cursor.execute(privatequery)
                
                key = cursor.fetchall()[0][0]
                # print(key)
                key = eval("b'" + key + "'")
                # print(key)
                key = Fernet(key)
              
                message = key.decrypt(message)
                #self.chat_transcript_area.tag_config('warning', foreground="green")
                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                
                self.chat_transcript_area.insert('end',msg['user'] +": "+message.decode('utf-8') + '\n')
                self.chat_transcript_area.yview(END)
                
                mesg = json.dumps({'user': username, 'group_name' : groupname , 'counter' : msg['counter']}).encode('utf-8')
                message_len = len(mesg)
                acknowledgement = f"V{message_len:<{HEADER_LENGTH}}".encode(
                                'utf-8') + mesg
                self.current_client_socket.send(acknowledgement)
            elif filtered_msg[0] == "C":
                
                for i in self.client_sockets:
                    i.close()
                break
                
            elif filtered_msg[0] == "R":
                self.enter_text_widget.config(state='disabled')
                self.current_group = None
                message = message.decode('utf-8')
              
                self.chat_transcript_area.tag_config('warning', foreground="red")
                self.chat_transcript_area.insert('end',message + '\n','warning')
                self.chat_transcript_area.yview(END)

        print("closed")
        so.close()
        self.current_client_socket = None


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
        self.pass_widget = Entry(frame,show="*" ,width=40,font=("arial", 13))
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



    def send_image(self):
        filename = askopenfilename()
        if filename == "":
            return
        f = open(filename, 'rb')
        send = b""
        data = f.read()
        while data : 
            send += data
            data = f.read(1024)

        username = self.name_widget.get()
        fernetkeyquery = f'''
        Select key from {username} where GroupName = \'{self.current_group}\'
        '''
        cursor.execute(fernetkeyquery)
        key = cursor.fetchall()
        key = key[0][0]
        key = eval("b'" + key + "'")
        key = Fernet(key)
        send = key.encrypt(send)
        img_header = f"I{len(send):<{HEADER_LENGTH}}".encode('utf-8')
        self.current_client_socket.send(img_header + send)
        self.load_switcher()
        
      

    def display_create_group_window(self):
        """
        This is the popup window that opens upon pressing the Creata/Amend Group button
        """
        
        
        top= Toplevel(self.root)
        top.resizable(0, 0)
        top.title("Create/Amend a Group")

        
    
        
        
        frame = Frame(top)
        frame.pack()
        
        Label(frame, text='Group Name:', font=("arial", 13,"bold")).grid(row=0,column=0,padx=5,pady=10)
        self.group_name_widget = Entry(frame, width=40,font=("arial", 13))
        self.group_name_widget.grid(row=0,column=1,padx=10,pady=10)
        
        #password
        Label(frame, text='Add Members(enter CSV):', font=("arial", 13,"bold")).grid(row=1,column=0,padx=5,pady=10)
        self.add_members_widget = Entry(frame, width=40,font=("arial", 13))
        self.add_members_widget.grid(row=1,column=1,padx=10,pady=10)
        

        Label(frame, text='Remove Members(enter CSV):', font=("arial", 13,"bold")).grid(row=2,column=0,padx=5,pady=10)
        self.remove_members_widget = Entry(frame, width=40,font=("arial", 13))
        self.remove_members_widget.grid(row=2,column=1,padx=10,pady=10)


        Button(frame,width=20 ,text='Create/Amend Group', command=(lambda : self.create_group_request(top))).grid(row= 3,column = 0)
       
      
        return
    
    def create_group_request(self,top):
        """
        This sends a request to the server to create/amend a group and add members to it
        :param top: This is the popup window
        :type top: TopLevel
        """
        add_members_list = self.add_members_widget.get().strip().split(',')
        remove_members_list = self.remove_members_widget.get().strip().split(',')
        

        for i in range(len(add_members_list)):
            add_members_list[i] = add_members_list[i].strip()
        for i in range(len(remove_members_list)):
            remove_members_list[i] = remove_members_list[i].strip()
        grp_head=json.dumps({"members_to_add" : add_members_list,"members_to_remove" : remove_members_list ,"groupname" : self.group_name_widget.get().strip()})

        request = (grp_head).encode('utf-8')
        header = f"R{len(request):<{HEADER_LENGTH}}".encode('utf-8')
        self.current_client_socket.send(header + request)
        self.load_switcher()
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
        self.current_client_socket.send(header + request)       
        top.destroy()
        self.join_group_button['text'] = 'Change Group'
        self.select_image_button.config(state = 'normal')
        self.load_switcher()

    def load_switcher(self):

        ####ROUND ROBIN LOAD SWITCHER
        # self.current_index = load_balancer_round_robin.get_port_index()
        # self.current_client_socket= self.client_sockets[self.current_index]


        #####LOAD BALANCER BASED ON CPU UTILISATION
        # self.current_index = cpuutil_load_balancer.get_port_from_table()
        # self.current_client_socket= self.client_sockets[self.current_index]


        #####LOAD BALANCER BASED ON ROUND ROBIN BUT ON CLIENT SIDE
        self.current_index = (self.current_index +1)%(len(self.ports))
        self.current_client_socket= self.client_sockets[self.current_index]

        ##### RANDOM LOAD SWITCHER
        # self.curent_index = random.randint(0,len(self.ports)-1)
        # self.current_client_socket= self.client_sockets[self.current_index]


    def on_signup(self):
        """
        This handles the signup request to the server
        """
        if len(self.name_widget.get()) == 0 or len(self.pass_widget.get()) == 0:
            messagebox.showerror(
                "Invalid username/password", "The username/password field cannot be blank!")
            return
        if not self.has_registered:
            self.initialize_socket(self.current_port)
            
     
            username = self.name_widget.get()
            password = self.pass_widget.get().encode('utf-8')
            

            salt = bcrypt.gensalt()
            pwdhash = bcrypt.hashpw(password,salt).decode('utf-8')
      
            public_key, private_key, insertmsgquery = enter_my_key(username,cursor)
      
            userdetails = json.dumps({'token' : 'register','user' : username, 'pass' : pwdhash, 'public_key': public_key }).encode('utf-8')
            header = f"S{len(userdetails):<{HEADER_LENGTH}}".encode('utf-8')
            self.current_client_socket.send(header + userdetails)
       
            code = self.current_client_socket.recv(10).decode('utf-8')

            if code == 'err_2':
                messagebox.showerror(
                "Invalid username/password", "The user already exists!")
            else:
                messagebox.showinfo(
                "Success!", "You have successfully registered!")
            self.has_registered = True
            
            user_table(username)
            cursor.execute(insertmsgquery, (public_key, private_key))
                
        
    
    def on_join(self):
        """
        This handles the join request to the server
        """
      
        if len(self.name_widget.get()) == 0 or len(self.pass_widget.get()) == 0:
            messagebox.showerror(
                "Invalid username/password", "The username/password field cannot be blank!")
            return
        if not self.has_joined:
            # self.initialize_socket(self.current_port)
            
            
            
            username = self.name_widget.get()
            password = self.pass_widget.get()

       
            
            userdetails = json.dumps({'token' : 'join','user' : username, 'pass' : password}).encode('utf-8')
            header = f"A{len(userdetails):<{HEADER_LENGTH}}".encode('utf-8')
         
    
            for port in self.ports:
               
                self.initialize_socket(port)
                self.current_client_socket.send(header + userdetails)
                code = self.current_client_socket.recv(10).decode('utf-8')
                self.client_sockets.append(self.current_client_socket)

            
            if code == 'err_1':
                self.client_sockets = []
                messagebox.showerror(
                "Invalid username/password", "If The username is not registered, try using the Sign In button!")
                return
            ##get validation message
            self.chat_transcript_area.yview(END)
            self.has_joined = True
            self.name_widget.config(state='disabled')
            self.pass_widget.config(state='disabled')

            
            self.create_group_button.config(state = 'normal')
            self.join_group_button.config(state = 'normal') 

            for cs in self.client_sockets:
                self.current_client_socket = cs                
                self.listen_for_incoming_messages_in_a_thread()
           
            
            self.current_client_socket = self.client_sockets[self.current_index]
            

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

            fernetkeyquery = f'''
            Select key from {username[:-2]} where GroupName = \'{self.current_group}\'
            '''
          
            cursor.execute(fernetkeyquery)
            key = cursor.fetchall()
            key = key[0][0]
        
            key = eval("b'" + key + "'")
            key = Fernet(key)
            message = key.encrypt(message)
            message_header = f"M{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            self.current_client_socket.send(message_header + message)

        self.enter_text_widget.delete(1.0, 'end')
        self.load_switcher()
        return 'break'

    def on_close_window(self):
        """
        This handles exiting the GUI
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.current_client_socket is None or not self.has_joined:
                self.root.destroy()
                exit(0)
            username = json.dumps({'user' : self.name_widget.get()}).encode('utf-8')
            header = f"C{len(username):<{HEADER_LENGTH}}".encode('utf-8')
            self.current_client_socket.send(header + username)
            while self.current_client_socket is not None:
                pass
            self.root.destroy()
            exit(0)
            
            
 
            

#the mail function 
if __name__ == '__main__':
    # proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")
    ports = [1234,1235]
    root = Tk()
    gui = GUI(root, ports)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
    # proxy.kill()p.