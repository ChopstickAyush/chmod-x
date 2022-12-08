#!/usr/bin/python3
import subprocess
import threading
from pwn import *

def server_start()  : 
    server = f'python3 server.py 1235'
    os.system(server)

def start_client(i) :
    try : 
        f = open("in.txt", "w")
        f.write(f'2\n{i}\n1')
        f.close()
        cmd = f'python3 client.py 1235 1 < in.txt'
        os.system(cmd)
    except EOFError : 
        pass

server_start_thread = threading.Thread(target=server_start)
server_start_thread.start()

for i in range(100) : 
    
    # client_start_thread = threading.Thread(target=start_client, args = (i+1,))
    # client_start_thread.start()
    start_client(i+1)

pid = os.getpid()
os.kill(pid, signal.SIGKILL)

