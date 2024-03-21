import sqlite3
import random
import string
import mysql.connector
from flask_sqlalchemy import SQLAlchemy

class StudentDatabase:
    def __init__(self, db_name='studTable.db'):
        self.db_name = db_name
        
    def create_connection(self):
        conn = sqlite3.connect(self.db_name)
        return conn
    
    def create_table(self, conn, payload):
        payload = payload
        schema = payload.get('schema')
        shards = payload.get('shards')
        try:
            cursor = conn.cursor()
            for sh in shards:
                cursor.execute(f'''CREATE TABLE IF NOT EXISTS {sh}(
		                        {schema["columns"][0]} INTEGER PRIMARY KEY NOT NULL,
		                        {schema["columns"][1]} TEXT NOT NULL,
		                        {schema["columns"][2]} TEXT NOT NULL,
		                        CONSTRAINT id_range CHECK ({schema["columns"][0]} BETWEEN 000000 AND 1000000)
		                    )''')
                conn.commit()
            cursor.close()
            result = shards
            return result
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return error_message, 500
    def check_table(self, conn, table_name):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        check = cursor.fetchone()[0]
        cursor.close()
        print(check)
        return check > 0
        
    def check_id(self, conn, table,s_id):
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE Stud_id=?", (s_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
        
    def create_meta_table(self, conn): #this is not needed 
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ShardT (
                Stud_id_low INTEGER PRIMARY KEY,
                Shard_id TEXT NOT NULL,
                Shard_size INTEGER NOT NULL,
                valid_idx INTEGER  ,
                CONSTRAINT  v_idx CHECK (valid_idx BETWEEN 000000 AND 1000000 )
            )''')
        conn.commit()
    
        cursor.execute('''CREATE TABLE IF NOT EXISTS MapT (
                Shard_id TEXT NOT NULL,
                Server_id TEXT NOT NULL,
                FOREIGN KEY (Shard_id) REFERENCES ShardT(Shard_id)       
            )''')
        conn.commit()
        cursor.close()

    def generate_random_name(self):
        return ''.join(random.choices(string.ascii_uppercase, k=5))

    def generate_random_marks(self):
        return random.randint(0, 100)

    def write(self, conn, payload):
        table = payload.get('shard')
        curr_idx = int(payload.get('curr_idx'))
        datas = payload.get('data')
        cursor = conn.cursor()
        try:
            if self.check_table(conn, table) :
                for data in datas:
                    cursor.execute("INSERT INTO {} (Stud_id, Stud_name, Stud_marks) VALUES (?,?,?)".format(table),(int(data['Stud_id']), data['Stud_name'], str(data['Stud_marks'])))
                    conn.commit()
                    curr_idx += 1
                cursor.close()
                message = 'Data entries added'
                current_idx = curr_idx
                return message, current_idx,200
            else :
                message= f"Error:   {table} does not exist in the database. write failed."
                current_idx=curr_idx
                return message,current_idx,500
    
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return error_message,curr_idx,500
		
    
    def insert_shards(self, conn, payload):   # this is not needed
        table = payload.get('shard')
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO ? (Stud_id_low, Shard_id, Shard_size) VALUES (?, ?, ?)", (table,0, "sh1", 50))
        conn.commit()
        cursor.close()

    def insert_shard_mapping(self, conn): #this is not needed
        cursor = conn.cursor()
        cursor.execute("INSERT INTO MapT (Shard_id, Server_id) VALUES (?, ?)", ("sh1", "Server0"))
        conn.commit()
        cursor.close()
    
    def select_all_rows(self, conn, shard):
        table = shard
        cursor = conn.cursor() 	
        cursor.execute(f"SELECT * FROM {table}")
        listofstu = cursor.fetchall()  # Fetch all rows
        message = []
        data = {}
        for i in listofstu:
            data['Stud_id'] = i[0]
            data['Stud_name'] = i[1]
            data['Stud_marks'] = i[2]
            message.append(str(data))
        cursor.close()
        return message
    
    def copy(self, conn, shards):
        #table = payload.get('shard')
        message = []
        try:
            for i in shards:
                message.append(self.select_all_rows(conn,i))
            return message,200
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return error_message, 500
    
    def read(self, conn, payload):
        table = payload.get('shard')
        low = payload['Stud_id']['low']
        high = payload['Stud_id']['high']
        try:
            if not self.check_table(conn,table):
                message = f"Error: Shard with ID {table} does not exist in the database. read failed."
                status_code = 500
                return message,status_code
            else :
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table} WHERE Stud_id BETWEEN {low} AND {high}")
                listofstu = cursor.fetchall()  # Fetch all rows
                message = []
                data = {}
                for i in listofstu:
                    data['Stud_id'] = i[0]
                    data['Stud_name'] = i[1]
                    data['Stud_marks'] = i[2]
                    message.append(str(data))
                cursor.close()
                return message,200
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return error_message, 500
    
    def update(self, conn, payload):
        table = payload.get('shard')
        data = payload.get('data')
        s_id = payload.get('Stud_id')
        stud_id = int(data['Stud_id'])
        stud_marks = data['Stud_marks']
        stud_name = data['Stud_name']
        try:
            if not self.check_id(conn, table, s_id):
                message= f"Error: Student with ID {s_id} does not exist in the table {table}. Update failed."
                status_code=500
                return message,status_code
            else:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE {table} SET Stud_id=?, Stud_name=?, Stud_marks=? WHERE Stud_id=?", (stud_id, stud_name, stud_marks, s_id))
                conn.commit()
                message = f'data entry for stud_id {s_id} updated'
                return message,200
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return error_message, 500
           
    def delete(self, conn, payload):
        table = payload.get('shard')
        stud_id = payload.get('Stud_id')
        try :
            if not self.check_id(conn, table, stud_id):
                message= f"Error: Student with ID {stud_id} does not exist in the table {table}. delete failed."
                status_code=500
                return message,status_code
            else:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {table} WHERE Stud_id=?", (stud_id,))
                conn.commit()
                cursor.close()
                message = f'data entry for stud_id {stud_id} deleted '
                return message,200
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return error_message, 500
        

def main():
    student_db = StudentDatabase()
    conn = student_db.create_connection()
    conn.close()

if __name__ == "__main__":
    main()
