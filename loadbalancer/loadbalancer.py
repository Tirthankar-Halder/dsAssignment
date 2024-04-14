import json
from flask import Flask,request,jsonify,url_for,redirect
import random
import requests
import os
#Differnt type Consistant Hashmapiing
from consistant_HASHMAP import ConsistentHashMap  
# from consistant_HASHMAP_1 import ConsistentHashMap  
# from consistant_HASHMAP_2 import ConsistentHashMap  
# from consistant_HASHMAP_3 import ConsistentHashMap  
# import subprocess

import threading
import time
from assist import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LoadBalancer:')
    

time.sleep(7)
app = Flask(__name__)

#GLOBAl VARIABLES
NUM_CONTAINERS = 3
TOTAL_SLOTS = 512
NUM_VIRTUAL_SERVERS = 9
MAX_RETRIES = 5
shardServerMap = {}
consistent_hash_map = ConsistentHashMap(NUM_CONTAINERS, TOTAL_SLOTS, NUM_VIRTUAL_SERVERS)
# replicas = [f"Server_{random.randint(100000,999999)}" for _ in range(1, NUM_CONTAINERS + 1)]
replicas = []
SHARD_REPLICAS = 2
################Initialize the Datbase for Loadbalance#############
schema = {}
mapT_json = {
    "schema" : {"columns":["Shard_id","Server_id","PrimaryServer"],
                "dtypes":["String","String","Boolean"]},
}
shardT_json = {
    "schema" : {"columns":["Shard_id","Stud_id_low","Shard_size","valid_idx"],
                "dtypes":["String","Number","Number","Number"]},
}

queryHandler = SQLHandler(db="loadbalancerDB")

### mapT######
columnsName = mapT_json['schema']['columns']
dtypes = mapT_json['schema']['dtypes']
queryHandler.hasTable(tabname="mapT",columns=columnsName,dtypes=dtypes,primaryKeyFlag=False)

### shardT######
columnsName = shardT_json['schema']['columns']
dtypes = shardT_json['schema']['dtypes']
queryHandler.hasTable(tabname="shardT",columns=columnsName,dtypes=dtypes,primaryKeyFlag=False)

# # Server Replica Initialization## 
# for replica in replicas:
#     # consistent_hash_map.add_server_container(int(replica[7]))
#     consistent_hash_map.add_server_container(replica)

# for replica in replicas:
#         print(replica)
#         os.system(f'sudo docker run --name {replica} --network net1 --network-alias {replica} -e "SERVER_ID={replica}" -d server:latest')
#         # out = os.system(f'sudo docker run --name {replica} --network net1 -e "SERVER_ID={replica}" -d server:latest')

# serverInitializaton = False
######################### Difining the another thread to check server status #######################
# def replica_status(replicas):
# def replica_status():
#     # global serverInitializaton
    
#     while True:
#         ####################Respwn Method 1###############################
#         global schema,replicas
#         for replica in replicas:

#             # alive = None
#             alive = os.system(f"ping -c 1 {replica}")
#             logger.info(f"Livenness of {replica} is {alive}, Available replica {replicas}")
#             if alive :
#                 logger.info(f"{replica} is down... Trying to Re-initialize ...")
#                 res = os.popen(f"sudo docker rm {replica}")
#                 shradinReplica = queryHandler.getShardsinServer(replica)
#                 res=os.popen(f"sudo docker run --name {replica} --network net1 --network-alias {replica} -e 'SERVER_ID={replica}' -d server:latest").read()
#                 # res=os.popen(f"sudo docker restart {replica}").read()
#                 time.sleep(20)

#                 logger.info("I am waiting for server to Re-initilize....... ")
#                 logger.info(f"Intialized server:{replica}")
#                 # shardsinserver = queryHandler.getShardsinServer(server)
#                 logger.info(f"shards list inside server : {shradinReplica}")
#                 serverPayload_json = {
#                     "schema": schema,
#                     "shards": shradinReplica
#                 }
#                 logger.info(f"Server paylod at config: {serverPayload_json}")
#                 print(serverPayload_json)
#                 tries = 0
#                 print("Calling config for ",replica)
#                 logger.info(f"Calling config for {replica}")
            
#                 try:
#                     url = f"http://{replica}:5000/config"
#                     res=requests.post(url,json=serverPayload_json).json()
#                     logger.info(f"Response from {replica} is :{res}")
#                 except Exception as e:
#                     logger.info(f"The routed {replica} is not yet Initialized, Retrying ....{tries}")

#                 shardsToCopy = queryHandler.getShardsinServer(replica)
#                 for shard in shardsToCopy:
#                     serverToCopyFrom = select_random_elements(queryHandler.whereIsShard(shard),[replica],len(queryHandler.whereIsShard(shard))-1)
#                     copyRES = {}
#                     for oldserver in serverToCopyFrom:
#                         logger.info(f"Starting data migration from {oldserver} to new server {replica}")
#                         copyJSON = {
#                             "shards" : [shard]
#                         }
#                         url = f"http://{oldserver}:5000/copy"
#                         copyRES = requests.get(url,json=copyJSON).json()
#                         # logger.info(f"Copy endpoint of {oldserver} gave response {copyRES}")
#                         logger.info(f"Fetched data from {oldserver}: {copyRES}")
#                         if copyRES["status"] == "success":
#                             break
#                     logger.info(f"Starting Data migration from {oldserver} of {shard} for {replica}")
#                     data = copyRES[shard]
#                     writeJSON ={
#                         "shard": shard,
#                         "curr_idx" : 0,
#                         "data": data
#                     }
#                     logger.info(f"Json for wrtting the data to newly added {replica}:{writeJSON}")

#                     url = f"http://{replica}:5000/write"
#                     writeRES = requests.post(url, json=writeJSON).json()

#                     logger.info(f"Response from {replica} is : {writeRES}")
#                     logger.info(f"Copied data of {shard} from {oldserver} to {replica}")
#                 # if replica not in queryHandler.getServerList():
#                 #     #handled: skipped if server is already present(valid for second time init call)
#                 #     if replica.find("[") != -1:
#                 #         #Handled Server[5] Case
#                 #         while True:
#                 #             #if randomly choosed server is present in keyist
#                 #             serverName = f"Server{random.randint(0,999999999)}" 
#                 #             os.system(f'sudo docker run --name {serverName} --network net1 --network-alias {serverName} -e "SERVER_ID={serverName}" -d server:latest')
#                 #             replicas.append(serverName)
#                 #             if serverName != replica :
#                 #                 #replaced the server key information with randomly choosed name
#                 #                 replicas[serverName] = replicas[replica]
#                 #                 del replicas[replica]
#                 #             break
#                 #     else:
#                 #         os.system(f'sudo docker run --name {replica} --network net1 --network-alias {replica} -e "SERVER_ID={replica}" -d server:latest')
#                 #         replicas.append(replica)
#                 #     logger.info(f"Container {replica} is added. New available server : {replicas}")

#                 if len(res)==0:
#                     print(f"Unable to start {replica}")
#                 else:
#                     print(f"successfully started {replica}")
                    

#         ####################Respwn Method 2###############################

#         # missingContainerOut = os.popen("sudo docker ps --format '[[ .Names ]]'").read().split("\n")
#         # missingContainerOut = missingContainerOut[:len(missingContainerOut)-1] 
#         # for replica in replicas:
#         #     if replica not in missingContainerOut:
#         #         print(f"{replica} is failed initiate, Trying to respwn")
#         #         res=os.popen(f"sudo docker run --name {replica} --network net1 --network-alias {replica} -e 'SERVER_ID={replica}' -d server:latest").read()

#         #         if len(res)==0:
#         #             print(f"Unable to start {replica}")
#         #         else:
#         #             print(f"successfully started {replica}")

#         ################Remove Unwanted container or respwn previous container automatically #############################
#         extraContainerOut = os.popen("sudo docker ps --format '[[ .Names ]]'").read().split("\n")
#         extraContainerOut = extraContainerOut[:len(extraContainerOut)-1]
#         for container in extraContainerOut:
#             if container not in replicas and container=="loadbalancer":
#                 os.system(f"sudo docker stop {container} && sudo docker rm {container}")
#         time.sleep(5)
    

# ############### Calling Server thread ###############
# server_thread = threading.Thread(target=replica_status)
# server_thread.start()
# # server_thread = threading.Thread(target=replica_status,args=(replicas,))
# # server_thread.start()





@app.route('/')
def index():
    logger.info("Welcome to HELLO WORLD")
    return "Welcome to HELLO WORLD"

@app.route('/rep', methods=['GET'])
def rep():
    # for replica in replicas:
    #     out = os.popen(f'sudo docker run --name {replica} --network net1 -e "SERVER_ID={replica}" -d server').read()
        # subprocess.run(f"sudo docker run --name {replica} --network net1 -e 'SERVER_ID={replica}' -d server",shell=True)
    global replicas
    response_json = {

        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status" : "successful"
    }
    return jsonify(response_json), 200


# @app.route('/add',methods = ['POST'])
# def add_replicas():
#     payload_json = request.get_json()
#     noOfServer = payload_json.get('n')
#     nameOfHostnames = payload_json.get('hostnames', [])
#     if len(nameOfHostnames) > noOfServer:
#         response_json = {
#             "message":"<Error> Length of hostname list is more than newly added instances",
#             "status" : "Failure"
#         }
#         return jsonify(response_json), 400
        
#     for i in range(noOfServer):
#         if i < len(nameOfHostnames):
#             replica = nameOfHostnames[i]
#         else:
#             replica = f"RandomServer{random.randint(100000, 999999)}"
#         replicas.append(replica)
#         # consistent_hash_map.add_server_container(int(replica[1:]))
#         consistent_hash_map.add_server_container(replica)
#         os.system(f"sudo docker run --name {replica} --network net1 --network-alias {replica} -e 'SERVER_ID={replica}' -d server:latest")
#     response_json = {
#         "message": {
#             "N": len(replicas),
#             "replicas": replicas
#         },
#         "status" : "successful"
#     }

#     return jsonify(response_json), 200

# @app.route('/rm', methods=['DELETE'])
# def remove_replicas():
#     payload_json = request.get_json()
#     noOfServer = payload_json.get('n')
#     nameOfHostnames = payload_json.get('hostnames', [])

#     if len(nameOfHostnames) > noOfServer:
#         response_json = {
#             "message":"<Error> Length of hostname list is more than newly removable instances",
#             "status" : "Failure"
#         }
#         return jsonify(response_json), 400
    
#     removed_replicas = []

#     for i in range(noOfServer):
#         if i < len(nameOfHostnames):
#             replica = nameOfHostnames[i]
#         else:
#             replica = random.choice(replicas)
#         removed_replicas.append(replica)
#         os.system(f"sudo docker stop {replica} && sudo docker rm {replica}")
#         # os.system(f"sudo docker stop {replica}")
#         replicas.remove(replica)
#         # consistent_hash_map.remove_server_container(int(replica[1:]))
#         consistent_hash_map.remove_server_container(replica)

#     response_json = {
#         "message": {
#             "N": len(replicas),
#             "replicas": replicas
#         },
#         "status" : "successful"
#     }

#     return jsonify(response_json), 200

@app.route('/<req_path>', methods=['GET'])
def route_request(req_path):
    req_id=random.randint(100000,999999)
    # replica = consistent_hash_map.get_server_container(req_id)
    replica = replicas[random.randint(0,len(replicas)-1)]
    app.logger.warn("Assigned {}".format(replica))
    if replica in replicas:
        try:
            url = f"http://{replica}:5000/home"
            res=requests.get(url).json()
            app.logger.warn(res)
            return res,200
        except Exception as e:
            print("The routed server is down && trying to ")

    else:
        response_json = {
            "message": f"<Error> '{req_path}' endpoint does not exist in server replicas",
            "status" : "Failure"
        }
        return jsonify(response_json), 400



 ############################################### PART 2 ##########################
      
database_configuration = None
mutex_locks = {}

@app.route('/init', methods=['POST'])
def initialize_database():
    print("inside api")

    try:
        global mutex_locks,replicas,shardServerMap, MAX_RETRIES,schema
        # Extract data from the request
        print("got payload")
        
        payload_json = request.get_json()
        n = payload_json["N"]
        schema = payload_json["schema"]
        shards = payload_json["shards"]
        servers = payload_json["servers"]

        

        #Server Container Inintialization
        keysList = list(servers.keys())
        if n== len(keysList):
            for server in keysList:
                if server not in queryHandler.getServerList():
                    #handled: skipped if server is already present(valid for second time init call)
                    if server.find("[") != -1:
                        #Handled Server[5] Case
                        while True:
                            #if randomly choosed server is present in keyist
                            serverName = f"Server{random.randint(0,999999999)}" 
                            if serverName not in keysList:
                                os.system(f'sudo docker run --name {serverName} --network net1 --network-alias {serverName} -e "SERVER_ID={serverName}" -d server:latest')
                                replicas.append(serverName)
                                if serverName != server :
                                    #replaced the server key information with randomly choosed name
                                    servers[serverName] = servers[server]
                                    del servers[server]
                                break
                    else:
                        os.system(f'sudo docker run --name {server} --network net1 --network-alias {server} -e "SERVER_ID={server}" -d server:latest')
                        replicas.append(server)
                    logger.info(f"Container {server} is added. New available server : {replicas}")
        else:
            #Edge case n mismiatch with server list handled
            if n>len(keysList): 
                response_json = {
                "error": "Number of Server is greater than server id",
                "status": "Failure"}
            elif n<len(keysList): 
                response_json = {
                "error": "Number of Server is less than server id",
                "status": "Failure"
                }
            return jsonify(response_json), 500

        print("added server to list")
    
        #Insert the init config data in datatables
        queryHandler.InsertLBshardT(row=shards)
        print("updated shardT")
        queryHandler.InsertLBmapT(row=servers)
        print("inserted values to tables")

        #Select Primary Server through Random func
        for shard in shards:
            id = shard['Shard_id']
            serverContainer = queryHandler.whereIsShard(id)
            pServer = random.choice(serverContainer)
            queryHandler.changePrimary(pServer,id)

        # Initialize mutex locks for each shard
        for shard in shards:
            id = shard['Shard_id']
            shardServerMap[id] = ConsistentHashMap(num_containers=0, total_slots= TOTAL_SLOTS, num_virtual_servers=NUM_VIRTUAL_SERVERS)
            serverContainer = queryHandler.whereIsShard(id)
            # print(f"servers for a shard {shard}: {serverContainer}")
            logger.info(f"servers for a shard {shard}:{serverContainer}")
            for server in serverContainer:
                shardServerMap[id].add_server_container(server)
        print(shardServerMap)
        mutex_locks = {shard["Shard_id"]: threading.Lock() for shard in shards}
        print(mutex_locks)
        print("ConsistantHashMap Shard Initialized")
        logger.info("ConsistantHashMap Shard Initialized ")
        logger.info("Mutex Lock init")
        
        # /config call of individual servers.
        print(servers)
        logger.info(f"Server {servers}")
        time.sleep(20)


        # ################ Calling Server thread ###############
        # server_thread = threading.Thread(target=replica_status,args=(replicas,))
        # server_thread.start()


        logger.info("Bro I am waiting for server to initilize....... ")
        for server in servers:
            print("call for individual server:" ,server)
            logger.info(f"call for individual server:{server}")
            # shardsinserver = queryHandler.getShardsinServer(server)
            shardsinserver = servers[server]
            logger.info(f"shards list inside server : {shardsinserver}")
            serverPayload_json = {
                "schema": schema,
                "shards": shardsinserver
            }
            logger.info(f"Server paylod at config: {serverPayload_json}")
            print(serverPayload_json)
            tries = 0
            print("Calling config for ",server)
            logger.info(f"Calling config for {server}")
            
            try:
                url = f"http://{server}:5000/config"
                res=requests.post(url,json=serverPayload_json).json()
                logger.info(f"Response from {server} is :{res}")
            except Exception as e:
                logger.info(f"The routed {server} is not yet Initialized, Retrying ....{tries}")

        response_json = {
            "message": "Configured Database",
            "status": "success"
        }

        # serverInitializaton = True

        return jsonify(response_json), 200

    except Exception as e:
        error_response = {
            "message": f"Error during initialization: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500
    
@app.route('/status', methods=['GET'])
def get_database_status():
    global schema
    res = queryHandler.getServerList()
    shard,_ = queryHandler.getShardInfo()
    server,__ = queryHandler.getServerInfo()

    if schema:

        response_json = {
            "N": len(res),
            "schema": schema,
            "shards": shard,
            "servers": server
        }
        if len(res):
            return jsonify(response_json), 200
        else:
            response_data = {
                "message": "Database not configured yet",
                "status": "error"
            }
            return jsonify(response_data), 404
    else:
        return jsonify("Schema is not defined yet."),404

@app.route('/add', methods=['POST'])
def add_servers():
    global mutex_locks,replicas,shardServerMap, MAX_RETRIES,schema
    try:
        # Extract data from the request
        # global database_configuration
        payload_json = request.get_json()
        n = payload_json["n"]
        new_shards = payload_json["new_shards"]
        servers = payload_json["servers"]

        

        # Simple sanity checks on the request payload
        if n > len(servers):
            error_response = {
                "message": "Number of new servers (n) is greater than newly added instances",
                "status": "failure"
            }
            return jsonify(error_response), 400

        # Up new servers
        for server in list(servers.keys()):
            if server not in queryHandler.getServerList():
                if server.find("[") != -1:
                        #Handled Server[5] Case
                        while True:
                            #if randomly choosed server is present in keyist
                            serverName = f"Server{random.randint(0,999999999)}" 
                            if serverName not in list(servers.keys()):
                                os.system(f'sudo docker run --name {serverName} --network net1 --network-alias {serverName} -e "SERVER_ID={serverName}" -d server:latest')
                                replicas.append(serverName)
                                if serverName != server :
                                    #replaced the server key information with randomly choosed name
                                    servers[serverName] = servers[server]
                                    del servers[server]
                                break
                else:
                    os.system(f'sudo docker run --name {server} --network net1 --network-alias {server} -e "SERVER_ID={server}" -d server:latest')
                    replicas.append(server)
                logger.info(f"Container {server} is added. New available server : {replicas}")
            else:
                logger.info(f"Server {server} is already exists,Choose different name else will be skipped")
        
        

        # Update shard information
        # database_configuration["N"] += n
        # database_configuration["shards"].extend(new_shards)
        
        serverForShard = {}
        oldshards = queryHandler.getShardList()
        for shard in oldshards:
            serverForShard[shard] = queryHandler.whereIsShard(shard)
        logger.info(f"Server for Shard: {serverForShard}")
        #add new shard information
        ##Have to handle edge case wheather shard is alredy present or not
        queryHandler.InsertLBshardT(row=new_shards)
        logger.info("Inserted new_Shard to shardT ")
        queryHandler.InsertLBmapT(row=servers)
        logger.info("Inserted Server to mapT tables for newly added servers")
        #add new server details

        #Select Primary Server through Random func
        for shard in new_shards:
            id = shard['Shard_id']
            serverContainer = queryHandler.whereIsShard(id)
            pServer = random.choice(serverContainer)
            queryHandler.changePrimary(pServer,id)
            logger.info(f"Primary server {pServer} for shard {id}")

        for shard in new_shards:
            shard_id = shard['Shard_id']
            shardServerMap[shard_id] = ConsistentHashMap(num_containers=0, total_slots= TOTAL_SLOTS, num_virtual_servers=NUM_VIRTUAL_SERVERS)
            serverContainer = queryHandler.whereIsShard(shard_id)
            print("servers for a shard:",serverContainer)
            logger.info(f"Servers for a shard:{serverContainer}")
            for server in serverContainer:
                shardServerMap[shard_id].add_server_container(server)
        logger.info("Consistent Hashmap configaured for Newly added servers")
        print(shardServerMap)

        mutex_locks = {shard["Shard_id"]: threading.Lock() for shard in new_shards}
        print(mutex_locks)

        time.sleep(20)

        for server in servers:
            print("Call for individual server:" ,server)
            logger.info(f"Call for individual server:{server} for Shard Insertion")
            # shardsinserver = queryHandler.getShardsinServer(server)
            shardsinserver = servers[server]
            logger.info(f"Shards list inside server {server} : {shardsinserver}")
            serverPayload_json = {
                "schema": schema,
                "shards": shardsinserver
            }
            print(serverPayload_json)
            tries = 0
            print("Calling config for ",server)
            logger.info(f"Calling config for {server}")
            
            try:
                url = f"http://{server}:5000/config"
                res=requests.post(url,json=serverPayload_json).json()
                logger.info(f"Response from {server} is :{res}")
            except Exception as e:
                logger.info(f"The routed {server} is not yet Initialized, Retrying ....{tries}")

            
            for shard in shardsinserver:
                logger.info(f"Fetching Shard : {shard}, as it is present in {server}. Shard_In_Server:  {shardsinserver}")
                if shard in serverForShard:
                    logger.info(f"Shard : {shard} in Serverforshard: {serverForShard}")
                    # currID,___ = queryHandler.getCurrIdx(shardName=shard)
                    copyRES = {}
                    # for oldserver in serverForShard[shard]:
                    primaryServer = queryHandler.getPrimary(shard)
                    logger.info(f"Starting data Copying from {primaryServer} to new server {server}")
                    copyJSON = {
                        "shards" : [shard]
                    }
                    url = f"http://{primaryServer}:5000/copy"
                    copyRES = requests.get(url,json=copyJSON).json()
                    # logger.info(f"Copy endpoint of {oldserver} gave response {copyRES}")
                    logger.info(f"Fetched data from {primaryServer}: {copyRES}")
                    if copyRES["status"] != "success":
                        return jsonify({"error":f"Could not fetch data from primary server {primaryServer} for shard- {shard}"})
                    logger.info(f"Starting Data Writing from {primaryServer} of {shard} for {server}")
                    data = copyRES[shard]

                    writeJSON ={
                        "shard": shard,
                        "curr_idx" : 0,
                        "data": data,
                        "slaves":[]
                    }
                    logger.info(f"Json for wrtting the data to newly added {server}:{writeJSON}")

                    url = f"http://{server}:5000/write"
                    writeRES = requests.post(url, json=writeJSON).json()

                    logger.info(f"Response from {server} is : {writeRES}")
                    logger.info(f"Copied data of {shard} from {primaryServer} to {server}")
                    queryHandler.updateCurrIdx(writeRES["current_idx"],shardName=shard)
                    logger.info("Updated current index in newly added servers")

        response_data = {
            "N": len(queryHandler.getServerList()),
            "message": f"Add {', '.join(servers.keys())}",
            "status": "successful"
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_response = {
            "message": f"Error during adding new servers: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500

def select_random_elements(A, B, n):
    # Convert lists to sets to find the difference
    difference = set(A) - set(B)
    
    # Convert the set back to a list
    difference_list = list(difference)
    
    # Ensure we don't try to select more elements than available
    num_elements_to_select = min(n, len(difference_list))
    
    # Select and return n random elements from the difference
    return random.sample(difference_list, min(num_elements_to_select,len(difference_list)))

@app.route('/rm', methods=['DELETE'])
def remove_servers():
    global mutex_locks,replicas,shardServerMap, MAX_RETRIES,schema, SHARD_REPLICAS
    
    try:
        # Extract data from the request
        payload_json = request.get_json()
        n = payload_json["n"]
        servers_to_remove = payload_json["servers"]

        # Simple sanity checks on the request payload
        if n < len(servers_to_remove):
            error_response = {
                "message": "Length of server list is more than removable instances",
                "status": "failure"
            }
            return jsonify(error_response), 400

        # create list of severs to be removed
        servers = queryHandler.getServerList()
        chooseRandomServer = select_random_elements(servers,servers_to_remove,n-len(servers_to_remove))
        logger.info(f"random servers purge - {chooseRandomServer}")
        servers_to_remove.extend(chooseRandomServer)
        logger.info(f"Server to remove -{servers_to_remove}")

        # delete from replicas
        replicas = select_random_elements(replicas,servers_to_remove,len(servers) - len(servers_to_remove))
        logger.info(f"after removal - {replicas}")
        
        # delete from consistant hashmaps shardServerMap
        for server in servers_to_remove:
            for shard in queryHandler.getShardsinServer(server):
                shardServerMap[shard].remove_server_container(server)
        logger.info(f"updated consistant hashmaps")

        #delete entry from mapT
        deletedShards = {}
        beforeDel = queryHandler.getShardList()
        for server in servers_to_remove:
            for shard in queryHandler.getShardsinServer(server):
                if shard not in list(deletedShards.keys()):
                    deletedShards[shard] = {}
                    deletedShards[shard]["servers"] = []
                    deletedShards[shard]["primary"] = queryHandler.getPrimary(shard)
                deletedShards[shard]["servers"].append(server)
            queryHandler.deleteServer(server)
        afterDel = queryHandler.getShardList()
        logger.info(f"potential danger - {deletedShards}")

        # list of shards to be transfered
        danger = select_random_elements(beforeDel,afterDel,len(beforeDel)-len(afterDel))
        logger.info(f"need to transfer - {danger}")
        
        # transfer the danger shards to random servers
        for shard in danger:
        
            randomServer = random.sample(replicas,SHARD_REPLICAS)
            logger.info(f"start migrating {shard} to {randomServer}")
            #send config of shard to random server 
            configJSON = {
                "schema": schema,
                "shards": [shard]
            }
            logger.info(f"config JSON - {configJSON}")
            for newLoc in randomServer:
                url = f"http://{newLoc}:5000/config"
                res=requests.post(url,json=configJSON).json()
                if(res["status"]=="success"):
                    logger.info(f"configured {shard} in {newLoc}")
                else:
                    logger.info(f"FAILURE in configuring {shard} in {newLoc}")
            #copy contents from old server
            
            copyJSON = {
                "shards" : [shard]
            }
            old_primary = deletedShards[shard]["primary"]
            logger.info(f"copy JSON - {copyJSON} copying from {old_primary}")
            url = f"http://{old_primary}:5000/copy"
            copyRES = requests.get(url,json=copyJSON).json()
            data = copyRES[shard]            
            #write content to new server
            writeJSON ={
                "shard": shard,
                "curr_idx" : 0,
                "data": data,
                "slaves":[]
            }
            for newLoc in randomServer:
                url = f"http://{newLoc}:5000/write"
                writeRES = requests.post(url, json = writeJSON).json()
                logger.info(f"transfered to {newLoc} status -{writeRES}")
                
            
            for newLoc in randomServer:
                #update mapT
                queryHandler.nrq(f"INSERT INTO mapT (Shard_id, Server_id) VALUES ('{str(shard)}','{str(newLoc)}')")
                #update consistant hashmap
                shardServerMap[shard].add_server_container(newLoc)
            
        for shard in queryHandler.getShardList():
            logger.info(f"Running leader election for {shard}")
            try:
                old_primary = queryHandler.getPrimary(shard)
            except Exception as e:
                old_primary = ""
            logger.info(f"Old Primary {old_primary} for {shard}")
            serverList = queryHandler.whereIsShard(shard)
            logger.info(f"candidates for new primary for {shard} are {serverList}")
            request_json ={
                "shard": shard,
                "servers": serverList,
                "old_primary": old_primary
            }
            try:
                url = "http://shardmanager:5000/primary_elect"
                res = requests.get(url, json = request_json).json()
                if res["status"] == "success":
                    new_primary = res["primary"]
                    logger.info(f"New Primary {new_primary} for {shard}")
                    queryHandler.changePrimary(new_primary,shard)
                else:
                    logger.info(f"primary elect endpoint gives wrong return")
            except Exception as e:
                logger.info(f"primary elect endpoint not working")
                return jsonify({"error": str(e)}),500

        # kill server containers
        for server in servers_to_remove:
            # replicas.remove(server)
            os.system(f"sudo docker stop {server} && sudo docker rm {server}")
            logger.info(f"stopped {server}")
        
        response_data = {
            "message": {
                "N": len(replicas),
                "servers": queryHandler.getServerList()
            },
            "status": "successful"
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_response = {
            "message": f"Error during removing servers: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500

@app.route('/read', methods=['POST'])
def read_data():
    try:
        # Extract data from the request
        # global database_configuration
        payload_json = request.get_json()
        stud_id_range = payload_json["Stud_id"]

        # Placeholder for queried shards and data
        shards_queried = []
        queried_data = []

        # Iterate through shards to find relevant ones based on Stud id range
        shardList = queryHandler.getShardList()

        for shard in shardList:
            stud_id_low,_ = queryHandler.getStud_id_low(shardName=shard)
            shard_size,__ = queryHandler.getStud_size(shardName=shard)

            # Check if the shard contains relevant data based on the Stud id range
            # low:5000 high:8000
            if stud_id_low <= stud_id_range["high"] and (stud_id_low + shard_size) >= stud_id_range["low"]:
                shards_queried.append(shard)

                serverPayload_json ={
                    "shard" :shard,
                    "Stud_id": stud_id_range
                    }
                req_id=random.randint(100000,999999)
                server = shardServerMap[shard].get_server_container(req_id)  
                logger.info(f"Read:: Obtained {server} by consistantHashmap") 
                try:
                    url = f"http://{server}:5000/read"
                    res=requests.post(url,json=serverPayload_json).json()
                    # flag=False
                    logger.info(f"Response from {server} is :{res}")
                    # success_count+=1
                except Exception as e:
                    logger.info(f"Reading failure")

                queried_data.extend(res["data"])

        response_data = {
            "shards_queried": shards_queried,
            "data": queried_data,
            "status": "success"
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_response = {
            "message": f"Error during reading data: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500

@app.route('/write', methods=['POST'])
def write_data():
    try:
        # Extract data from the request
        global mutex_locks
        payload_json = request.get_json()
        data = payload_json["data"]
        logger.info(f"Fetched data: {data}")
        success_count = 0
        failed_entries = []
        
        # Iterate through data entries and write to the database
        for entry in data:
            logger.info(f"Entry in data: {entry}")
            stud_id = entry["Stud_id"]
            shard_id = get_shard_id(stud_id)

            # Acquire mutex lock for the shard
            mutex_lock = mutex_locks[shard_id]
            mutex_lock.acquire()
            logger.info("Mutex lock accquired")
            try:
                # Get all servers having replicas of the shard
                primaryServer = queryHandler.getPrimary(shardID=shard_id)
                serverList = queryHandler.whereIsShard(shardID=shard_id)
                serverList.remove(primaryServer)
                logger.info(f"{primaryServer} is Primary for {shard_id}.")
                logger.info(f"Slave list  is {serverList} for {shard_id}.")
                
                # Write entries in all servers of the shard
                # for server in serverList:
                # write_successful = write_entries_to_servers(servers, entry)
                currID,___ = queryHandler.getCurrIdx(shardName=shard_id)
                
                serverPayload_json ={
                "shard" :shard_id,
                "curr_idx" : currID,
                "data" : [entry],
                "slaves": serverList
                }
                logger.info(f"payload - {serverPayload_json}")
                logger.info(f"{shard_id} is available on {primaryServer}")
                try:
                    url = f"http://{primaryServer}:5000/write"
                    res=requests.post(url,json=serverPayload_json).json()
                    logger.info(f"Response from {primaryServer} is :{res}")
                    success_count+=1
                except Exception as e:
                    logger.info(f"The Data entrie is not added with stud_id {stud_id} in shard_id {shard_id} on {primaryServer}")
                    error_response = {
                        "message": f"Error during writing data: {str(e)}",
                        "status": "error"
                    }
                    return jsonify(error_response), 500

                #update currIDX
                queryHandler.updateCurrIdx(currID+1,shardName=shard_id)
                logger.info("updated current index")
            finally:
                # Release the mutex lock for the shard
                mutex_lock.release()
                logger.info("mutex lock released")

        # Dummy response for demonstration purposes
        response_data = {
            "message": f"{success_count} Data entries added",
            "status": "success"
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_response = {
            "message": f"Error during writing data: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500

# Function to get the shard id based on the Stud id
def get_shard_id(stud_id):
    logger.info("Fetching Shard_id")
    shardList = queryHandler.getShardList()
    for shardN in shardList:
        stud_id_low,_ = queryHandler.getStud_id_low(shardName=shardN)
        shard_size,__ = queryHandler.getStud_size(shardName=shardN)
        logger.info(f"ShardID : {shardN} Stud_id_low: {stud_id_low} Shard_size: { shard_size}")
        if stud_id_low <= stud_id < stud_id_low + shard_size:
            return shardN

# Function to write entries to all servers of a shard
def write_entries_to_servers(servers, entry):
    time.sleep(0.1)
    return True

# Function to update the valid idx of a shard in the metadata
def update_valid_idx(shard_id):
    # Placeholder for actual update logic (replace with your actual logic)
    pass

@app.route('/update', methods=['PUT'])
def update_data():
    global mutex_locks
    try:
        # Extract data from the request
        global  mutex_locks
        payload_json = request.get_json()
        stud_id = payload_json["Stud_id"]
        data =payload_json["data"]

        try:
            shardName = get_shard_id(stud_id)
            # Get all servers having replicas of the shard
            primaryServer = queryHandler.getPrimary(shardID=shardName)
            serverList = queryHandler.whereIsShard(shardID=shardName)
            serverList.remove(primaryServer)
            logger.info(f"{primaryServer} is Primary for {shardName}.")
            logger.info(f"Slave list  is {serverList} for {shardName}.")             # Acquire mutex lock for the shard
            mutex_lock = mutex_locks[shardName]
            mutex_lock.acquire()
            updateShard = 0
            serverPayload_json ={
                    "shard" :shardName,
                    "Stud_id" :stud_id,
                    "data" : data,
                    "slaves": serverList
            }
            # for server in servers:
            
            try:
                url = f"http://{primaryServer}:5000/update"
                res=requests.put(url,json=serverPayload_json).json()
                logger.info(f"Response from {primaryServer} is :{res}")
                updateShard+=1
            except Exception as e:
                logger.info(f"The stud_id {stud_id} is not updated on {primaryServer}")


            if updateShard:
                success=res["successCount"]
                failed = res["FailedServer"]
                response_data = {
                    "message": f"Data entry for Stud_id: {stud_id} updated in {success}, Failed in {failed}",
                    "status": "success"
                }
            else:
                response_data = {
                    "message": f"Failed to update data entry for Stud_id: {stud_id}",
                    "status": "failure"
                }

                return jsonify(response_data), 500
            return jsonify(response_data), 200

        finally:
            # Release the mutex lock for the shard
            mutex_lock.release()

    except Exception as e:
        error_response = {
            "message": f"Error during updating data: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500

@app.route('/del', methods=['DELETE'])
def delete_data():
    try:
        # Extract data from the request
        global mutex_locks
        payload_json = request.get_json()
        stud_id = payload_json["Stud_id"]
        logger.info(f"fetched payload {stud_id}")
        try:
            # Get the shard id for the provided Stud id
            shardName = get_shard_id(stud_id=stud_id)
            logger.info(f"{stud_id} is in {shardName}")
            # call primary server
            primaryServer = queryHandler.getPrimary(shardID=shardName)
            serverList = queryHandler.whereIsShard(shardID=shardName)
            serverList.remove(primaryServer)
            logger.info(f"{primaryServer} is Primary for {shardName}.")
            logger.info(f"Slave list  is {serverList} for {shardName}.") 
            # Acquire mutex lock for the shard
            mutex_lock = mutex_locks[shardName]
            mutex_lock.acquire()
            logger.info(f"{shardName} Mutex lock acquired")
            serverPayload_json ={
                "shard" :shardName,
                "Stud_id" :stud_id,
                "slaves": serverList
                
            }
            
            currID,___ = queryHandler.getCurrIdx(shardName=shardName)
            logger.info(f"payload - {serverPayload_json}")
            url = f"http://{primaryServer}:5000/del"
            res=requests.delete(url,json=serverPayload_json).json()
            logger.info(f"Response from {primaryServer} is :{res}")
            
            if res["status"] == "success":
                #update currIDX
                success=res["successCount"]
                failed = res["FailedServer"]
                queryHandler.updateCurrIdx(currID-1,shardName=shardName)
                logger.info("updated current index")
                response_data = {
                    "message": f"Data entry with Stud_id:{stud_id} removed in {success}, Failed in {failed}",
                    "status": "success"
                }
            else:
                response_data = {
                    "message": f"Failed to remove data entry with Stud_id:{stud_id}",
                    "status": "failure"
                }

            return jsonify(response_data), 200

        finally:
            # Release the mutex lock for the shard
            mutex_lock.release()

    except Exception as e:
        error_response = {
            "message": f"Error during deleting data: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500

if  __name__ == '__main__':
    
    app.run(host='0.0.0.0',port=5000,debug=True)