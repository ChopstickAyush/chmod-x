#! /usr/bin/env python3

import os
import sys
import select
import socket

import pickle
import getpass
import threading
import time
from datetime import datetime
from tkinter import *

# Adding APIs directory to python system path
# sys.path.insert(-1, os.path.join(os.path.dirname
#                                 (os.path.realpath(__file__)), 'APIs'))

# Local modules
from APIs.logging import Log
from APIs.security import *

GUI_OBJ = None
KEY = None


class GUI(object):
    def __init__(self, master, network_obj):
        global GUI_OBJ
        self.master = master
        self.network = network_obj
        self.txt_input = Text(self.master, width=60, height=5)
        self.txt_disp = Text(self.master, width=60, height=15, bg='light grey')
        self.txt_input.bind('<Return>', self.get_entry)
        self.txt_disp.configure(state='disabled')
        self.txt_input.focus()
        self.txt_disp.pack()
        self.txt_input.pack()
        self.flag = True
        GUI_OBJ = self

    def init_canvas(self):
        self.canvas = Canvas(root, width=730, height=600)
        self.canvas.pack(fill="both", expand=True)

    def init_frame(self):
        self.frame_left = Frame(self.canvas, height=400, width=200)
        self.frame_right = Frame(self.canvas, width=500)
        self.frame_right_chat_show = Frame(self.frame_right)
        self.frame_right_chat_input = Frame(self.frame_right, width=460)
        self.frame_right_chat_input_buttons = Frame(self.frame_right, width=40)

        self.frame_left.pack(fill=Y, side='left')
        self.frame_right.pack(fill=Y, side='left')
        self.frame_right_chat_show.pack(fill=X, side='top')
        self.frame_right_chat_input.pack(side='left')
        self.frame_right_chat_input_buttons.pack(side='left')
    # def init_textbox(self):

    def update(self, msg):
        '''
        This method updates chat window
        '''
        msg = '\n' + msg
        self.txt_disp.configure(state='normal')
        self.txt_disp.insert(END, msg)
        self.txt_disp.see(END)
        self.txt_disp.configure(state='disabled')

    def get_entry(self, *arg):
        ''' Gets input from the input field and uses
        network object to send message to the server.
        Finally clears input field to enter msg.
        '''
        # print(self.thread_name + ">> " + str(self.txt_input.get('1.0',END)))
        msg_snd = self.txt_input.get('1.0', END)
        msg_snd = msg_snd.strip('\n')
        self.network.send_msg(msg_snd)
        msg_snd = '<YOU> ' + msg_snd
        self.update(msg_snd)
        self.txt_input.delete('1.0', END)

    def get_msg(self, *arg):
        ''' This method is being used by separate thread
        to keep on receiving messages from the server and
        update chat window.
        '''
        while True:
            msg_rcv = self.network.get_msg()
            if msg_rcv:
                msg_rcv = msg_rcv.strip('\n')
                print('-' * 60)
                print(msg_rcv)
                self.update(msg_rcv)

class Network():
    def __init__(self, thread_name, SRV_IP='', SRV_PORT=''):
        ''' Constructor to initialise network
        connectivity between the client and server.
        '''
        self.SRV_IP = SRV_IP
        self.SRV_PORT = int(SRV_PORT)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.SRV_IP, self.SRV_PORT))
        self.KEY_FLAG = False
        self.priv_key = None
        self.pub_key = None

    def genRSA(self, *args):
        # Generate Private and Public key for particular session
        logging.log("Generating private and public key")
        self.priv_key, self.pub_key = RSA_.genRSA()
        logging.log("Keys generation completed.")
        logging.log(self.pub_key.exportKey())

    def initEncryption(self, userName):
        global KEY

        # Generate Private and Public key for particular session
        #logging.log("Generating private and public key for %s", userName)
        #priv, pub = RSA_.genRSA()
        #logging.log("Keys generation completed.")
        #logging.log(pub.exportKey())
        
        # Prepare data for serialization as tuple
        # can't be transmitted over network.
        msg_send = (userName, self.pub_key)
        msg_send = pickle.dumps(msg_send)
        self.client.send(msg_send)
        logging.log("User name along with public key has been sent to the server.")

        # Wait for the server to send symmetric key
        EnSharedKey = self.client.recv(1024)
        EnSharedKey = pickle.loads(EnSharedKey)
        print(EnSharedKey)
        KEY = RSA_.decrypt(self.priv_key, EnSharedKey)
        print(KEY)
        if KEY:
            logging.log("Unique key has been received")
            self.KEY_FLAG = True
            logging.log("Secure connection has been established.")

    def get_msg(self):
        if KEY != None:
            msg_rcv = AES_.decrypt(KEY.encode(), self.client.recv(20000))
            return msg_rcv

    def send_msg(self, msg_snd):
        if KEY is None:
            # Send (userName, RSA_PublicKey) to the server
            # to get encrypted symmetric key for further encryption.
            self.initEncryption(msg_snd)
            return
        try:
            print(msg_snd)
            result = self.client.send(AES_.encrypt(KEY.encode(), msg_snd))
            print("Bytes sent: ", result)
        except Exception as e:
            print(e)
            GUI.update(GUI_OBJ, "Not connected to the server")

# Outsite class functions
def connection_thread(*args):
    root = args[0]
    retry_count = 0
    gui_flag = False
    while True:
        try:
            network = Network('network_thread', '127.0.0.1', 8080)
            if gui_flag:
                gui.network = network
            if not gui_flag:
                gui = GUI(root, network)
            logging.log('Connected to the server')
            gui.update('Connected to the server')
            gui.update('Enter your name.')
            break
        except Exception as e:
            msg = "[Retry {}] {}".format(retry_count+1, e)
            logging.log(msg)
            retry_count += 1
            if retry_count == 1:
                gui = GUI(root, None)
                gui.update("Failed to connect the server.\n" +\
                        "Started retrying.")
                gui.update("Retry connecting...")
                time.sleep(5)
                gui_flag = True
            elif 4 > retry_count:
                #logging.log('Retry connecting...')
                #gui.update("Retry connecting...")
                time.sleep(5)
                gui_flag = True
            elif retry_count == 5:
                gui.update("Retry limit exceeded.\n" +\
                        "Unable to connect the server.\n" +\
                        "Program will automatically exit after 5 sec.")
                time.sleep(5)
                gui_flag = True
                root.destroy()
    logging.log('New thread has been initialized to fetch data from the server')
    #threading._start_new_thread(network.genRSA, ())
    rsa_thread = threading.Thread(target=network.genRSA, args=())
    rsa_thread.start()
    rsa_thread.join()
    threading._start_new_thread(gui.get_msg,())

def main():
    root = Tk() # instialize root window
    root.title('ChatRoom')

    threading._start_new_thread(connection_thread, (root,))
    logging.log('Connection thread has been called')

    root.mainloop()

    logging.log('exiting main thread.')
    logging.stop()

if __name__ == "__main__":
    logging = Log(f_name='client_chatroom_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    opt = input('Enable logging? (y/N): ')
    if opt in ('y', 'Y', 'yes', 'Yes', 'YES'):
        # it will both save log_msg to a file and print to sys.stdout
        logging.logging_flag = True
        logging.validate_file()
    main()
#TODO: client unable to detemine if server is alive after chat has been started.