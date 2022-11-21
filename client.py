from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox #Tkinter Python Module for GUI  
import socket #Sockets for network connection
import threading # for multiple proccess 
import psycopg2
import json
HEADER_LENGTH = 10

conn2 = psycopg2.connect(
        database="postgres", user='postgres', password='1234', host='127.0.0.1', port= '5432'
    )
conn2.autocommit =True
cursor = conn2.cursor()
def user_table(username):
    create= f'''
            CREATE TABLE IF NOT EXISTS {username} (
            GroupName VARCHAR ( 20 ),
            public_key VARCHAR(1000),
            private_key VARCHAR(1000)
            );'''
    cursor.execute(create)

class GUI:
    client_socket = None
    last_received_message = None
    
    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.has_joined = False
        self.has_registered = False
        self.current_group = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        
        self.initialize_gui()
        

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        remote_port = 1243 #TCP port
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

            
            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(header):
                self.chat_transcript_area.insert('end','Connection closed by the server' + '\n')
                break
                # print('Connection closed by the server')
                # sys.exit()
            # if header.decode('utf-8').isalpha:
            #     break
            # Convert header to int value
            length = int(header.decode('utf-8').strip())

            # Receive and decode username
            message = so.recv(length).decode('utf-8')
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
        frame.pack()

        #username
        Label(frame, text='Username:', font=("arial", 13,"bold")).grid(row=0,column=0,padx=5,pady=10)
        self.name_widget = Entry(frame, width=40,font=("arial", 13))
        self.name_widget.grid(row=0,column=1,padx=10,pady=10)
        
        #password
        Label(frame, text='Password:', font=("arial", 13,"bold")).grid(row=1,column=0,padx=5,pady=10)
        self.pass_widget = Entry(frame, width=40,font=("arial", 13))
        self.pass_widget.grid(row=1,column=1,padx=10,pady=10)

        #groupname
        # Label(frame, text='Group Name:', font=("arial", 13,"bold")).grid(row=2,column=0,padx=5,pady=10)
        # self.group_widget = Entry(frame, width=40,font=("arial", 13))
        # self.group_widget.grid(row=2,column=1,padx=10,pady=10)

        self.join_button = Button(frame, text="Join", width=10, command=self.on_join).grid(row=0,column=2,padx=10)
        self.sign_up_button = Button(frame, text="Sign Up", width=10, command=self.on_signup).grid(row=1,column=2,padx=10)

        # self.create_group_button = Button(frame, text="Create Group", width=10, command=self.on_join).grid(row=2,column=2,padx=10)
        

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


    def on_signup(self):
        if len(self.name_widget.get()) == 0 or len(self.pass_widget.get()) == 0:
            messagebox.showerror(
                "Invalid username/password", "The username/password field cannot be blank!")
            return
        if not self.has_registered:
            self.initialize_socket()
            
            username = self.name_widget.get()
            password = self.pass_widget.get()
            
            userpass = ("register_"+username+"_"+password).encode('utf-8')
            header = f"{len(userpass):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(header + userpass)
            code = self.client_socket.recv(10).decode('utf-8')

            if code == 'err_2':
                messagebox.showerror(
                "Invalid username/password", "The user already exists!")
                return
            else:
                messagebox.showerror(
                "Success!", "You have successfully registered!")
                user_table(username)
            self.has_registered = True
    
    def on_join(self):
        if len(self.name_widget.get()) == 0 or len(self.pass_widget.get()) == 0:
            messagebox.showerror(
                "Invalid username/password", "The username/password field cannot be blank!")
            return
        if not self.has_joined:
            self.initialize_socket()
            
            
            
            username = self.name_widget.get()
            password = self.pass_widget.get()
            
            userpass = ("join_"+username+"_"+password).encode('utf-8')
            header = f"{len(userpass):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(header + userpass)
            code = self.client_socket.recv(10).decode('utf-8')

            if code == 'err_1':
                messagebox.showerror(
                "Invalid username/password", "If The username is not registered, try using the Sign In button!")
                return
            ##get validation message
            if code == 'grp_1':
                x=int(input("1) CREATE GROUP 2) JOIN GROUP"))
                if x==2:
                    groupname = input("Enter name of the group you want to join : ")
                    group_pass = ("grp2_"+groupname +"_"+ username).encode('utf-8')
                    head_group = f"{len(group_pass):<{HEADER_LENGTH}}".encode('utf-8')
                    self.client_socket.send(head_group+group_pass)
                    
                if x==1:
                    groupname = input("Enter name of the group you want to Create:")
                    grp_mem=[username]
                    while True:
                        y=input("Member Name (Press 0 to create or exit)")
                        if y=="0":
                            break
                        else:
                            grp_mem.append(y)
                    # grp_head=json.dumps({"members" : grp_mem, "groupname" : groupname})
                    # head_group2 = f"{len(grp_head):<{HEADER_LENGTH}}".encode('utf-8')
                    # group_pass=("grp3_"+groupname).encode('utf-8')
                    # head_group = f"{len(group_pass):<{HEADER_LENGTH}}".encode('utf-8')
                    #self.client_socket.send(head_group+group_pass)
                    grp_head=json.dumps({"members" : grp_mem, "groupname" : groupname})
                    grp_head = ("grp3_" + grp_head).encode('utf-8')
                    head_group = f"{len(grp_head):<{HEADER_LENGTH}}".encode('utf-8')
                    print(grp_head)
                    self.client_socket.send(head_group+grp_head)


            self.chat_transcript_area.insert('end','You have joined the server!' + '\n')
            self.chat_transcript_area.yview(END)
            self.has_joined = True
            self.name_widget.config(state='disabled')
            self.pass_widget.config(state='disabled')
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
        username = self.name_widget.get().strip() +": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        if data != "":
            message = data.encode('utf-8')
            self.chat_transcript_area.insert('end', username+message.decode('utf-8') + '\n')
            self.chat_transcript_area.yview(END)
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header + message)

        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

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