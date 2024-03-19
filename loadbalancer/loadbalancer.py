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
################Initialize the Datbase for Loadbalance#############

mapT_json = {
    "schema" : {"columns":["Shard_id","Server_id"],
                "dtypes":["String","String"]},
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


######################### Difining the another thread to check server status #######################
def replica_status(replicas):
    while True:

        ####################Respwn Method 1###############################

        for replica in replicas:

            alive = None
            alive = os.system(f"ping -c 1 {replica}")
            if alive is None:
                res=os.popen(f"sudo docker run --name {replica} --network net1 --network-alias {replica} -e 'SERVER_ID={replica}' -d server:latest").read()

                if len(res)==0:
                    print(f"Unable to start {replica}")
                else:
                    print(f"successfully started {replica}")

        ####################Respwn Method 2###############################

        # missingContainerOut = os.popen("sudo docker ps --format '[[ .Names ]]'").read().split("\n")
        # missingContainerOut = missingContainerOut[:len(missingContainerOut)-1] 
        # for replica in replicas:
        #     if replica not in missingContainerOut:
        #         print(f"{replica} is failed initiate, Trying to respwn")
        #         res=os.popen(f"sudo docker run --name {replica} --network net1 --network-alias {replica} -e 'SERVER_ID={replica}' -d server:latest").read()

        #         if len(res)==0:
        #             print(f"Unable to start {replica}")
        #         else:
        #             print(f"successfully started {replica}")

        ################Remove Unwanted container or respwn previous container automatically #############################
        extraContainerOut = os.popen("sudo docker ps --format '[[ .Names ]]'").read().split("\n")
        extraContainerOut = extraContainerOut[:len(extraContainerOut)-1]
        for container in extraContainerOut:
            if container not in replicas and container=="loadbalancer":
                os.system(f"sudo docker stop {container} && sudo docker rm {container}")
        time.sleep(1)

################ Calling Server thread ###############
# server_thread = threading.Thread(target=replica_status,args=(replicas,))
# server_thread.start()





@app.route('/')
def index():
    return "Welcome to HELLO WORLD"

@app.route('/rep', methods=['GET'])
def rep():
    # for replica in replicas:
    #     out = os.popen(f'sudo docker run --name {replica} --network net1 -e "SERVER_ID={replica}" -d server').read()
        # subprocess.run(f"sudo docker run --name {replica} --network net1 -e 'SERVER_ID={replica}' -d server",shell=True)

    response_json = {

        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status" : "successful"
    }
    return jsonify(response_json), 200


@app.route('/add',methods = ['POST'])
def add_replicas():
    payload_json = request.get_json()
    noOfServer = payload_json.get('n')
    nameOfHostnames = payload_json.get('hostnames', [])
    if len(nameOfHostnames) > noOfServer:
        response_json = {
            "message":"<Error> Length of hostname list is more than newly added instances",
            "status" : "Failure"
        }
        return jsonify(response_json), 400
        
    for i in range(noOfServer):
        if i < len(nameOfHostnames):
            replica = nameOfHostnames[i]
        else:
            replica = f"RandomServer{random.randint(100000, 999999)}"
        replicas.append(replica)
        # consistent_hash_map.add_server_container(int(replica[1:]))
        consistent_hash_map.add_server_container(replica)
        os.system(f"sudo docker run --name {replica} --network net1 --network-alias {replica} -e 'SERVER_ID={replica}' -d server:latest")
    response_json = {
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status" : "successful"
    }

    return jsonify(response_json), 200

@app.route('/rm', methods=['DELETE'])
def remove_replicas():
    payload_json = request.get_json()
    noOfServer = payload_json.get('n')
    nameOfHostnames = payload_json.get('hostnames', [])

    if len(nameOfHostnames) > noOfServer:
        response_json = {
            "message":"<Error> Length of hostname list is more than newly removable instances",
            "status" : "Failure"
        }
        return jsonify(response_json), 400
    
    removed_replicas = []

    for i in range(noOfServer):
        if i < len(nameOfHostnames):
            replica = nameOfHostnames[i]
        else:
            replica = random.choice(replicas)
        removed_replicas.append(replica)
        os.system(f"sudo docker stop {replica} && sudo docker rm {replica}")
        # os.system(f"sudo docker stop {replica}")
        replicas.remove(replica)
        # consistent_hash_map.remove_server_container(int(replica[1:]))
        consistent_hash_map.remove_server_container(replica)

    response_json = {
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status" : "successful"
    }

    return jsonify(response_json), 200

@app.route('/<req_path>', methods=['GET'])
def route_request(req_path):
    req_id=random.randint(100000,999999)
    replica = consistent_hash_map.get_server_container(req_id)
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
        global database_configuration,mutex_locks,replicas,shardServerMap, MAX_RETRIES
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
                if server.find("[") != -1:
                    #Handled Server[5] Case
                    while True:
                        #if randomly choosed server is present in keyist
                        serverName = f"Server{random.randint(100000,999999)}" 
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
        queryHandler.InsertLBmapT(row=servers)
        print("inserted values to tables")
        # Initialize mutex locks for each shard
        for shard in shards:
            id = shard['Shard_id']
            shardServerMap[id] = ConsistentHashMap(num_containers=0, total_slots= TOTAL_SLOTS, num_virtual_servers=NUM_VIRTUAL_SERVERS)
            serverContainer = queryHandler.whereIsShard(id)
            for server in serverContainer:
                shardServerMap[id].add_server_container(server)
        print(shardServerMap)
        mutex_locks = {shard["Shard_id"]: threading.Lock() for shard in database_configuration["shards"]}

        # /config call of individual servers.
        for server in servers:
            shardsinserver = queryHandler.getShardsinServer(server)
            print(shardsinserver)
            serverPayload_json = {
                "schema": schema,
                "shards": shardsinserver
            }

            retries = MAX_RETRIES
            while(retries > 0):
                retries-=1
                #call api
                url = f"http://{server}:5000/config"
                res=requests.get(url,timeout = 5).json()
                app.logger.warn(res)

                if res["status"] == "success":
                    break
        # the database initialization 

        response_json = {
            "message": "Configured Database",
            "status": "success"
        }

        return jsonify(response_json), 200

    except Exception as e:
        error_response = {
            "message": f"Error during initialization: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500
    
@app.route('/status', methods=['GET'])
def get_database_status():
    global database_configuration
    if database_configuration:
        return jsonify(database_configuration), 200
    else:
        response_data = {
            "message": "Database not configured yet",
            "status": "error"
        }
        return jsonify(response_data), 404

@app.route('/add', methods=['POST'])
def add_servers():
    try:
        # Extract data from the request
        global database_configuration
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

        # Add new servers and shards to the configuration
        for i in range(n):
            new_server_id = f"Server{random.randint(1000, 9999)}"
            database_configuration["servers"][new_server_id] = servers.get(f"Server[{i}]", [])
            #server add

        # Update shard information
        database_configuration["N"] += n
        database_configuration["shards"].extend(new_shards)

        response_data = {
            "N": database_configuration["N"],
            "message": f"Add {', '.join(database_configuration['servers'].keys())}",
            "status": "successful"
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_response = {
            "message": f"Error during adding new servers: {str(e)}",
            "status": "error"
        }
        return jsonify(error_response), 500

@app.route('/rm', methods=['DELETE'])
def remove_servers():
    try:
        # Extract data from the request
        global database_configuration
        payload_json = request.get_json()
        n = payload_json["n"]
        servers_to_remove = payload_json["servers"]

        # Simple sanity checks on the request payload
        if n > len(servers_to_remove):
            error_response = {
                "message": "Length of server list is more than removable instances",
                "status": "failure"
            }
            return jsonify(error_response), 400

        # Remove servers and update shard information
        for server in servers_to_remove:
            if server in database_configuration["servers"]:
                del database_configuration["servers"][server]
                #server remove

        response_data = {
            "message": {
                "N": database_configuration["N"],
                "servers": list(database_configuration["servers"].keys())
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
        global database_configuration
        payload_json = request.json
        stud_id_range = payload_json["Stud_id"]

        # Placeholder for queried shards and data
        shards_queried = []
        queried_data = []

        # Iterate through shards to find relevant ones based on Stud id range
        for shard in database_configuration["shards"]:
            shard_id = shard["Shard_id"]
            stud_id_low = shard["Stud_id_low"]
            shard_size = shard["Shard_size"]

            # Check if the shard contains relevant data based on the Stud id range
            if stud_id_low <= stud_id_range["high"] and (stud_id_low + shard_size) >= stud_id_range["low"]:
                shards_queried.append(shard_id)

                # Placeholder for data in the shard
                shard_data = []

                # Fetch data from the shard based on Stud id range
                for i in range(stud_id_range["low"], stud_id_range["high"] + 1):
                    shard_data.append({
                        "Stud_id": i,
                        "Stud_name": f"Student{i}",
                        "Stud_marks": i % 100
                    })

                queried_data.extend(shard_data)

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
        global database_configuration, mutex_locks
        payload_json = request.get_json()
        data = payload_json["data"]
        # Placeholder for response details
        success_count = 0
        failed_entries = []

        # Iterate through data entries and write to the database
        for entry in data:
            stud_id = entry["Stud_id"]
            shard_id = get_shard_id(stud_id)

            # Acquire mutex lock for the shard
            mutex_lock = mutex_locks[shard_id]
            mutex_lock.acquire()

            try:
                # Get all servers having replicas of the shard
                servers = database_configuration["servers"].get(shard_id, [])

                # Write entries in all servers of the shard
                write_successful = write_entries_to_servers(servers, entry)

                # Update the valid idx of the shard in the metadata if writes are successful
                if write_successful:
                    update_valid_idx(shard_id)

                    # Increment success count
                    success_count += 1
                else:
                    failed_entries.append(entry)

            finally:
                # Release the mutex lock for the shard
                mutex_lock.release()

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
    for shard in database_configuration["shards"]:
        stud_id_low = shard["Stud_id_low"]
        shard_size = shard["Shard_size"]

        if stud_id_low <= stud_id < stud_id_low + shard_size:
            return shard["Shard_id"]

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
    try:
        # Extract data from the request
        global database_configuration, mutex_locks
        payload_json = request.get_json()
        stud_id = payload_json["Stud_id"]
        data_entry =payload_json["data"]

        # Get the shard id for the provided Stud id
        shard_id = get_shard_id(int(stud_id))

        # Acquire mutex lock for the shard
        mutex_lock = mutex_locks[shard_id]
        mutex_lock.acquire()

        try:
            # Get all servers having replicas of the shard
            servers = database_configuration["servers"].get(shard_id, [])

            # Update the data entry in all servers of the shard
            update_successful = update_entry_in_servers(servers, data_entry)

            if update_successful:
                response_data = {
                    "message": f"Data entry for Stud_id: {stud_id} updated",
                    "status": "success"
                }
            else:
                response_data = {
                    "message": f"Failed to update data entry for Stud_id: {stud_id}",
                    "status": "failure"
                }

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

# Function to get the shard id based on the Stud id
def get_shard_id(stud_id):
    for shard in database_configuration["shards"]:
        stud_id_low = shard["Stud_id_low"]
        shard_size = shard["Shard_size"]

        if stud_id_low <= stud_id < stud_id_low + shard_size:
            return shard["Shard_id"]

# Function to update an entry in all servers of a shard
def update_entry_in_servers(servers, data_entry):
    time.sleep(0.1)
    return True

@app.route('/del', methods=['DELETE'])
def delete_data():
    try:
        # Extract data from the request
        global database_configuration, mutex_locks
        payload_json = request.get_json()
        stud_id = payload_json["Stud_id"]

        # Get the shard id for the provided Stud id
        shard_id = get_shard_id(int(stud_id))

        # Acquire mutex lock for the shard
        mutex_lock = mutex_locks[shard_id]
        mutex_lock.acquire()

        try:
            # Get all servers having replicas of the shard
            servers = database_configuration["servers"].get(shard_id, [])

            # Delete the data entry from all servers of the shard
            delete_successful = delete_entry_from_servers(servers, stud_id)

            if delete_successful:
                response_data = {
                    "message": f"Data entry with Stud_id:{stud_id} removed from all replicas",
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

# Function to get the shard id based on the Stud id
def get_shard_id(stud_id):
    for shard in database_configuration["shards"]:
        stud_id_low = shard["Stud_id_low"]
        shard_size = shard["Shard_size"]

        if stud_id_low <= stud_id < stud_id_low + shard_size:
            return shard["Shard_id"]

# Function to delete an entry from all servers of a shard
def delete_entry_from_servers(servers, stud_id):
    time.sleep(0.1)
    return True

if  __name__ == '__main__':
    
    app.run(host='0.0.0.0',port=5000,debug=True)