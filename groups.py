from codecs import latin_1_decode
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

    create ='''
        DROP TABLE IF EXISTS Users cascade; 
        CREATE TABLE IF NOT EXISTS Users (
        Name VARCHAR ( 20 ) PRIMARY KEY,
        Password VARCHAR ( 20 ) NOT NULL
        );

        DROP TABLE IF EXISTS UserGroupInfo cascade;
        CREATE TABLE IF NOT EXISTS UserGroupInfo (
        Name VARCHAR ( 20 ),
        GroupName VARCHAR ( 20 ),
        Isadmin BOOLEAN, 
        Time INT DEFAULT 0,
        FOREIGN KEY (Name)
        REFERENCES Users (Name),
        FOREIGN KEY (GroupName)
        REFERENCES Groups (GroupName)
        );

        DROP TABLE IF EXISTS Messages cascade;
        CREATE TABLE IF NOT EXISTS Messages (
        GroupName VARCHAR( 20 ), 
        msg VARCHAR ( 100 ), 
        Name VARCHAR ( 20 ),
        Time SERIAL
        );

        DROP TABLE IF EXISTS Groups cascade;
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
    insertmsgquery = f'''
    INSERT INTO  Messages(GroupName, msg, Name) VALUES (\'{grpname}\',\'{message}\', \'{username}\')'''
    cursor.execute(insertmsgquery)
    


def pendingmsg(username, grpname, cursor) :
    '''
    grpname : string
    username : string
    returns : list of strings
    '''

    gettimequery = f'''
    Select Time from UserGroupInfo where Name=\'{username}\' AND GroupName=\'{grpname}\''''
    cursor.execute(gettimequery)
    time = cursor.fetchone()
    print(time)
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
    curtimequery = f'''Select Max(Time) from Messages where GroupName = \'{grpname}\' '''
    cursor.execute(curtimequery)
    curtime = cursor.fetchone()

    if len(curtime) > 0:
        if  curtime[0] is not None:
            updatetimequery = f'''
            Update UserGroupInfo SET Time = ({curtime[0]})
            '''
            cursor.execute(updatetimequery)
   

    

    return rows

def enter(user_name,grp_name,cursor):
    messages = pendingmsg(user_name,grp_name,cursor)
    if messages is not None:
        print(messages)
    
    print("start chat")

    
def creategrp(grpname, names, cursor) :
    '''
    grpname : string
    names : list of strings
    output : True if created, False if already exists
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

def join_group(user_name,cursor):
    while True:
        print('Enter OPTION \n 1. Enter a group \n 2. Join a group  \n 3. Exit')
        x = int(input(">>>"))
        if x == 1:
            print("Enter Group Name")
            grp=input(">>>>")
            check_group(grp, user_name, cursor)
                
        if x == 2 :
            grpname=input("Enter Group Name")
            L1=[user_name]
            print("Enter Members ")
            print("Enter 1. Member Name \n 2. 0 to create group ")
            x=input(">>>")
            while x!="0":
                while check_user_name(x, cursor)==False:
                    print("NOT A member Enter again")
                    x=input(">>>")
                L1.append(x)
                print("Enter 1.Member Name \n 2.0 to creste group")
                x=input(">>>")           
            a= creategrp(grpname,L1,cursor)
            while a==False:
                print("Name Already In Use. Try another")
                print("Enter Groupname")
                grpname=input(">>>")
                a= creategrp(grpname,L1,cursor)
            if a==True:
                print("group created")
            
        if x==3:
            break
            
def check_group(grp, username, cursor) :

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
            print("Not A group Member") 
        else : 
            enter(grp,username,cursor)


def check_user_name(name, cursor) :
    check_user = f"Select * from Users where Name = '{name}'"
    cursor.execute(check_user)
    lst = cursor.fetchone()
    if (lst == None): return False
    else : return lst


def validate(name, password ,cursor) :
    validate = f"Select * from Users where Name = '{name}' and Password= '{password}'"
    cursor.execute(validate)
    lst = cursor.fetchone()
    if (lst == None): return False
    else : return True


def add_user(name, password, cursor):
    
    if not check_user_name(name,cursor):
        insert = f'''
                INSERT INTO Users (Name, Password) VALUES ('{name}', '{password}');
                '''
        cursor.execute(insert)
        print('User Added!')

def get_all_users(cursor,ex=None):
    if ex is None:
        query = f'''SELECT Name From Users;'''
    else:
        query = f'''SELECT Name From Users WHERE Name != \'{ex}\''''
    cursor.execute(query)
    names = []
    lst = cursor.fetchall()
    if (lst == None): return []
    else:
        for i in lst:
            names.append(i[0])
        return names


#temporary function
#it doesnt check if the user is already present or not
def enter_group(name,grpname):
    grpquery = f'''
    Select count(*) from UserGroupInfo where GroupName = \'{grpname}\'
    '''
    cursor.execute(grpquery)
    count = cursor.fetchone()[0]
    #pdb.set_trace()
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
        checkquery = f'''
            Select * FROM UserGroupInfo WHERE Name =\'{name}\' AND GroupName =\'{grpname}\'
            '''
        cursor.execute(checkquery)
        results = cursor.fetchall()
        # print(results)
        if len(results) !=0 :
            return
        insertnamesquery = f'''
            INSERT INTO UserGroupInfo (Name, GroupName, IsAdmin) VALUES (\'{name}\', \'{grpname}\', FALSE)
            '''
        cursor.execute(insertnamesquery)

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Preparing query to create a database
create_tables(cursor)
#creategrp()
# print('Welcome')
def userloop(cursor):
    while True:
        print('Enter OPTION \n 1. Existing User \n 2. New User \n 3. Exit')
        x=int(input(">>>"))
        if x==1:
          print("Enter Username")
          user_name = input(">>>")
          lst = check_user_name(user_name, cursor)
          if lst != False:
            print("Enter Password")
            password = input(">>>")
            while password != lst[1]:
                 print("Incorrect Password!! Enter Password Again")
                 password = input(">>>")
            join_group(user_name,cursor)
          else:
                 print("Not a Existing User")       
        elif(x==2):
            print("Type your username")
            user_name = input(">>>")
            lst = check_user_name(user_name, cursor)
            if lst != False:
              print("Already Existing Try Another")
              user_name = input(">>>")
            print("Enter Password")
            password = input(">>>")
            print("Enter Password Again")
            mypassword = input(">>>")
            while mypassword!= password:
                print("Don't Match Enter Again")
                print("Enter Password")
                password = input(">>>")
                print("Enter Password Again")
                mypassword = input(">>>") 
            insert = f'''
            INSERT INTO Users (Name, Password) VALUES ('{user_name}', '{password}');
            '''
            cursor.execute(insert)
            print("Successfully Registered")   
        else:
            break

#Closing the connection
#conn.close()
