from pwn import *
import time
import threading
import os
from os.path import exists

NUM_CLIENTS = 4
NUM_SERVERS = 3

if not exists("log"): os.makedirs("log")

class Server : 
    servers = []
    def __init__(self, port):
        self.ps = None
        self.port = port
        self.ps = process(argv=[f'./server.py', f'{port}' , '--cmd'])
        self.log_file = open("log/server" + f'{port}' +"_log.txt", "wb")
        Server.servers.append(port)

    def create_process(self)->None:
        while True : 
            pass
    
    def close(self):

        while True : 
            try:
                self.log_file.write(self.ps.recvline())
                self.log_file.flush()
            except:
                pass

        if self.ps.poll(block = True):
            self.ps.close()
class Client:
    users = []

    def __init__(self, username, infile):
        self.ps = None
        self.username = username
        self.ps = process(argv=['./client.py', '--cmd'])
        self.ps.sendline(b'1')
        self.ps.sendline(self.username.encode())
        self.ps.sendline(b'1')
        self.infile = open(infile, 'r')
        self.ps.sendline(b'2')
        self.ps.sendline(b'aa')
        Client.users.append(username)
        self.log_file = open("log/" + username+"_log.txt", "wb")


    def create_process(self)->None:
        while True :
            chunk = self.infile.readline()
            if chunk == '' : break
            #self.log_file.write(chunk.encode())
            #self.log_file.write(("File input : " + chunk).encode())
            self.ps.sendline(chunk.strip('\n').encode())

    def close(self):

        # for i in range(NUM_CLIENTS):
        while True : 
            try:
                self.log_file.write(self.ps.recvline())
                self.log_file.flush()
            except:
                pass
    
        if self.ps.poll(block = True):
            self.ps.close()

try : 
    servers = [Server(int(sys.argv[2])+i) for i in range(NUM_SERVERS)]
    clients = [Client(chr(97+i), sys.argv[1]) for i in range(NUM_CLIENTS)]
    print(clients)
    server_threads = [threading.Thread(target=Server.create_process, args = (server,)) for server in servers]
    client_threads = [threading.Thread(target=Client.create_process, args=(client,)) for client in clients]
    server_closing_threads = [threading.Thread(target=Server.close, args=(server,)) for server in servers]
    client_closing_threads = [threading.Thread(target=Client.close, args=(client,)) for client in clients]
    for thread in server_threads : 
        thread.start()

    for thread in client_threads:
        thread.start()

    # time.sleep(10)
    for thread in server_closing_threads : 
        thread.start()

    for thread in client_closing_threads:
        thread.start()

    for thread in server_threads:
        thread.join()

    for thread in client_threads:
        thread.join()

    # for c in clients:
    #     c.ps.sendline(b'exit')
    #     # c.log_file.write(c.ps.recv())
    #     # c.log_file.flush()

    for thread in closing_threads:
        thread.join()

except (BrokenPipeError, IOError):
    print ('BrokenPipeError caught', file = sys.stderr)