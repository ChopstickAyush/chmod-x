import psycopg2
import sys



class LoadBalancerRoundRobin:
    def __init__(self,n_ports,cursor):
        
        self.current_port_index = 0
        self.num_ports = n_ports
        self.cursor = cursor
        self.create_tables()

    def get_port_index(self):
        self.current_port_index = (self.get_port_index_from_table())%self.num_ports
        self.update_port_index()
        return self.current_port_index

    def update_port_index(self):
        update =f'''UPDATE RoundRobin SET index = index+1 WHERE id = (123)'''
        self.cursor.execute(update)

    def get_port_index_from_table(self):
        get =f'''SELECT  index from RoundRobin WHERE id =(123)'''
        self.cursor.execute(get)
        index = self.cursor.fetchone()[0]
        return index
        
    def create_tables(self) :
        
        create ='''
            DROP TABLE IF EXISTS RoundRobin;
            CREATE TABLE IF NOT EXISTS RoundRobin (
            id INT PRIMARY KEY,
            index INT DEFAULT 0
            );
        '''
        self.cursor.execute(create)
        #Creating a database
        check  = '''SELECT index from RoundRobin WHERE id = (123)'''
        self.cursor.execute(check)
        result = self.cursor.fetchone()
        print(result)
        if result is None:
            insert = '''INSERT INTO RoundRobin (id,index) VALUES(123,0)'''
            self.cursor.execute(insert)
            

        

        print("Database created successfully........")

        return

class LoadBalancerCPUUtil:
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
        update =f'''UPDATE CPUUtil SET util = ({cpu_util}) WHERE port = ({port})'''
        self.cursor.execute(update)

    def get_port_from_table(self):

        min_util_query = '''SELECT Min(util) from CPUUtil'''
        self.cursor.execute(min_util_query)
        min_util = self.cursor.fetchone()[0]
        get =f'''SELECT id from CPUUtil WHERE util =({min_util})'''
        self.cursor.execute(get)
        index = self.cursor.fetchone()[0]
        return index
        
    def create_tables(self) :
        
        create ='''
            CREATE TABLE IF NOT EXISTS CPUUtil (
            id SERIAL ,
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

        return

conn = psycopg2.connect(
database="postgres", user='postgres', password='1234', host='127.0.0.1', port= '5432')
conn.autocommit = True
n_ports =2 # NEED TO MANUALLY SET THIS
ports = [1234,1235]
# load_balancer_round_robin = LoadBalancerRoundRobin(n_ports, conn.cursor())
cpuutil_load_balancer = LoadBalancerCPUUtil(n_ports,ports,conn.cursor())