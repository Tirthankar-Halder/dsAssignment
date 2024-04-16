from flask import (Flask,request,jsonify,render_template,abort,url_for,json)
import sqlite3
import mysql.connector
import os
import time
import logging
import threading
from assist import *
import logging 
import random
# logging.basicConfig(filename="serverLog.log",format='%(asctime)s %(message)s',filemode = 'w')

logger = logging.getLogger('ShardManager:')

def select_random_elements(A, B, n):
    # Convert lists to sets to find the difference
    difference = set(A) - set(B)
    
    # Convert the set back to a list
    difference_list = list(difference)
    
    # Ensure we don't try to select more elements than available
    num_elements_to_select = min(n, len(difference_list))
    
    # Select and return n random elements from the difference
    return random.sample(difference_list, min(num_elements_to_select,len(difference_list)))
def getShardsinServer(res,replica):
    return res["servers"][replica]
def whereIsShard(res,shard):
    shards = res["shards"]
    server = []
    for row in shards:
        if row["Shard_id"] == shard:
            server.append(row["primary_server"])

    return server

    

def replica_status():
    # global serverInitializaton
    
    while True:
        ####################Respwn Method 1###############################
        try:
            url = "http://loadbalancer:5000/status"
            res=requests.get(url).json()
            schema = res["schema"]
            replicas = res["servers"]
        except :
            continue

        for replica in replicas:

            # alive = None
            alive = os.system(f"ping -c 1 {replica}")
            logger.info(f"Livenness of {replica} is {alive}, Available replica {replicas}")
            if alive :
                logger.info(f"{replica} is down... Trying to Re-initialize ...")
                res = os.popen(f"sudo docker rm {replica}")
                shradinReplica = getShardsinServer(res,replica)
                res=os.popen(f"sudo docker run --name {replica} --network net1 --network-alias {replica} -e 'SERVER_ID={replica}' -d server:latest").read()
                # res=os.popen(f"sudo docker restart {replica}").read()
                time.sleep(20)

                logger.info("I am waiting for server to Re-initilize....... ")
                logger.info(f"Intialized server:{replica}")
                # shardsinserver = queryHandler.getShardsinServer(server)
                logger.info(f"shards list inside server : {shradinReplica}")
                serverPayload_json = {
                    "schema": schema,
                    "shards": shradinReplica
                }
                logger.info(f"Server paylod at config: {serverPayload_json}")
                print(serverPayload_json)
                tries = 0
                print("Calling config for ",replica)
                logger.info(f"Calling config for {replica}")
            
                try:
                    url = f"http://{replica}:5000/config"
                    res=requests.post(url,json=serverPayload_json).json()
                    logger.info(f"Response from {replica} is :{res}")
                except Exception as e:
                    logger.info(f"The routed {replica} is not yet Initialized, Retrying ....{tries}")

                shardsToCopy = getShardsinServer(res,replica)
                for shard in shardsToCopy:
                    serverToCopyFrom = select_random_elements(whereIsShard(res,shard),[replica],len(whereIsShard(res,shard))-1)
                    copyRES = {}
                    for oldserver in serverToCopyFrom:
                        logger.info(f"Starting data migration from {oldserver} to new server {replica}")
                        copyJSON = {
                            "shards" : [shard]
                        }
                        url = f"http://{oldserver}:5000/copy"
                        copyRES = requests.get(url,json=copyJSON).json()
                        # logger.info(f"Copy endpoint of {oldserver} gave response {copyRES}")
                        logger.info(f"Fetched data from {oldserver}: {copyRES}")
                        if copyRES["status"] == "success":
                            break
                    logger.info(f"Starting Data migration from {oldserver} of {shard} for {replica}")
                    data = copyRES[shard]
                    writeJSON ={
                        "shard": shard,
                        "curr_idx" : 0,
                        "data": data
                    }
                    logger.info(f"Json for wrtting the data to newly added {replica}:{writeJSON}")

                    url = f"http://{replica}:5000/write"
                    writeRES = requests.post(url, json=writeJSON).json()

                    logger.info(f"Response from {replica} is : {writeRES}")
                    logger.info(f"Copied data of {shard} from {oldserver} to {replica}")
                # if replica not in queryHandler.getServerList():
                #     #handled: skipped if server is already present(valid for second time init call)
                #     if replica.find("[") != -1:
                #         #Handled Server[5] Case
                #         while True:
                #             #if randomly choosed server is present in keyist
                #             serverName = f"Server{random.randint(0,999999999)}" 
                #             os.system(f'sudo docker run --name {serverName} --network net1 --network-alias {serverName} -e "SERVER_ID={serverName}" -d server:latest')
                #             replicas.append(serverName)
                #             if serverName != replica :
                #                 #replaced the server key information with randomly choosed name
                #                 replicas[serverName] = replicas[replica]
                #                 del replicas[replica]
                #             break
                #     else:
                #         os.system(f'sudo docker run --name {replica} --network net1 --network-alias {replica} -e "SERVER_ID={replica}" -d server:latest')
                #         replicas.append(replica)
                #     logger.info(f"Container {replica} is added. New available server : {replicas}")

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
        time.sleep(5)
    

############### Calling Server thread ###############
server_thread = threading.Thread(target=replica_status)
server_thread.start()

# server_thread = threading.Thread(target=replica_status,args=(replicas,))
# server_thread.start()
app = Flask(__name__,template_folder='.')

@app.route('/primary_elect', methods=['GET'])
def primary_election():
    payload_json = request.get_json()
    shardName = payload_json.get('shard')
    serverList = payload_json.get('servers')
    old_primary = payload_json.get('old_primary')
    print("inside shardmanager")
    if old_primary != "" and old_primary in serverList:
        try:
            res = requests.get(f"http://{old_primary}:5000/heartbeat")
            response_json = {
                "primary" : old_primary,
                "status": "success"
            }
            return jsonify(response_json),200
        except Exception as e:
            pass

    length = 0
    new_primary = None
    request_json = {
        "shard": shardName
    }
    for server in serverList:
        
        try:
            url = f"http://{server}:5000/log"
            response = requests.get(url,json=request_json).json()

            if response["status"] == "success" and response["length"] > length:
                length = response["length"]
                new_primary = server
        except Exception as e:
            pass

    if new_primary == None:
        return jsonify({
            "primary" : new_primary,
            "status": "failure"
        }),500
    
    return jsonify({
        "primary" : new_primary,
        "status": "success"
    }),200
    

@app.route('/')
def index():
    return "Welcome to ShardManager"


if  __name__ == '__main__':
    # app.run(debug=True,host='0.0.0.0')
    app.run(host='0.0.0.0',port=5000,debug=True)
