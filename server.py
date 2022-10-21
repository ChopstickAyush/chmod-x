import  socket

class server:
    def server(self):
        pass
        
    def makeserver(self,IP,Port,Client):
        self.s=socket.socket()
        self.s.bind((IP,Port))
        self.s.listen(Client)
        return self.s
        
    def addclient(self):
        while True:
            c,addr=self.s.accept()
            return self.start_chat(c,addr)
            
    def start_chat(self,c,addr):
        c.send(bytes('hi','utf-8'))
        while True:
            b=c.recv(1024).decode()
            print(b)
            if(b=="0"):
                break
            a=input()
            if(a=="0"):
                break
            c.send(bytes(a,'utf-8'))
        c.close()
        
A=server()
A.makeserver('localhost',9993,5)
A.addclient()

        


        
