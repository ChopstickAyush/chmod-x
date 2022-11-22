from tkinter import Tk,Toplevel ,Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox, Checkbutton, IntVar #Tkinter Python Module for GUI  
import socket #Sockets for network connection
import threading # for multiple proccess 
import json


HEADER_LENGTH = 10


class GUI:
    client_socket = None
    last_received_message = None
    
    def __init__(self, master):
        # self.proxy = proxy
        self.root = master
        self.chat_transcript_area = None
        self.has_joined = False
        self.has_registered = False
        self.current_group = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.users = None
        self.initialize_gui()
        

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        remote_port = 1234 #TCP port
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

            header = so.recv(HEADER_LENGTH+1)

            
            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(header):
                self.chat_transcript_area.insert('end','Connection closed by the server' + '\n')
                break
                # print('Connection closed by the server')
                # sys.exit()

            filtered_msg = header.decode('utf-8').strip()

            length = int(filtered_msg[1:])


            message = so.recv(length).decode('utf-8')
            # Receive and decode username
            if filtered_msg[0] == 'R':
                self.users = eval(message)
                continue
            elif filtered_msg[0] == 'E':
                if message == "err_0":
                    messagebox.showerror("Invalid GroupName", "Either the group doesn't exist or you're not in the group!")
                else:
                    self.enter_text_widget.config(state='normal')
                    if self.current_group is not None:
                        self.chat_transcript_area.insert('end',f'You have left {self.current_group}!' +'\n')
                        self.chat_transcript_area.yview(END)
                    self.current_group = message
                    self.chat_transcript_area.insert('end',f'You have joined {self.current_group}!' +'\n')
                    self.chat_transcript_area.yview(END)
            else:
                
                self.chat_transcript_area.tag_config('warning', foreground="green")
                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                if ":" in message:
                    self.chat_transcript_area.insert('end',message + '\n')
                    self.chat_transcript_area.yview(END)
                else:
                    self.chat_transcript_area.insert('end',message + '\n','warning')
                    self.chat_transcript_area.yview(END)

        print('closed!')
        so.close()


    #Requests
    #1. a - authenticate
    #2. b - recieve all users

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


        
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join)
        self.join_button.grid(row=0,column=2,padx=10)
        
        self.sign_up_button = Button(frame, text="Sign Up", width=10, command=self.on_signup)
        self.sign_up_button.grid(row=1,column=2,padx=10)


        self.create_group_button = Button(frame, text="Create/Amend Group", width=20, command=self.display_create_group_window, state='disabled')
        self.create_group_button.grid(row=3,column=0,padx=10)

        self.join_group_button = Button(frame, text="Join Group", width=10, command=self.display_join_group_window, state='disabled')
        self.join_group_button.grid(row=3,column=2,padx=10)

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
        self.enter_text_widget.config(state='disabled')
        self.enter_text_widget.pack(side='left', pady=10, padx=10)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='left')


    def display_create_group_window(self):

        
        
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
        
        request = (grpname).encode('utf-8')
        header = f"J{len(request):<{HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(header + request)   
        top.destroy()
        self.join_group_button['text'] = 'Change Group'


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
        username = self.name_widget.get().strip() +": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        if data != "":
            message = data.encode('utf-8')
            self.chat_transcript_area.insert('end', username+message.decode('utf-8') + '\n')
            self.chat_transcript_area.yview(END)
            message_header = f"M{len(message):<{HEADER_LENGTH}}".encode('utf-8')
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
    # proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
    # proxy.kill()