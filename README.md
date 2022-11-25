# FastChat

This code is developed and maintained by Ayush Agarwal, Sankalan Baidya and Soham Joshi as a part of the CS251-course project as a part of the autumn semester of the academic year 2022-23. 

In this project, we have used the following softwares : 
         * Python 3.8
         * PostGreSQL

For running the code, the following modules have to be installed in python : 

          - rsa
          - random
          - psycopg2
          - io
          - tkinter
          - PIL
          - socket
          - threading
          - json
          - bcrypt
          - numpy

In addition, we have used the versions Python 3.8 and PostGreSQL 15.1

In order to run the code, the following steps have to be performed : 

         1. python3 server.py 1234
         2. python3 server.py 1235
         3. Run multiple servers in a similar fashion
         4. python3 client.py
         5. Run multiple clients in a similar fashion 

Now, once the tkinter window is opened, the following options are available : 

1. Sign Up : This is for users who are new to the platform and do not have an account yet 

2. Join : This is for users who have signed up previously 

3. Create/Amend Group : This is for users to create new groups or add/remove people in groups they are part of. 

4. Join Group : Allows users to switch between groups they are part of. 

5. Send Image : This allows the users to send images on the groups or in direct messages by selecting a file on their PC. 

6. Chatbox : Simply typing the messages in the chatbox and pressing enter sends the message in the chatroom :)

### How to use mulitple servers?
For multiserver setup, you have to run each *server.py* as 
```console
python server.py <port>
```
Ensure that the *<port>* matches with the list at the bottom of *client.py* names *ports*. If you use
*Load Balancing Based on CPU utilisation* given below, make sure to do the same in *load_balancer.py*

### How to use different load balancing methods?
The default load balancer is a client-side Round Robin, which is basically switching servers after each request. The other two methods of load balancing are :
1. Standard Round Robin
2. Load Balancing Based on CPU utilisation
3. Random Load Balancer

To use any of them, first go to the function *load_switcher(self)* and then comment out whatever is present there, and uncomment the load balancer you want to use.
There are some additional steps you need to follow to test out *Standard Round Robin* and *Load Balancing Based on CPU utilisation*
#### Standard Round Robin
Comment in *load_balancer_round_robin*  inside *load_balancer.py* and comment out the other. Comment in *from load_balancer import load_balancer_round_robin* inside *client.py*

#### Load Balancing Based on CPU utilisation
Comment in *cpuutil_load_balancer*  inside *load_balancer.py* and comment out the other. Comment in *from load_balancer import cpuutil_load_balancer* inside *client.py*. Comment in *from load_balancer import cpuutil_load_balancer* inside *server.py* and the entire block which begins with *log_cpu_util()* and ends with *perf_thread.start()*

### References:
The intial code to setup the simple server and client was heavily influenced by the tutorial series
**Sockets Tutorial with Python 3** by *Sentdex*

&copy; 23/11/2022 : This project is developed, maintained and the intellectual property of Ayush Agarwal, Sankalan Baidya and Soham Joshi, currently Undergraduate Sophomores in the CSE Department@IIT Bombay.
