from myrsa import *
import pickle
a=generate_fernet()
key = Fernet(a)
print(key.decrypt(key.encrypt(b"hello")))

# b = str(a)
# c = eval(b)
# d = b.encode()
# print(a, type(a))
# print(b, type(b))
# print(c, type(c))
# print(d, type(d))
# e = c.encode()
# print(e, type(e))
