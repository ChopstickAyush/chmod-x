User_auth= dict({})
print('Welcome')
print('Enter OPTION \n 1. Existing User \n 2. New User \n 3. Exit')
while True:
    x=int(input(">>>"))
    if x==1:
      print("Enter Username")
      user_name = input(">>>")
      if user_name in User_auth.keys():
        print("Enter Password")
        password = input(">>>")
        while password != User_auth[user_name]:
             print("Incorrect Password!! Enter Password Again")
             password = input(">>>")
        if password == User_auth[user_name]:
             print("WELCOME")
      else:
             print("Not a Existing User")       
    elif(x==2):
        print("Type your username")
        user_name = input(">>>")
        while user_name in User_auth.keys():
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
        User_auth[user_name]=password 
        print("Successfully Registered")   
    else:
        break