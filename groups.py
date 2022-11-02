from codecs import latin_1_decode
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
        CREATE TABLE IF NOT EXISTS Users (
        Name VARCHAR ( 20 ) PRIMARY KEY,
        Password VARCHAR ( 20 ) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS UserGroupInfo (
        Name VARCHAR ( 20 ),
        GroupName VARCHAR ( 20 ),
        Isadmin BOOLEAN, 
        Time INT 
        );

        CREATE TABLE IF NOT EXISTS Messages (
        GroupName VARCHAR( 20 ), 
        msg VARCHAR ( 100 ), 
        Name VARCHAR ( 20 ),
        Time INT
        );

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

def generatekey(grpname):
    publicKey, privateKey = rsa.newkeys(random.randint(100,500))
    pass

def pending_message(user_name,cursor,grp_name):
    pass
# pending message of 

group_dict = dict({})
def enter(user_name,grp_name,cursor):
    pending_message(user_name,grp_name,cursor)
    print("start chat")
    pass
    
def create_grp(grp_name,L1,cursor):
    pass

def join_group(user_name,cursor):
    while True:
        print('Enter OPTION \n 1. Enter a group \n 2. Join a group  \n 3. Exit')
        x = int(input(">>>"))
        if x == 1:
            print("Enter Group Name")
            grp=input(">>>>")
            if  grp not in group_dict.keys():
                print("Not A Valid Group Name")
            elif user_name in group_dict[grp]:
                enter(grp,user_name,cursor)
            else: 
                print("Not A group Member")
                
        if x == 2 :
            grpname=input("Enter Group Name")
            L1=[user_name]
            print("Enter Members ")
            print("Enter 1. Member Name \n 2. 0 to create group ")
            x=input(">>>")
            while x!="0":
                L1.append(x)
                print("Enter 1.Member Name \n 2.0 to creste group")
                x=input(">>>")
                while check_user_name(x)==False:
                    print("NOT A member Enter again")
                    x=input(">>>")           
            a= create_grp(grp_name,L1,cursor)
            while a==False:
                print("Name Already In Use. Try another")
                print("Enter Groupname")
                grp_name=input(">>>")
                a= create_grp(grp_name,L1,cursor)
            if a==True:
                print("group created")
                generatekey(grpname)
            
        if x==3:
            break
            
            

def check_user_name(name, cursor) :
    check_user = f"Select * from Users where Name = '{name}'"
    cursor.execute(check_user)
    lst = cursor.fetchone()
    if (lst == None): return False
    else : return lst



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
conn.close()
