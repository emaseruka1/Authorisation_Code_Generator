import sqlite3
from abc import ABC,abstractmethod    


class Sql_database(ABC):

    def connect_db(self):                          #this concrete method is abstracted away to hide sensitive database connection logic
        self.conn=sqlite3.connect('auth_code.db')
        self.cursor=self.conn.cursor()
        #print("Database Connected & Activated")
        return self
        


    @abstractmethod      
    def action_db(self):   #this abstract method is used to offer safe pathway to connect to database without showing database credentials
        pass



    def create_tables(self):                         #method creating relational database tables for first time if non-existent
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores_table (                 
        id INTEGER PRIMARY KEY,                
        store_code INTEGER,                  
        store_name TEXT,
        password TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_transfers_table (  
        id INTEGER PRIMARY KEY,                
        code TEXT,
        from_store TEXT,
        to_store TEXT,
        product TEXT, 
        date_issued DATE,
        FOREIGN KEY (from_store) REFERENCES stores_table(store_name)
        FOREIGN KEY (code) REFERENCES authcode_table(authcode)
        )                   
        """ )

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdts_table (
        id INTEGER PRIMARY KEY, 
        pdt_name TEXT, 
        pdt_code TEXT)
        """
        )

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS authcode_table (
        id INTEGER PRIMARY KEY,
        authcode TEXT, 
        used BOOLEAN)
        """
        )

        print("Tables created")

    def close_db(self):
        self.conn.close()
        print("Database closed")
    
    def action_db(self):
        self.connect_db()
        self.create_tables()




################################################## Unit Tests #########################################################################
if __name__=="__main__":

    sql_object=Sql_database()
    sql_object.action_db()    #create database tables for first time

    sql_object.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") #check tables in Database
    created_tables=sql_object.cursor.fetchall()
    
    for table in created_tables:
        print(table[0])

    #add Admin user for first time if non-existant
    sql_object.cursor.execute("SELECT COUNT(*) FROM stores_table WHERE store_code = ?", (0,))
    warehouse_exists = sql_object.cursor.fetchone()[0]
    if warehouse_exists == 0:
        sql_object.cursor.execute("""INSERT INTO stores_table (store_code, store_name, password) VALUES (?, ?, ?)
        """, (0, 'Administrator', 'warehouse1')) 
        sql_object.conn.commit()

    sql_object.cursor.execute("SELECT * FROM stores_table WHERE store_code=0")   #check if warehouse exists in stores table
    admin=sql_object.cursor.fetchall()
    print(f'Admin exists in stores_table as: {admin}')
 
with sqlite3.connect('auth_code.db') as conn:   #enable concurrent writes and reads
    conn.execute('PRAGMA journal_mode=WAL;')