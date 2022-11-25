from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet

def generate_fernet(): 
    """
    This function is used for generation for fernet key
    
    
    :returns key: returns the generated key
    :rtype key: fernet key
    """ 
    key = Fernet.generate_key()
    return key

def generatekey():
    """
    This function is used to generate rsa private and public key and return it.
    
    :returns public_key: returns the rsa public key
    :rtype public_key: rsa_publickey
    :returns private_key: returns the rsa private key
    :rtype private_key: rsa_private_key
    """
    private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend())
    public_key = private_key.public_key()
    return(public_key,private_key)

default_pad = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),label=None)

def entergrp_key(username,grpname,cursor,private_key,public_key):
    """Enter the group key in the database of each user for this group

    
    :param username: The username with whom the key is shared
    :type username: string
    :param grpname: The group whose key is shared
    :type grpname: string
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
    :param private_key: private key of the user
    :type  private_key: rsa_private_key
    :param public_key: public key of the user
    :type public_key: rsa_public_key
    """
    insertmsgquery = f'''
    INSERT INTO  {username}(GroupName,public_key,private_key) VALUES (\'{grpname}\',\'{public_key}\', \'{private_key}\')'''
    cursor.execute(insertmsgquery)

def public_encode(public_key):
    """
    Deserialize the public key
    
    :param publickey: serialized public key
    :type publickey: rsa_public_key
    :returns publickey: unserialized public key
    :rtype publickey: rsa_public_key
    """
    return public_key.public_bytes(
           encoding=serialization.Encoding.PEM,
           format=serialization.PublicFormat.SubjectPublicKeyInfo )
    
def private_encode(private_key):
    """"
    Deserialize the private key
    
    :param privatekey: serialized private key
    :type privatekey: rsa_private_key
    :returns privatekey: unserialized private key
    :rtype privatekey: rsa_private_key
    """
    return private_key.private_bytes(
           encoding=serialization.Encoding.PEM,
           format=serialization.PrivateFormat.TraditionalOpenSSL,
           encryption_algorithm=serialization.NoEncryption()
    )
    
def private_key_decode(private_key):
    """
    Serialize the private key
    
    :param privatekey: unserialized private key
    :type privatekey: rsa_private_key
    :returns privatekey: serialized private key
    :rtype privatekey: rsa_private_key
    """
    
    private_key=private_key.encode('utf-8')
    private_key = serialization.load_pem_private_key(
        private_key, 
        password = None
    )
    return private_key

def public_key_decode(public_key):
    """
    Serialize the public key
    
    :param publickey: unserialized public key
    :type publickey: rsa_public_key
    :returns publickey: serialized public key
    :rtype publickey: rsa_public_key
    """
    public_key=public_key.encode('utf-8')
    public_key = serialization.load_pem_public_key(
        public_key
    )
    return public_key

def enter_my_key(username,cursor):
    """
    Enter the key in user local database using insert query.
    
    :param username: name of the user
    :type username: string
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
    
    """
    (public_key,private_key)=generatekey()
    public_key= public_encode(public_key).decode()
    private_key=private_encode(private_key).decode()
    insertmsgquery = f'''
    INSERT INTO  {username}info (public_key,private_key) VALUES (%s,%s);'''
    #cursor.execute(insertmsgquery,(public_key,private_key))
    return (public_key,private_key,insertmsgquery)