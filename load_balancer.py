import psycopg2
import sys



class LoadBalancerRoundRobin:
    """
    This class is designed for load balancing strategy as a round robin at server.
    basically, the next message is allocated to the next server.
    The record is maintained in a database.
    :param 
    """
    def __init__(self,n_ports,cursor):
        """Constructor for LoadBalancerRoundRobin Class. Intializing the number of 
        ports and cursor

        :param nports: Number of ports
        :type ports: int
        :param cursor: cursor to execute query
        :type cursor: cursor.cursor
        """
        
        self.current_port_index = 0
        self.num_ports = n_ports
        self.cursor = cursor
        self.create_tables()

    def get_port_index(self):
        """Getting the next port index according to round robin by taking modulus
        using the get_port_index_from_table(self) index.
        
        :param self.current_port_index: port number
        :type self.current_port_index: int
        """
        self.current_port_index = (self.get_port_index_from_table())%self.num_ports
        self.update_port_index()
        return self.current_port_index

    def update_port_index(self):
        """
        Updating the database for the port number used by update query.
        """
        update =f'''UPDATE RoundRobin SET index = index+1 WHERE id = (1234)'''
        self.cursor.execute(update)

    def get_port_index_from_table(self):
        """
        Gets the next port number by database through Select query.
        
        :param index: index
        :rtype index: int
        """
        get =f'''SELECT  index from RoundRobin WHERE id =(1234)'''
        self.cursor.execute(get)
        index = self.cursor.fetchone()[0]
        return index
        
    def create_tables(self) :
        """
        Create Table for holding the turns of roundrobin.
        """
        create ='''
            DROP TABLE IF EXISTS RoundRobin;
            CREATE TABLE IF NOT EXISTS RoundRobin (
            id INT PRIMARY KEY,
            index INT DEFAULT 0
            );
        '''
        self.cursor.execute(create)
        #Creating a database
        check  = '''SELECT index from RoundRobin WHERE id = (1234)'''
        self.cursor.execute(check)
        result = self.cursor.fetchone()
        if result is None:
            insert = '''INSERT INTO RoundRobin (id,index) VALUES(1234,0)'''
            self.cursor.execute(insert)
            

        

       # print("Database created successfully........")

        return

class LoadBalancerCPUUtil:
    """
    This class is designed for load balancing strategy according to the load at 
    cpu which is monitored according to the memory allocated.
    The least occupied server is given the duty of message.
    The record is maintained in a database.
    """
    def __init__(self,n_ports,ports,cursor):
        
        self.ports = ports
        # self.current_port_index = 0
        self.num_ports = n_ports
        self.cursor = cursor
        self.create_tables()

    # def get_port_index(self):
    #     self.current_port_index = (self.get_port_index_from_table())%self.num_ports
    #     self.update_port_index()
    #     return self.current_port_index

    def update_port_index(self,cpu_util,port):
        """Update the port's memory usage at database 

        :param cpu_util: CPU's memory
        :type cpu_util: int 
        :param port: Update the port's memory at cpu
        :type port: int    
        """
        update =f'''UPDATE CPUUtil SET util = ({cpu_util}) WHERE port = ({port})'''
        self.cursor.execute(update)

    def get_port_from_table(self):
        """
        Gets the next port number by database through Select query selecting minima
        of all.
        :param index: index
        :rtype index: int
        """
        min_util_query = '''SELECT Min(util) from CPUUtil'''
        self.cursor.execute(min_util_query)
        min_util = self.cursor.fetchone()[0]
        get =f'''SELECT id from CPUUtil WHERE util =({min_util})'''
        self.cursor.execute(get)
        index = self.cursor.fetchone()[0]
        return index ### NOTE: YOU MIGHT HAVE TO do index-1 
        
    def create_tables(self) :
        """
        Create Table for holding the cpu's memory usage.
        """
        create ='''
            CREATE TABLE IF NOT EXISTS CPUUtil (
            id SERIAL,
            Port INT PRIMARY KEY,
            util FLOAT
            );
        '''
        self.cursor.execute(create)
        #Creating a database
        for i in self.ports:
            check  = f'''SELECT util from CPUUtil WHERE Port = ({i})'''
            self.cursor.execute(check)
            result = self.cursor.fetchone()

            if result is None :
                insert = f'''INSERT INTO CPUUtil (Port,util) VALUES({i},0.0)'''
                self.cursor.execute(insert)


        

        print("Database created successfully........")

        return

conn = psycopg2.connect(
database="postgres", user='postgres', password='1234', host='127.0.0.1', port= '5432')
conn.autocommit = True
n_ports =1 # NEED TO MANUALLY SET THIS
ports = [1234,1235] # NEED TO MANUALLY ADD PORTS
# load_balancer_round_robin = LoadBalancerRoundRobin(n_ports, conn.cursor())
cpuutil_load_balancer = LoadBalancerCPUUtil(n_ports,ports,conn.cursor())