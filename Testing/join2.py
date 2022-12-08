#!/usr/bin/python3
import os
import threading
from pwn import *

def server_start()  : 
    server = f'python3 server.py 1236'
    os.system(server)

def start_client(i, str1) :
    try : 
        f = open("in.txt", "w")
        f.write(f'1\n{i}\n1\n1\naa\n' + str1 + '\n' + '\n')
        f.close()
        cmd = f'python3 client.py 1236 1 < in.txt'
        os.system(cmd)
    except : 
        pass

server_start_thread = threading.Thread(target=server_start)
server_start_thread.start()

lst = list(range(100))
str1 = ''
for i in lst : 
    str1 += str(i+1) + ','
str1 = str1[:-1]
start_client('1', str1)

pid = os.getpid()
os.kill(pid, signal.SIGKILL)
