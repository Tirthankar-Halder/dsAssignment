import os
import numpy as np
import pandas as pd
import mysql.connector
# import logging
# from multiprocessing.dummy import Pool


# logging.basicConfig(filename="serverQuery.log",format='%(asctime)s %(message)s',filemode = 'w')

# loggerQuery = logging.getLogger()
# loggerQuery.setLevel(logging.DEBUG)


# class DataHandler:
#     def __init__(self,columns=None,dtypes=None,is_SQL=False,SQL_handle=None,table_name=None):
#         self.columns=columns
#         self.dtypes=dtypes
#         self.is_SQL=is_SQL
#         self.SQL_handle=SQL_handle
#         self._setup(table_name)

#     def _setup(self,table_name):
#         if not self.is_SQL:
#             self.table=pd.DataFrame(columns=self.columns)
#         else:
#             self.table_name=self.SQL_handle.jobrunner.apply(self.SQL_handle.hasTable,(table_name,self.columns,self.dtypes))
    
#     @property
#     def Count(self):
#         if not self.is_SQL:
#             return self.table.shape[0]
#         else:
#             return self.SQL_handle.jobrunner.apply(self.SQL_handle.Count,(self.table_name,))

#     def Insert(self,row):
#         if not self.is_SQL:
#             id=self.table.shape[0]
#             self.table.loc[self.table.shape[0]]=row
#         else:
#             id=self.SQL_handle.jobrunner.apply(self.SQL_handle.Insert,(self.table_name,row))
#         return id

#     def Update(self,idx,col,val):
#         if not self.is_SQL:
#             self.table.loc[idx,col]=val
#         else:
#             self.SQL_handle.jobrunner.apply(self.SQL_handle.setVal,(self.table_name,idx,col,val))

#     def GetAT(self,idx,col):
#         if not self.is_SQL:
#             return self.table.loc[idx,col]
#         else:
#             return self.SQL_handle.jobrunner.apply(self.SQL_handle.getVal,(self.table_name,idx,col))

#     def IncrementBy(self,idx,col,by):
#         if not self.is_SQL:
#             self.table.loc[idx,col]+=by
#         else:
#             self.SQL_handle.jobrunner.apply(self.SQL_handle.IncrementBy,(self.table_name,idx,col,by))


class SQLHandler:
    def __init__(self,host='localhost',user='root',password='password',db='shardDB'):
        self.host=host
        self.user=user
        self.password=password
        self.db=db

    def connect(self):
        connected=False
        while not connected:
            try:
                self.mydb = mysql.connector.connect(host=self.host,user=self.user,password=self.password)
                self.UseDB(self.db)
                connected=True
                print("Connection Established...")
            except Exception as e:
                print(e)
                pass

    def nrq(self,sql):
        try:
            cursor = self.mydb.cursor()
            cursor.execute(sql)
        except Exception :
            self.connect()
            cursor = self.mydb.cursor()
            cursor.execute(sql)
        cursor.close()
        self.mydb.commit()
        return 
    
    def query(self, sql):
        try:
            cursor = self.mydb.cursor()
            cursor.execute(sql)
        except Exception :
            self.connect()
            cursor = self.mydb.cursor()
            cursor.execute(sql)
        res=cursor.fetchall()
        print(res)
        cursor.close()
        self.mydb.commit()
        return res

    def UseDB(self,dbname=None):
        res=self.query("SHOW DATABASES")
        print(res)
        if dbname not in [r[0] for r in res]:
            self.nrq(f"CREATE DATABASE {dbname}")
        self.nrq(f"USE {dbname}")

    def DropDB(self,dbname=None):
        res=self.query("SHOW DATABASES")
        print(res)
        if dbname in [r[0] for r in res]:
            self.nrq(f"DROP DATABASE {dbname}")

    def hasTable(self,tabname=None,columns=None,dtypes=None):
        res=self.query("SHOW TABLES")
        print(res)
        if tabname not in [r[0] for r in res]:
            dmap={'Number':'INT','String':'VARCHAR(32)'}
            col_config=''
            flag =True
            for c,d in zip(columns,dtypes):
                if flag:
                    col_config+=f" {c} {dmap[d]} PRIMARY KEY NOT NULL"
                    flag = False
                else: 
                    col_config+=f", {c} {dmap[d]}"
            print(f"CREATE TABLE {tabname} ({col_config});")
            self.nrq(f"CREATE TABLE {tabname} ({col_config});")
        return tabname

    def fetchTable(self):
        res=self.query("SHOW TABLES")
        return res

    def getVal(self,table_name,idx,col):
        row=self.query(f"SELECT {col} FROM {table_name} where id={idx+1}")
        if len(row)==0:raise KeyError(f"Key:idx-{idx} is not found")
        else:return row[0][0]

    def Read(self,table_name,lowVal,highVal):
        try:
            res=self.query(f"SELECT * FROM {table_name} where Stud_id BETWEEN {lowVal} AND {highVal};")
            messgae =[]
            if len(res)==0 :raise KeyError(f"Key:idx-{lowVal} and {highVal} is not found")
            else:
                for row in res:
                    messgae.append({"Stud_id":row[0],"Stud_name":row[1],"Stud_marks":row[2]})
                return messgae,1
        except Exception as e:
            return str(e),0

    def setVal(self,table_name,idx,col,val):
        if type(val)==str:
            self.nrq(f"UPDATE {table_name} SET {col}='{val}' WHERE id={idx+1}")
        else:
            self.nrq(f"UPDATE {table_name} SET {col}={val} WHERE id={idx+1}")

    def IncrementBy(self,table_name,idx,col,by):
        self.nrq(f"UPDATE {table_name} SET {col}={col}+{by} WHERE id={idx+1}")

    def Insert(self,table_name,row):
        error = ""
        c=0
        for data in row:
            try:
                
                self.nrq(f"INSERT INTO {table_name} (Stud_id, Stud_name, Stud_marks) VALUES ({int(data['Stud_id'])},'{str(data['Stud_name'])}',{str(data['Stud_marks'])})")
                c+=1
            except Exception as e:
                error+= str(e)
        if error != "" and c>0 :
            return error+"\n Other entries inserted"
        return error
    
    def Update(self,shardN,updatedData,studID):
        try:
            self.nrq(f"UPDATE {shardN} SET Stud_id={int(updatedData['Stud_id'])}, Stud_name='{str(updatedData['Stud_name'])}', Stud_marks={str(updatedData['Stud_marks'])} WHERE Stud_id={studID}")
        except Exception as e:
            print(e)
            return e

    def getTopicTables(self):
        res=self.query("SHOW TABLES")
        return [r[0] for r in res if r[0] not in ['subl','publ']]
    
    def Count(self,table_name):
        res=self.query(f"SELECT count(id) FROM {table_name}")
        return res[0][0]
    
    def checkIfIdExists(self,tableName, StudID):
        try:
            res = self.query(f"SELECT COUNT(*) FROM {tableName} WHERE Stud_id = {StudID}")
            return res[0][0],1
        except Exception as e:
            return str(e),0

    def Copy(self, tableName):
        try:
            res = self.query(f"SELECT * FROM {tableName}")
            messgae =[]
            for row in res:
                messgae.append({"Stud_id":row[0],"Stud_name":row[1],"Stud_marks":row[2]})
            # print(res)
            return messgae,1
        except Exception as e:
            return str(e),0
        
    def Delete(self,tabname,studid):
        try:
            self.nrq(f"DELETE FROM {tabname} WHERE Stud_id={studid}")
        except Exception as e:
            return str(e)
# def env_config():
#     config={}
#     config['persist']=True if os.environ['PERSIST']=='yes' else False
#     config['broker_id']=os.environ['BID']
# #     return config
    

# handler = SQLHandler(db = "shardDB")
# handler.connect()

# print("Connection Established...")
# payload_json = {"schema": {"columns":["Stud_id","Stud_name","Stud_marks"],
#             "dtypes":["Number","String","String"]},
# "shards" : ["sh1","sh2"]}

# {"shards" : ["sh1","sh2"]}

# {"shard" : "sh2",
# "Stud_id":{"low":2235,"high":2555}}

# payload_json = {"shard" : "sh2",
# "curr_idx":507,
# "data":[{"Stud_id":2235,"Stud_name":"GHI","Stud_marks":27}]}
# columnsName = payload_json['schema']['columns']
# dtypes = payload_json['schema']['dtypes']
# shardsName = payload_json.get('shards', [])
# print(columnsName)
# print(dtypes)
# print(shardsName)
# shardsName = payload_json.get('shards', [])
# currentidx = payload_json.get('curr_idx',[])
# data = payload_json.get('data',[])
# print(handler.Insert(shardsName,data))
# table = handler.hasTable(tabname=shardsName,columns=columnsName,dtypes=dtypes)

# for shards in shardsName:
#     table = handler.hasTable(tabname=shards,columns=columnsName,dtypes=dtypes)

# print(handler.fetchTable())
# print(handler.fetchColumn('sh1'))