import os
import numpy as np
import pandas as pd
import mysql.connector
# import logging
# from multiprocessing.dummy import Pool


# logging.basicConfig(filename="serverQuery.log",format='%(asctime)s %(message)s',filemode = 'w')

# loggerQuery = logging.getLogger()
# loggerQuery.setLevel(logging.DEBUG)

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
                # print("is there a connection?")
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
    def changePrimary(self,serverID,shardID):
        self.nrq(f"UPDATE mapT SET PrimaryServer = CASE WHEN Server_id = '{serverID}' THEN 1 ELSE 0 END WHERE Shard_id = '{shardID}'; ")

    def getPrimary(self,shardID):
        print(shardID)
        row = self.query(f"SELECT Server_id from mapT WHERE Shard_id = '{shardID}' AND PrimaryServer = 1;")
        print(row)
        return row[0][0]
    
    def hasTable(self,tabname=None,columns=None,dtypes=None,primaryKeyFlag=True):
        res=self.query("SHOW TABLES")
        print(res)
        if primaryKeyFlag:
            if tabname not in [r[0] for r in res]:
                dmap={'Number':'INT','String':'VARCHAR(32)','Boolean':'BOOLEAN DEFAULT 0'}
                # print(dmap)
                col_config=''
                flag =True
                for c,d in zip(columns,dtypes):
                    # print(c,d)
                    if flag:
                        col_config+=f" {c} {dmap[d]} PRIMARY KEY NOT NULL"
                        flag = False
                    else: 
                        col_config+=f", {c} {dmap[d]}"
                print(f"CREATE TABLE {tabname} ({col_config} );")
                self.nrq(f"CREATE TABLE {tabname} ( {col_config} );")
        else:
            if tabname not in [r[0] for r in res]:
                dmap={'Number':'INT','String':'VARCHAR(32)','Boolean':'BOOLEAN DEFAULT 0'}
                col_config=''
                flag =True
                for c,d in zip(columns,dtypes):
                    if flag:
                        col_config+=f" {c} {dmap[d]}"
                        flag = False
                    else: 
                        col_config+=f", {c} {dmap[d]}"
                print(f"CREATE TABLE {tabname} ({col_config} );")
                self.nrq(f"CREATE TABLE {tabname} ( {col_config} );")
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
    
    def InsertLBshardT(self,row):
        error = ""
        c=0
        # for data in row:
        #     print(data)
        for data in row:
            try:
                self.nrq(f"INSERT INTO shardT (Shard_id, Stud_id_low, Shard_size, valid_idx) VALUES ('{str(data['Shard_id'])}',{int(data['Stud_id_low'])},{int(data['Shard_size'])},0)")
                # self.nrq(f"INSERT INTO shardT (Shard_id, Stud_id_low, Shard_size, Valid_idx) VALUES ('{str(data['Shard_id'])}',{int(data['Stud_id_low'])},{int(data['Shard_size'])},{})")
                c+=1
            except Exception as e:
                error+= str(e)
        if error != "" and c>0 :
            return error+"\n Other entries inserted"
        return error
    
    def InsertLBmapT(self,row):
        error = ""
        c=0
        keysList = list(row.keys())
        print(keysList)
        for server in keysList:
            for shard in row[server]:
                print(server,shard)
        # for data in row:
                try:
                    self.nrq(f"INSERT INTO mapT (Shard_id, Server_id) VALUES ('{str(shard)}','{str(server)}')")
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
        
    def whereIsShard(self, shardID):
        try:
            # print(shardID)
            # print(f"SELECT DISTINCT Server_id FROM mapT WHERE Shard_id = '{shardID}'")
            res = self.query(f"SELECT DISTINCT Server_id FROM mapT WHERE Shard_id = '{shardID}'")
            return [x[0] for x in res]
        except Exception as e:
            return str(e)
    
    def getShardsinServer(self,serverID):
        try:
            res = self.query(f"SELECT DISTINCT Shard_id FROM mapT WHERE Server_id = '{serverID}'")
            return [x[0] for x in res]
        except Exception as e:
            return str(e)
    def getServerList(self):
        try:
            res = self.query(f"SELECT DISTINCT Server_id FROM mapT")
            return [x[0] for x in res]
        except Exception as e:
            return str(e)
    def getShardList(self):
        try:
            res = self.query(f"SELECT DISTINCT Shard_id FROM mapT")
            return [x[0] for x in res]
        except Exception as e:
            return str(e)
    def getShardInfo(self):
        try:
            res = self.query(f"SELECT Stud_id_low, Shard_id, Shard_size FROM shardT")
            messgae =[]
            for row in res:
                messgae.append({"Stud_id_low":row[0],"Shard_id":row[1],"Shard_size":row[2],"primary_server":self.getPrimary(row[1])})
            # print(res)
            return messgae,1
        except Exception as e:
            return str(e),0
    def deleteServer(self,serverName):
        try:
            self.nrq(f"DELETE FROM mapT WHERE Server_id = '{serverName}'")
        except Exception as e:
            return str(e)
    def getServerInfo(self):
        try:
            # serverList = self.getServerList()
            
            res = self.query(f"SELECT Shard_id, Server_id FROM mapT")
            message ={}
            for row in res:
                if row[1] not in list(message.keys()):
                    message[row[1]] = []
                message[row[1]].append(row[0])
            # print(res)
            return message,1
        except Exception as e:
            return str(e),0
    def getStud_id_low(self,shardName):
        try:
            res = self.query(f"SELECT Stud_id_low FROM shardT where Shard_id = '{shardName}'")
            return res[0][0],1
        except Exception as e:
            return str(e),0
    def getStud_size(self,shardName):
        try:
            res = self.query(f"SELECT Shard_size FROM shardT where Shard_id = '{shardName}'")
            return res[0][0],1
        except Exception as e:
            return str(e),0
    def getCurrIdx(self,shardName):
        try:
            res = self.query(f"SELECT valid_idx FROM shardT where Shard_id = '{shardName}'")
            return res[0][0],1
        except Exception as e:
            return str(e),0
    def updateCurrIdx(self,noofEntry,shardName):
        try:
            self.nrq(f"UPDATE shardT SET valid_idx={noofEntry} WHERE Shard_id = '{shardName}'")
        except Exception as e:
            return str(e),0


        

    
# def env_config():
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