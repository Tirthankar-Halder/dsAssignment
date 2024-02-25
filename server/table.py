from flask import Flask, request, jsonify
import sqlite3
import random
import string

# Function to generate random student name
def generate_random_name():
    return ''.join(random.choices(string.ascii_uppercase, k=5))

# Function to generate random student marks
def generate_random_marks():
    return random.randint(0, 100)

def create_connection():
    conn = sqlite3.connect('studTable.db')
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS StudT (
                        Stud_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Stud_name TEXT NOT NULL,
                        Stud_marks FLOAT NOT NULL,
                        CONSTRAINT id_range CHECK (Stud_id BETWEEN 000000 AND 1000000),
                        CONSTRAINT stu_m CHECK (Stud_marks BETWEEN 0 AND 100)
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ShardT (
            Stud_id_low INTEGER PRIMARY KEY,
            Shard_id TEXT NOT NULL,
            Shard_size INTEGER NOT NULL,
            valid_idx INTEGER NOT NULL DEFAULT=Stud_id_low+Sharf_size,
            CONSTRAINT  v_idx CHECK (valid_idx BETWEEN 000000 AND 1000000 ),
            FOREIGN KEY (Stud_id_low) REFERENCES StudT(Stud_id)
        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS MapT (
            Shard_id TEXT NOT NULL,
            Server_id TEXT NOT NULL,
            FOREIGN KEY (Shard_id) REFERENCES ShardT(Shard_id)       
        )''')
    conn.commit()
    cursor.close()

def insert_table_stu(conn,name="NULL",marks="NULL"):
    if(name=="NULL"):
        name=generate_random_name()
    if(marks=="NULL"):
        marks=generate_random_marks()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO StudT (Stud_name,Stud_marks) values (?,?)",(name,marks))
    conn.commit()
    cursor.close()

def show_data(conn):
    cursor=conn.cursor()
    cursor.execute("SELECT * from STudT")
    listofstu = cursor.fetchall()  # Fetch all rows
    print(listofstu)
    cursor.close()

# Initialize the database when the application starts
conn = create_connection()

create_table(conn)
insert_table_stu(conn)
show_data(conn)

conn.close()
