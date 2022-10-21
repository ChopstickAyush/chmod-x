import socket
c=socket.socket()
c.connect(('localhost',9993))
while(True):        
        myname=c.recv(1024).decode()
        print(myname)
        a=input()
        if(myname=='0'):
            break
        c.send(bytes(a,'utf-8'))
        if(myname=='0'):
            break
c.close()
