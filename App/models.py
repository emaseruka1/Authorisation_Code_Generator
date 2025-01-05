from db_connection import Sql_database
import csv
from io import StringIO
from datetime import datetime
import pandas as pd

class User(Sql_database):

    def __init__(self,store_code,password):

        self.store_code = store_code
        self.password = password

    def action_db(self):
        return self.connect_db()
    
    def get_store_name(self,store_code):
        self.sql_obj=self.action_db()
        self.sql_obj.cursor.execute('SELECT store_name FROM stores_table WHERE store_code =?',(store_code,))
        results = self.sql_obj.cursor.fetchall()
        #results=results[0]
        print(results)
        return results


class Admin(User):

    def __init__(self, store_code, password):
        super().__init__(store_code, password)
        self.sql_obj=self.action_db()

    def add_products(self,csv_file):   #accepts excel file
        csv_file =pd.read_csv(csv_file)
        
        csv_file.to_sql('pdts_table',  self.sql_obj.conn, if_exists='append', index=False)

    def view_products(self):
        self.sql_obj.cursor.execute('SELECT * FROM pdts_table')
        results = self.sql_obj.cursor.fetchall()
        print(results)
        return results

    def add_stores(self,new_store_code,new_store_name,new_store_password):
        self.sql_obj.cursor.execute('SELECT store_code FROM stores_table WHERE store_code = ?',(new_store_code,))
        result = self.sql_obj.cursor.fetchall()
        
        if result:
            print("Error: Store already exists")
            return "Error: Store already exists"

        self.sql_obj.cursor.execute('INSERT INTO stores_table (store_code,store_name,password) VALUES (?,?,?)',(new_store_code,new_store_name,new_store_password))
        self.sql_obj.conn.commit()

    def view_stores(self):
        self.sql_obj.cursor.execute('SELECT * FROM stores_table')
        results = self.sql_obj.cursor.fetchall()
        print(results)
        return results


    def change_store_password(self,store_code,new_store_password):
        self.sql_obj.cursor.execute('UPDATE stores_table SET password =? WHERE store_code=?',(new_store_password,store_code))
        self.sql_obj.conn.commit()

    def remove_store(self,store_code):
        self.sql_obj.cursor.execute('DELETE FROM stores_table WHERE store_code=?',(store_code,))
        self.sql_obj.conn.commit()

    def view_all_authcodes(self):
        self.sql_obj.cursor.execute('SELECT * FROM store_transfers_table')
        result = self.sql_obj.cursor.fetchall()
        print(result)
        return result
    
    def view_authcode_table(self):
        self.sql_obj.cursor.execute('SELECT * FROM authcode_table')
        result = self.sql_obj.cursor.fetchall()
        print(result)
        return result

    def search_auth_code(self,from_store=None,to_store=None,date_issued=None,auth_code=None):
        query = "SELECT * FROM store_transfers_table"
        conditions = []
        parameters = []

        # Dynamically add conditions based on user input
        if from_store is not None:
            conditions.append("from_store = ?")
            parameters.append(from_store)
        
        if to_store is not None:
            conditions.append("to_store = ?")
            parameters.append(to_store)
        
        if auth_code is not None:
            conditions.append("code = ?")
            parameters.append(auth_code)
        
        if date_issued is not None:
            conditions.append("date_issued BETWEEN '1948-01-01' AND ?")
            parameters.append(date_issued)

        # Combine the conditions with AND
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute the query
        print(query, parameters)
        self.sql_obj.cursor.execute(query, parameters)
        results = self.sql_obj.cursor.fetchall()
        print(results)
        return results      
      
    def generate_new_authcodes(self,code_letters,max_count):
        code_letters = code_letters.upper()
        
        self.sql_obj.cursor.execute('SELECT authcode FROM authcode_table WHERE authcode LIKE ?',(code_letters + '%',))
        results = self.sql_obj.cursor.fetchall()

        if results:
            print("error codes exist")
            error_message = (f"❌ERROR: Letters \"{code_letters}\" already exist. Choose another Letter Combination")
            return {"status": "success", "message": error_message}  # Error response

        auth_codes = []

        for i in range(0,max_count,1):
            code = f'{code_letters}{i:03}'
            auth_codes.append(code)

        for code in auth_codes:
            self.sql_obj.cursor.execute('INSERT INTO authcode_table (authcode,used) VALUES (?,?)',(code,0))
            self.sql_obj.conn.commit()

        print(auth_codes)

        success_message = (f"✅SUCCESS: Auth Codes from \"{code_letters}001\" to \"{code_letters}{max_count:03}\" have been created successfully!")

        return {"status": "success", "message": success_message}
    



class Store(User):

    def __init__(self, store_code, password):
        super().__init__(store_code, password)
        self.sql_obj=self.action_db()

    def view_my_codes(self):
        self.sql_obj.cursor.execute('''SELECT * FROM store_transfers_table WHERE from_store =?''',(self.store_code,))
        results = self.sql_obj.cursor.fetchall()
        print(results)
        return results 


    def item_to_transfer(self,pdt_code,size_fit,qty):
        item = pdt_code+' '+size_fit+' x'+str(qty)
        print(item)
        return item
    
    def search_pdt(self,pdt_code):
        self.sql_obj.cursor.execute("SELECT pdt_name FROM pdts_table where pdt_code = ?",(pdt_code,))
        result = self.sql_obj.cursor.fetchone()
        print(result)
        return result
    

    def get_auth_code(self,to_store,all_items):
        
        self.sql_obj.cursor.execute('SELECT authcode FROM authcode_table WHERE used = FALSE LIMIT 1')
        code = self.sql_obj.cursor.fetchone()
        
        

        if code is None:
            print("no new codes")
            return "Error: Codes can not be issued at the Moment"

        code=code[0]
        self.sql_obj.cursor.execute('''INSERT 
                                    INTO 
                                    store_transfers_table 
                                    (code,from_store,to_store,product,date_issued) 
                                    VALUES (?,?,?,?,?)''',(code,self.store_code,to_store,' '.join(all_items),datetime.today().strftime("%Y-%m-%d")))
        
        self.sql_obj.conn.commit()

        self.sql_obj.cursor.execute('UPDATE authcode_table SET used =? WHERE authcode=?',(1,code))
        self.sql_obj.conn.commit()

        self.sql_obj.cursor.execute('SELECT code FROM store_transfers_table ORDER BY code DESC LIMIT 1')
        result = self.sql_obj.cursor.fetchall()
        print(result)
        return result


def download_all_authcodes(authcodes_table_data):
    csv_output = StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(['','timestamp', 'user_id', 'command', 'gods_eye_description']) # Write the header
    csv_writer.writerows(authcodes_table_data) #write data
    csv_output.seek(0)
    return csv_output.getvalue()



################################################## Unit Tests #########################################################################
if __name__=="__main__":

    admin_user = Admin('warehouse','warehouse1')

    admin_user.add_stores(20141,'Skopes Ashford','ashford1')
    admin_user.add_stores(20020,'Skopes Bridgend','bridgend1')
    admin_user.add_stores(2000,'test store','test1')
    admin_user.view_stores()

    admin_user.change_store_password(20141,'ashford2')
    admin_user.view_stores()


    admin_user.remove_store(2000)
    admin_user.view_stores()

    admin_user.generate_new_authcodes('a',5)
    
    store_user = Store(20141,'ashford2')


    all_items_to_transfer = [store_user.item_to_transfer('MM71001','34R',2)]
    #print(all_items_to_transfer)
    
    store_user.get_auth_code('20020',all_items_to_transfer)
    store_user.view_my_codes()


    store_user2 = Store(20020,'bridgend1')
    all_items_to_transfer = [store_user2.item_to_transfer('TA0021','72R',650)]
    store_user2.get_auth_code('20141',all_items_to_transfer)
    store_user2.view_my_codes()

    

    admin_user.view_authcode_table()

    

