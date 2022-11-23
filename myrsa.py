from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet

def generate_fernet():  
    key = Fernet.generate_key()
    return key

def generatekey():
    private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend())
    public_key = private_key.public_key()
    return(public_key,private_key)

default_pad = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),label=None)

def entergrp_key(username,grpname,cursor,private_key,public_key):
    insertmsgquery = f'''
    INSERT INTO  {username}(GroupName,public_key,private_key) VALUES (\'{grpname}\',\'{public_key}\', \'{private_key}\')'''
    cursor.execute(insertmsgquery)

def public_encode(public_key):
    return public_key.public_bytes(
           encoding=serialization.Encoding.PEM,
           format=serialization.PublicFormat.SubjectPublicKeyInfo )
    
def private_encode(private_key):
    return private_key.private_bytes(
           encoding=serialization.Encoding.PEM,
           format=serialization.PrivateFormat.TraditionalOpenSSL,
           encryption_algorithm=serialization.NoEncryption()
    )
    
def private_key_decode(private_key):
    private_key=private_key.encode('utf-8')
    private_key = serialization.load_pem_private_key(
        private_key, 
        password = None
    )
    return private_key

def public_key_decode(public_key):
    public_key=public_key.encode('utf-8')
    public_key = serialization.load_pem_public_key(
        public_key
    )
    return public_key

def enter_my_key(username,cursor):
    (public_key,private_key)=generatekey()
    public_key= public_encode(public_key).decode()
    private_key=private_encode(private_key).decode()
    insertmsgquery = f'''
    INSERT INTO  {username}info (public_key,private_key) VALUES (%s,%s);'''
    #cursor.execute(insertmsgquery,(public_key,private_key))
    return (public_key,private_key,insertmsgquery)