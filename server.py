import pdb
import socket
import select

from groups import *


HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234


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

# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False



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
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

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
            
            userdetails = userpass['data'].decode('utf-8').split("_")

            # err_1 validation failed
            if userdetails[0] == 'join':
                if not validate(userdetails[1],userdetails[2],cursor):
                    client_socket.send("err_1".encode('utf-8'))
                    continue
                else:
                    client_socket.send("suc_0".encode('utf-8'))

            elif userdetails[0] == 'register':
                if check_user_name(userdetails[1],cursor):
                    client_socket.send("err_2".encode('utf-8'))
                else:
                    add_user(userdetails[1],userdetails[2],cursor)
                    enter_group(userdetails[1],'Test')
                    client_socket.send("suc_0".encode('utf-8'))
                continue
            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = userdetails[1]
            # if user is not None:
            # client_socket.send(user['header'] + userdetails[1])

            for cs in clients:
                # But don't sent it to sender
                if cs != client_socket:
                    # Send user and message (both with their headers)
                    other_user = clients[cs]
                    join_message_to_others=(userdetails[1] +" has joined!").encode('utf-8')
                    join_message_len_1 = len(join_message_to_others)
                    message_1 = f"{join_message_len_1:<{HEADER_LENGTH}}".encode('utf-8') + join_message_to_others

                    print(join_message_to_others.decode('utf-8'))
                    join_message_to_new_user = (other_user +" has joined!").encode('utf-8')
                    join_message_len_2 = len(join_message_to_new_user)
                    message_2 = f"{join_message_len_2:<{HEADER_LENGTH}}".encode('utf-8') + join_message_to_new_user
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    cs.send(message_1)
                    client_socket.send(message_2)
            
            # userloop(cursor)
            
            messages = pendingmsg(userdetails[1],'Test',cursor)

            if messages is not None:
                # print(messages)
                for usr,msg in messages:
                    message_to_send = (usr+": " + msg).encode('utf-8')
                    message_len = len(message_to_send)
                    message_ = f"{message_len:<{HEADER_LENGTH}}".encode('utf-8') + message_to_send
                    client_socket.send(message_)
            #join_group(user_name=userdetails[1],cursor=cursor)
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, userdetails[1]))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            # user = clients[notified_socket]

            # print(userdetails[1])
            username = clients[notified_socket]
            sendmsg(username,'Test',cursor,message["data"].decode("utf-8"))

            #sendmsg(username,'Test',cursor,message["data"].decode("utf-8"),counter)
            #counter = counter+1
            
            print(f'Received message from {username}: {message["data"].decode("utf-8")}')
            
            # Iterate over connected clients and broadcast message
            for client_socket in clients:

                # But don't sent it to sender
                if client_socket != notified_socket:

                    # Send user and message (both with their headers)
                    # pdb.set_trace()
                    message_to_send = (username+": ").encode('utf-8') + message['data']
                    message_len = len(message_to_send)
                    message_ = f"{message_len:<{HEADER_LENGTH}}".encode('utf-8') + message_to_send
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(message_)

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]