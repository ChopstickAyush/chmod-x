import pdb
import socket
import select
import threading
import json
import re
import sys
import psutil
from load_balancer import cpuutil_load_balancer
# from xmlrpc.server import SimpleXMLRPCServer

from groups import *

current_process = psutil.Process()


HEADER_LENGTH = 10
LARGEST_PACKET_LENGTH = 1024

IP = "127.0.0.1"
PORT = int(sys.argv[1])


class Client:
    socket = None
    userdetails = None
    #public_key = None

    def __init__(self, socket, userdetails):
        self.socket = socket
        self.userdetails = userdetails
        #self.public_key = public_key


# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')


def send_message_in_packets(client_socket,message,header ,length):

    client_socket.send(header)
    while length > LARGEST_PACKET_LENGTH:
          length -= LARGEST_PACKET_LENGTH
          client_socket.send(message[:LARGEST_PACKET_LENGTH])
          message = message[LARGEST_PACKET_LENGTH:]
    if length > 0:
        client_socket.send(message)
    print('SEND SUCESSFULL')
    
    return

# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH+1)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        filtered_msg = message_header.decode('utf-8').strip()
        # print(filtered_msg)
        # Convert header to int value
        message_length = int(filtered_msg[1:])
        message = "".encode('utf-8')
        # print('here1')
        while message_length > LARGEST_PACKET_LENGTH:
            # print('here2')
            message += client_socket.recv(LARGEST_PACKET_LENGTH)
            message_length -= LARGEST_PACKET_LENGTH

        if message_length > 0:
            # print('here3',message_length)
            msg = client_socket.recv(message_length)
            # print(msg)
            message += msg

        # print(message)
        # Return an object of message header and message data
        return {'header': message_header, 'data': message}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False





def log_cpu_util():
    while True:
        cpuutil_load_balancer.update_port_index(current_process.cpu_percent(1),PORT)



perf_thread = threading.Thread(target=log_cpu_util, )
perf_thread.start()

while True:
   
    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            # user = receive_message(client_socket)
            userpass = receive_message(client_socket)
            # If False - client disconnected before he sent his name
            if userpass is False:
                continue

            userdetails = json.loads(userpass['data'])

            # err_1 validation failed
            if userdetails['token'] == 'join':
          
                if not validate(userdetails['user'], userdetails['pass'], cursor):
                    client_socket.send("err_1".encode('utf-8'))
                    continue
                else:
                    client_socket.send("suc_0".encode('utf-8'))

            elif userdetails['token'] == 'register':

                if check_user_name(userdetails['user'], cursor):
                    client_socket.send("err_2".encode('utf-8'))
                else:
                    add_user(userdetails['user'], userdetails['pass'],userdetails['public_key'] ,cursor)
                    # enter_group(userdetails['user'], 'Test')
                    client_socket.send("suc_0".encode('utf-8'))
                continue
            
            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = Client(
                client_socket, userdetails['user'])

            print('Accepted new connection from {}:{}, username: {}'.format(
                *client_address, userdetails['user']))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)
            
            # print(message)
            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(
                    clients[notified_socket].userdetails))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            username = clients[notified_socket].userdetails
            # print(message['header'][0])
            if message['header'].decode('utf-8')[0] == 'R':
                details = json.loads(message['data'].decode('utf-8'))
                group_name = details['groupname']

                users_list_add = details['members_to_add']
                users_list_remove = details['members_to_remove']
                
                users_lst_add = []
                users_lst_remove = []
                for i in users_list_add:
                    if not check_user_name(i, cursor) or (i == username):
                        print(i, ' is and invalid username!')
                    else:
                        users_lst_add.append(i)
                for i in users_list_remove:
                    if not check_user_name(i, cursor):
                        print(i, ' is and invalid username!')
                    else:
                        users_lst_remove.append(i)

                users_lst_add.append(username)
                users_lst_add = users_lst_add[::-1]
                mydict={}
                # enter_group(username,username ,group_name)
                for i in users_lst_add:
                    enter_group(i,username ,group_name)
                    key=f'''Select public_key from Users where Name=\'{i}\''''
                    cursor.execute(key)
                    rows = cursor.fetchall()[0]
                    row = rows[0]
                    mydict[i] = row
                # print(mydict)

                # Assuming no person called groupname
                mydict["groupname"] = group_name

                send_public_keys = json.dumps(mydict)    
                for i in clients : 
                    if clients[i].userdetails== username:
                        # print(username)
                        message_to_send= send_public_keys.encode('utf-8')
                        message_len = len(message_to_send)   
                        message_=f"L{message_len:<{HEADER_LENGTH}}".encode('utf-8')+message_to_send
                        # print(message_)
                        i.send(message_)
                        break

                for i in users_lst_add:
                    enter_group(i,username ,group_name)
                for i in users_lst_remove:
                    remove_users_from_group(i,group_name,username,cursor)
                    set_current_group(i,None,cursor,True)
                    remove_msg= f"You have been removed from {group_name}!".encode('utf-8')
                    message_len = len(message_to_send)   
                    message_=f"R{message_len:<{HEADER_LENGTH}}".encode('utf-8')+remove_msg
                    if i == username:
                       for cs in clients:
                            if get_current_group(clients[cs].userdetails,cursor) == group_name:
                                set_current_group(clients[cs].userdetails,None,cursor,True)
                                cs.send(message_) 
                                users_list_remove = []    
                    for cs in clients:
                        if clients[cs].userdetails == i:
                            cs.send(message_)

            elif message['header'].decode('utf-8')[0] == 'J':
                group_name = message['data'].decode('utf-8')
                # print(username, group_name)
                if not check_group(group_name,username,cursor):
                    msg = 'err_0'.encode('utf-8')
                    header = f"E{len(msg):<{HEADER_LENGTH}}".encode('utf-8') 
                    notified_socket.send(header + msg)
                    continue
                msg = group_name.encode('utf-8')
                header = f"E{len(msg):<{HEADER_LENGTH}}".encode('utf-8') 
                notified_socket.send(header + msg)
                
                set_current_group(clients[notified_socket].userdetails,group_name,cursor)
                for cs in clients:
                    # But don't sent it to sender
                    if cs != notified_socket and get_current_group(clients[cs].userdetails,cursor) == group_name:
                        # Send user and message (both with their headers)
                        other_user = clients[cs].userdetails
                        join_message_to_others = (
                            username + " has joined!").encode('utf-8')
                        join_message_len_1 = len(join_message_to_others)
                        message_1 = f"J{join_message_len_1:<{HEADER_LENGTH}}".encode(
                            'utf-8') + join_message_to_others

                        join_message_to_new_user = (
                            other_user + " has joined!").encode('utf-8')
                        join_message_len_2 = len(join_message_to_new_user)
                        message_2 = f"J{join_message_len_2:<{HEADER_LENGTH}}".encode(
                            'utf-8') + join_message_to_new_user
                        # We are reusing here message header sent by sender, and saved username header send by user when he connected
                        cs.send(message_1)
                        notified_socket.send(message_2)
 
                        
                key = get_encoded_key(username, group_name,cursor)
                message_to_send = json.dumps({"fernet_key" : key, "groupname" : group_name}).encode('utf-8')
                # print({"fernet_key" : key, "groupname" : group_name})
                message_len = len(message_to_send)
                message_ = f"Z{message_len:<{HEADER_LENGTH}}".encode('utf-8') + message_to_send
                notified_socket.send(message_)


                messages = pendingmsg(username, group_name, cursor)

                if messages is not None:
                
                    for usr, msg in messages:
                        counter =  get_message_counter(usr,group_name,msg,cursor)
                        message_to_send = json.dumps({'message': msg, 'user': usr, 'counter' : counter}).encode('utf-8')
                        message_len = len(message_to_send)
                        message_ = f"M{message_len:<{HEADER_LENGTH}}".encode(
                            'utf-8') + message_to_send
                        notified_socket.send(message_)

            elif message['header'].decode('utf-8')[0] == 'M' or message['header'].decode('utf-8')[0] == 'I':
                # Get user by notified socket, so we will know who sent the message
                # user = clients[notified_socket]

                
                group_name = get_current_group(clients[notified_socket].userdetails,cursor)
                counter = None
                if (message['header'].decode('utf-8')[0] == 'M') :
                    sendmsg(username, group_name , cursor,
                        message["data"].decode("utf-8"))
                    print(f'Received message from {username} in group{group_name}')

                    counter = get_message_counter(username,group_name,message["data"].decode("utf-8"),cursor)
                # Iterate over connected clients and broadcast message
                for cs in clients:
        
                    # But don't sent it to sender
                    if cs != notified_socket and get_current_group(clients[cs].userdetails,cursor) == group_name:

                        # Send user and message (both with their headers)
                        # pdb.set_trace()
                        message_to_send = None
                        
                        header = None
                        message_to_send = None
                        if (message['header'].decode('utf-8')[0] == 'M') :
                            message_to_send = json.dumps({'message':  message['data'].decode(), 'user': username, 'counter' : counter}).encode('utf-8')
                            message_len = len(message_to_send)
                            header = f"M{message_len:<{HEADER_LENGTH}}".encode(
                                'utf-8') 
                        elif (message['header'].decode('utf-8')[0] == 'I') :
                            message_to_send = message['data']
                            message_len = len(message_to_send)
                            header = f"I{message_len:<{HEADER_LENGTH}}".encode(
                                'utf-8')
                        # We are reusing here message header sent by sender, and saved username header send by user when he connected
                        # cs.send(message_)
                        send_message_in_packets(cs,message_to_send,header,message_len)
                
            elif message['header'].decode('utf-8')[0] == 'Q':
                    # Get user by notified socket, so we will know who sent the message
                # user = clients[notified_socket]
                
             
                y=(json.loads(message["data"].decode("utf-8")))
                group_name=y["groupname"]

                for i in y : 
                    if i == "groupname" : continue
                    x=y[i]
                    x = x.replace("'","''")
                    x = x.replace("\\","\\\\")
                 
                    set_private_key(i, group_name, x,cursor)
            elif message['header'].decode('utf-8')[0] == 'V':
                 mesg = json.loads(message["data"].decode("utf-8"))
                 update_client_counter(mesg['user'],mesg['group_name'],mesg['counter'],cursor)
            elif message['header'].decode('utf-8')[0] == 'C':
           
                 
                 message_to_send = "Yes".encode('utf-8')
                 message_len = len(message_to_send)
                 message_ = f"C{message_len:<{HEADER_LENGTH}}".encode(
                                'utf-8') + message_to_send    
                 set_current_group(username,None,cursor,True)
                 notified_socket.send(message_)
            


    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
