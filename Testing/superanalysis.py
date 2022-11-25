import os
import multiprocessing
import time
from pwn import *


# Different variations of inputs, generate inputs, call analysis.py on that
num_clients = 2
num_servers = 1

genlog = f"python3 testing.py input.txt 1234 {num_clients} {num_servers}"
os.system(genlog)

time.sleep(100)

test = f"python3 ./analysis.py > results.txt"
os.system(test)

with open("results.txt") as f : 
    lines = f.readlines()

print(lines)