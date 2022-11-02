import pdb
import psycopg2


#establishing the connection
conn = psycopg2.connect(
   database="postgres", user='postgres', password='1234', host='127.0.0.1', port= '5432'
)
conn.autocommit = True

def create_tables(cursor) :

    create ='''
        DROP TABLE IF EXISTS Users; 
        CREATE TABLE IF NOT EXISTS Users (
        Name VARCHAR ( 20 ) PRIMARY KEY,
        Password VARCHAR ( 20 ) NOT NULL
        );

        DROP TABLE IF EXISTS UserGroupInfo;
        CREATE TABLE IF NOT EXISTS UserGroupInfo (
        Name VARCHAR ( 20 ),
        GroupName VARCHAR ( 20 ),
        Isadmin BOOLEAN, 
        Time INT 
        );

        DROP TABLE IF EXISTS Messages;
        CREATE TABLE IF NOT EXISTS Messages (
        GroupName VARCHAR( 20 ), 
        msg VARCHAR ( 100 ), 
        Name VARCHAR ( 20 ),
        Time INT
        );

        DROP TABLE IF EXISTS Groups;
        CREATE TABLE IF NOT EXISTS GROUPS (
        GroupName VARCHAR ( 20 ) PRIMARY KEY,
        public_key VARCHAR(1000),
        private_key VARCHAR(1000)
        );
    '''

    #Creating a database
    cursor.execute(create)
    print("Database created successfully........")

    return

def check_user_name(name, cursor) :
    check_user = f"Select * from Users where Name = '{name}'"
    cursor.execute(check_user)
    lst = cursor.fetchone()
    if (lst == None): return False
    else : return lst

def creategrp(grpname, names, cursor) :
    '''
    grpname : string
    names : list of strings
    output : True if created, False if already exists
    '''

    # Checking if the group name is new ! 
    
    grpquery = f'''
    Select count(*) from GROUPS where GroupName = \'{grpname}\'
    '''
    cursor.execute(grpquery)
    count = cursor.fetchone()[0]
    pdb.set_trace()
    if count != 0 : return False
    
    # Now, creating the group .

    public_key = "hi"
    private_key = "bye"
    creategrpquery = f'''
    INSERT INTO GROUPS (GroupName, public_key, private_key) VALUES (\'{grpname}\', \'{public_key}\', \'{private_key}\')
    '''
    cursor.execute(creategrpquery)

    for i in range(len(names)) : 
        
        if i == 0 : 
            insertnamesquery = f'''
            INSERT INTO UserGroupInfo (Name, GroupName, IsAdmin, Time) VALUES (\'{names[i]}\', \'{grpname}\', TRUE, 0)
            '''
            cursor.execute(insertnamesquery)
        else : 
            insertnamesquery = f'''
            INSERT INTO UserGroupInfo (Name, GroupName, IsAdmin, Time) VALUES (\'{names[i]}\', \'{grpname}\', FALSE, 0)
            '''
            cursor.execute(insertnamesquery)

    return 

def pendingmsg(grpname, username, cursor) :
    '''
    grpname : string
    username : string
    returns : list of strings
    '''

    gettimequery = f'''
    Select Time from UserGroupInfo where Name=\'{username}\' AND GroupName = \'{grpname}\''''
    cursor.execute(gettimequery)
    time = cursor.fetchone()[0]

    # using this time to get list of messages after this time. 

    getmessagequery = f'''
    Select Name, msg from Messages where Time > {time} AND GroupName = \'{grpname}\'
    '''
    cursor.execute(getmessagequery)
    rows = cursor.fetchall()

    # Update the last seen message 

    updatetimequery = f'''
    Update UserGroupInfo SET Time = (Select Max(Time) from Messages where GroupName = \'{grpname}\')
    '''
    cursor.execute(updatetimequery)

    return rows

name = []

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Preparing query to create a database
create_tables(cursor)


print('Welcome')
print('Enter OPTION \n 1. Existing User \n 2. New User \n 3. Exit')
while True:
    x=int(input(">>>"))
    if x==1:
      print("Enter Username")
      user_name = input(">>>")
      lst = check_user_name(user_name, cursor)
      #pdb.set_trace()
      if lst != False:
        print("Enter Password")
        password = input(">>>")
        while password != lst[1]:
             print("Incorrect Password!! Enter Password Again")
             password = input(">>>")
        print("WELCOME")

        y = int(input())
        if (y == 0) :
            break
        else : 
            continue

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
        #pdb.set_trace()
        insert = f'''
        INSERT INTO Users (Name, Password) VALUES ('{user_name}', '{password}');
        '''
        cursor.execute(insert)
        name.append(user_name)
        print("Successfully Registered")   
    else:
        break

grpname = "FASTCHAT1"

creategrp(grpname, name, cursor)
#Closing the connection
conn.close()
