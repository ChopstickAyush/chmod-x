#! /usr/bin/env python3

import base64
import pycr
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
import hashlib


class RSA_(object):
    @classmethod
    def genRSA(cls):
        try:
            key = RSA.generate(1024, Random.new().read)  #generate Pub and Priv key
            public_key = key.publickey()  #export public key from the key
            return (key, public_key)
        except Exception as e:
            print("Error generating RSA keys")
            return e

    @classmethod
    def encrypt(cls, public_key=None, data=None):
        if public_key and data:
            try:
                return public_key.encrypt(data.encode(), 1)  #2nd arg is of no use. it can have any value
            except Exception as e:
                return e
        else:
            return None

    @classmethod
    def decrypt(cls, pri_key=None, data=None):
        if pri_key and data:
            try:
                return pri_key.decrypt(data).decode()
            except Exception as e:
                return e
        else:
            return None

class AES_(object):
    @classmethod
    def encrypt(cls, secret, data):
        BLOCK_SIZE = 32
        PADDING = '{'
        pad = lambda s : s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        cipher = AES.new(secret)
        encoded = EncodeAES(cipher, data)
        return encoded

    @classmethod
    def decrypt(cls, secret, data):
        BLOCK_SIZE = 32
        PADDING = '{'
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).decode().rstrip(PADDING)
        cipher = AES.new(secret)
        decoded = DecodeAES(cipher, data)
        return decoded

def hasher(key):
    hash_object = hashlib.sha512(key.encode())
    sha_hash = hash_object.hexdigest()
    hash_object = hashlib.md5(sha_hash.encode())
    md5_hash = hash_object.hexdigest() # digest is also known as hash
    return md5_hash
