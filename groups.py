from codecs import latin_1_decode
import bcrypt
import pdb
from re import L
import psycopg2
import random
import rsa

#establishing the connection
conn = psycopg2.connect(
   database="postgres", user='postgres', password='1234', host='127.0.0.1', port= '5432'
)
conn.autocommit = True

def create_tables(cursor) :
    """
    This function creates the server side database for fastchat. It contains 4 tables:
    
    - Users
    
    - UserGroupInfo
    
    - Messages
    
    -Groups
    
    :param cursor: This is the passed cursor to execute the create query.
    :type cursor: socket.cursor
    
    """

    create ='''
       
        CREATE TABLE IF NOT EXISTS Users (
        Name VARCHAR ( 20 ) PRIMARY KEY,
        Password VARCHAR ( 72 ) NOT NULL,
        CurrentGroup VARCHAR ( 20 ) DEFAULT NULL,
        public_key VARCHAR(20000)
        );

       
        CREATE TABLE IF NOT EXISTS UserGroupInfo (
        Name VARCHAR ( 20 ),
        GroupName VARCHAR ( 20 ),
        Isadmin BOOLEAN, 
        Coded_Key TEXT ,
        Time INT DEFAULT 0,
        FOREIGN KEY (Name)
        REFERENCES Users (Name),
        FOREIGN KEY (GroupName)
        REFERENCES Groups (GroupName)
        );

        
        CREATE TABLE IF NOT EXISTS Messages (
        GroupName VARCHAR( 20 ), 
        msg VARCHAR ( 10000 ), 
        Name VARCHAR ( 20 ),
        Time SERIAL
        );

      
        CREATE TABLE IF NOT EXISTS Groups (
        GroupName VARCHAR ( 20 ) PRIMARY KEY,
        public_key VARCHAR(1000),
        private_key VARCHAR(1000)
        );
    '''

    #Creating a database
    cursor.execute(create)
    print("Database created successfully........")

    return

def sendmsg(username,grpname,cursor,message):
    """
    Insert query for storing of message at server along with user , group in message table.

    :param username: Username of the sender of the message
    :type username: string
    :param grpname: Groupname to which message has been send
    :type grpname: String
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
    :param message: message sent by the user
    :type message: string
    """
    insertmsgquery = f'''
    INSERT INTO  Messages(GroupName, msg, Name) VALUES (\'{grpname}\',\'{message}\', \'{username}\')'''
    cursor.execute(insertmsgquery)
    
def get_message_counter(username, grpname, message,cursor):
    """
    Select query to get the time of the message with the given username, message and groupname.
    
    :param username: Username of the sender of the message
    :type username: string
    :param grpname: Groupname to which message has been send
    :type grpname: String
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
    :param message: message sent by the user
    :type message: string

    :returns counter: Time (serial number of the message).
    """
    getcounterquery = f'''
    Select Time from Messages where Name=\'{username}\' AND GroupName=\'{grpname}\' AND msg = \'{message}\''''
    cursor.execute(getcounterquery)
    time = cursor.fetchone()[0]
    return time

def pendingmsg(username, grpname, cursor) :
    '''
    Select query to get the list of pending message for a given user in a specified group.
    
    :type grpname : string
    :param grpname: group for which pending message of given user has to be found
    :type username: string
    :param username: username for which pending message has to be found
    :type cursor: socket.cursor
    
    :returns rows: list of pending messages
    :rtype rows: list of strings
    
    '''

    gettimequery = f'''
    Select Time from UserGroupInfo where Name=\'{username}\' AND GroupName=\'{grpname}\''''
    cursor.execute(gettimequery)
    time = cursor.fetchone()
    # print(time)
    if time is None :
        print("No pending messages")
        return
    else : 
        time = time[0]

    # using this time to get list of messages after this time. 
    print(time)
    # pdb.set_trace()
    getmessagequery = f'''
    Select Name, msg from Messages where Time > {time} AND GroupName = \'{grpname}\'
    '''
    cursor.execute(getmessagequery)
    rows = cursor.fetchall()

    # Update the last seen message 
    # curtimequery = f'''Select Max(Time) from Messages where GroupName = \'{grpname}\' '''
    # cursor.execute(curtimequery)
    # curtime = cursor.fetchone()

    # if len(curtime) > 0:
    #     if  curtime[0] is not None:
    #         updatetimequery = f'''
    #         Update UserGroupInfo SET Time = ({curtime[0]}) WHERE Name =\'{username}\' AND GroupName = \'{grpname}\'
    #         '''
    #         cursor.execute(updatetimequery)
    return rows

    
def creategrp(grpname, names, cursor) :
    '''
    Insert query for creation of a group and adding members and setting up the admin.
    
    :param name: list of all people to be added with admin as first entry
    :type name: list of strings
    :param grpname: groupname to be created
    :type grpname: string
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
    
    '''

    # Checking if the group name is new ! 
    
    grpquery = f'''
    Select count(*) from Groups where GroupName = \'{grpname}\'
    '''
    cursor.execute(grpquery)
    count = cursor.fetchone()[0]
    #pdb.set_trace()
    if count != 0 : return False
    
    # Now, creating the group .

    public_key, private_key = rsa.newkeys(random.randint(100,500))
    creategrpquery = f'''
    INSERT INTO Groups (GroupName, public_key, private_key) VALUES (\'{grpname}\', \'{public_key}\', \'{private_key}\')
    '''
    cursor.execute(creategrpquery)

    for i in range(len(names)) : 
        
        if i == 0 : 
            insertnamesquery = f'''
            INSERT INTO UserGroupInfo (Name, GroupName, IsAdmin) VALUES (\'{names[i]}\', \'{grpname}\', TRUE)
            '''
            cursor.execute(insertnamesquery)
        else : 
            insertnamesquery = f'''
            INSERT INTO UserGroupInfo (Name, GroupName, IsAdmin) VALUES (\'{names[i]}\', \'{grpname}\', FALSE)
            '''
            cursor.execute(insertnamesquery)

    return 
            
def check_group(grp, username, cursor) :
    """
    Bool type function to Check if the given user is present in a given group by using
    select query and comparison.
    
    :param grp: name of the group
    :type name: string
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
    
    :returns: True/False depending upon whether user is present or not.
    :rtype: bool
    """
    searchgrpquery = f'''
    Select count(*) from Groups where GroupName = \'{grp}\'
    '''
    cursor.execute(searchgrpquery)
    count = cursor.fetchone()[0]

    if count == 0 : 
        print("Not A Valid Group Name") 
    else : 
        searchuserquery = f'''
        Select count(*) from UserGroupInfo where Name = \'{username}\' AND GroupName = \'{grp}\'
        '''
        cursor.execute(searchuserquery)
        usercount = cursor.fetchone()[0]
        if usercount == 0 : 
            return False
        else : 
            return True


def check_user_name(name, cursor) :
    """
    Check if someone exists with that given username using select query and comparison.
    
    :param name: name of the user
    :type name: string
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
    
    :returns: True/False depending upon whether user is present or not.
    :rtype: bool
    """
    check_user = f"Select * from Users where Name = '{name}'"
    cursor.execute(check_user)
    lst = cursor.fetchone()
    if (lst == None): return False
    else : return lst


def validate(name, password ,cursor) :
    """
    Validate the password of the user by select query and comparison.

    :param name: name of the user
    :type name: string
    :param name: password of the user
    :type name: string
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor

    :returns: True/False depending upon the validation
    :rtype: bool
    """
    validate = f"Select Name, Password from Users where Name = '{name}'"
    cursor.execute(validate)
    lst = cursor.fetchone()
    # print(lst)
    if (lst == None): return False
    else:
        if bcrypt.checkpw(password.encode('utf-8'),lst[1].encode('utf-8')):
            return True
        return False

# def add_public_key(user,publickey,cursor):
#     insert = f'''
#         UPDATE Users SET public_key='{publickey}' WHERE Name = '{user}'
#         '''
#     cursor.execute(insert)

def add_user(name, password, public_key,  cursor):
    """
    Insert query to add new users to the database.
    
    :param name: name of the new user
    :type name: string
    :param name: encrypted password of the new user
    :type name: string
    :param public_key: public_key of the new user
    :type public_key: string
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
        
    """
    if not check_user_name(name,cursor):
        insert = f'''
                INSERT INTO Users (Name, Password, public_key) VALUES ('{name}', '{password}', '{public_key}');
                '''
        cursor.execute(insert)
        print('User Added!')


def remove_users_from_group(name,grpname,admin,cursor):
    """
    DELETE query to remove members from a group.
    
    :param name: list of people to be removed 
    :type name: list of strings
    :param admin: name of the admin
    :type admin: string 
    :param grpname: groupname of the names
    :type grpname: string
    :param cursor: cursor to execute query
    :type cursor: cursor.cursor
    
    """
    grpquery = f'''
    Select count(*) from UserGroupInfo where GroupName = \'{grpname}\'
    '''
    cursor.execute(grpquery)
    count = cursor.fetchone()[0]
    #pdb.set_trace()
    if count == 0 : 
        return
    else:
        getadminquery = f'''
            Select Name FROM UserGroupInfo WHERE Isadmin = TRUE
            '''
        cursor.execute(getadminquery)

        Admin = cursor.fetchone()[0]
        # to do proper error messages
        if Admin != admin:
            return
        checkAdmin = f'''
            Select Isadmin FROM UserGroupInfo WHERE Name =\'{name}\' AND GroupName =\'{grpname}\'
            '''
        cursor.execute(checkAdmin)

        result = cursor.fetchone()[0]

        if result == True:
            query = f'''DELETE FROM UserGroupInfo WHERE GroupName =\'{grpname}\' '''
            cursor.execute(query)
            query = f'''DELETE FROM Groups WHERE GroupName =\'{grpname}\' '''
            cursor.execute(query)
            return
        else:
            query = f'''DELETE FROM UserGroupInfo WHERE Name =\'{name}\' AND GroupName =\'{grpname}\' '''
            cursor.execute(query)
            return

    

#temporary function
#it doesnt check if the user is already present or not
def enter_group(name,admin,grpname):
    """
    Insert query to add members in a group.
    
    :param name: list of all people 
    :type name: list of strings
    :param admin: name of the admin
    :type admin: string 
    :param grpname: groupname to be created
    :type grpname: string
    """
    
    grpquery = f'''
    Select count(*) from UserGroupInfo where GroupName = \'{grpname}\'
    '''
    cursor.execute(grpquery)
    count = cursor.fetchone()[0]
    if count == 0 : 
        public_key, private_key = rsa.newkeys(random.randint(100,500))
        creategrpquery = f'''
        INSERT INTO Groups (GroupName, public_key, private_key) VALUES (\'{grpname}\', \'{public_key}\', \'{private_key}\')
        '''
        cursor.execute(creategrpquery)
        insertnamesquery = f'''
            INSERT INTO UserGroupInfo (Name, GroupName, IsAdmin) VALUES (\'{name}\', \'{grpname}\', TRUE)
            '''
        cursor.execute(insertnamesquery)
    else:
        getadminquery = f'''
            Select Name FROM UserGroupInfo WHERE Isadmin = TRUE AND GroupName = \'{grpname}\'
            '''
        cursor.execute(getadminquery)

        Admin = cursor.fetchone()[0]
        if Admin != admin:
            return
        checkquery = f'''
            Select * FROM UserGroupInfo WHERE Name =\'{name}\' AND GroupName =\'{grpname}\'
            '''
        cursor.execute(checkquery)
        results = cursor.fetchall()
        if len(results) !=0 :
            return
        insertnamesquery = f'''
            INSERT INTO UserGroupInfo (Name, GroupName, IsAdmin) VALUES (\'{name}\', \'{grpname}\', FALSE)
            '''
        cursor.execute(insertnamesquery)

def set_private_key(username , groupname, privatekey,cursor):
    """
    Update query to set the private_key of the user.

    :param username: name of the user
    :type username: string
    :param groupname: groupname of the user
    :type groupname: string
    :param privatekey: private key to be set of the user
    :type privatekey: string
    :param cursor: cursor to execute the query
    :type cursor: socket.cursor
    
    """
    query = f'''UPDATE UserGroupInfo Set Coded_Key = \'{privatekey}\' WHERE Name =\'{username}\' AND GroupName=\'{groupname}\''''
    cursor.execute(query)
    
def set_current_group(name,grpname,cursor):
    """
    Update query to set current group of the user.

    :param name: name of the user
    :type name: string
    :param groupname: groupname to be set
    :type groupname: string
    :param cursor: cursor to execute the query
    :type cursor: socket.cursor
    
    """
    
    query = f'''UPDATE Users Set CurrentGroup = \'{grpname}\' WHERE Name =\'{name}\''''
    cursor.execute(query)

def get_current_group(name,cursor):
    """
    Select query to get current group of the user.

    :param name: name of the user
    :type user: string
    :param cursor: cursor to execute the query
    :type cursor: socket.cursor

    :returns result: current groupname
    :rtype result: strinng
    """
    query = f'''SELECT CurrentGroup From Users WHERE Name =\'{name}\''''
    cursor.execute(query)
    result = cursor.fetchone()[0]
    return result

def get_encoded_key(name,grpname,cursor):
    """
    Select query to get the enrypted fernet key of the group, the key is coded by 
    name's pulic key. 
    
    :type grpname : string
    :param grpname: groupname for which fernet key has to be fetched
    :type name: string
    :param name: username whose public key has encrypted the fernet key
    :param cursor: cursor to execute the query
    :type cursor: socket.cursor
    
    :returns result: encrypted fernet key
    :rtype result: string
    
    """
    query = f'''SELECT Coded_Key From UserGroupInfo WHERE Name =\'{name}\' AND GroupName = \'{grpname}\' '''
    cursor.execute(query)
    result = cursor.fetchone()[0]
    result = result.replace("\\\\","\\")
    return result

def update_client_counter(name,grpname,counter,cursor):
    """
    Update query to update the time counter of usergroupinfo table showing that the user have seen
    that message.
    
    :type grpname : string
    :param grpname: groupname of user
    :type username: string
    :param username: name of the user
    :param cursor: cursor to execute the query
    :type cursor: socket.cursor

    """
    timequery = f'''SELECT Time From UserGroupInfo WHERE Name =\'{name}\' AND GroupName = \'{grpname}\''''
    cursor.execute(timequery)
    time = cursor.fetchone()[0]
    max_time = max(time,counter)

    update_query = f'''  
    UPDATE UserGroupInfo SET Time = ({max_time}) WHERE Name =\'{name}\' AND GroupName = \'{grpname}\' 
    '''
    cursor.execute(update_query)
    


cursor = conn.cursor()

#Preparing query to create a database
create_tables(cursor)
#creategrp()
# print('Welcome')

