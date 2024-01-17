from flask import Flask,request,jsonify,url_for,redirect
import random
import os
from consistant_HASHMAP import ConsistentHashMap  
app = Flask(__name__)

NUM_CONTAINERS = 3
TOTAL_SLOTS = 512
NUM_VIRTUAL_SERVERS = 9

consistent_hash_map = ConsistentHashMap(NUM_CONTAINERS, TOTAL_SLOTS, NUM_VIRTUAL_SERVERS)

replicas = [f"Server {i}" for i in range(1, NUM_CONTAINERS + 1)]

for replica in replicas:
    consistent_hash_map.add_server_container(int(replica[7]))

@app.route('/')
def index():
    return "Welcome to HELLO WORLD"

@app.route('/rep', methods=['GET'])
def rep():
    # for replica in replicas:
        # os.system(f"sudo docker run --name {replica} -e 'SERVER_ID={replica}' ")
    response_json = {

        "message": {
            "N": NUM_CONTAINERS,
            "replicas": replicas
        },
        "status" : "successful"
    }
    return jsonify(response_json), 200


@app.route('/add',methods = ['POST'])
def add_replicas():
    data = request.get_json()
    noOfServer = data.get('n')
    nameOfHostnames = data.get('hostnames', [])
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
            replica = f"RandomServer{random.randint(1, 100)}"
        replicas.append(replica)
        consistent_hash_map.add_server_container(int(replica[1:]))
        # os.system(f"sudo docker run --name {replica} -e 'SERVER_ID={replica}' ")

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
    data = request.get_json()
    noOfServer = data.get('n')
    nameOfHostnames = data.get('hostnames', [])

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
        # os.system(f"sudo docker stop {replica} && sudo docker rm {replica}")
        replicas.remove(replica)
        consistent_hash_map.remove_server_container(int(replica[1:]))

    response_json = {
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status" : "successful"
    }

    return jsonify(response_json), 200

@app.route('/<path>', methods=['GET'])
def route_request(path):
    replica = consistent_hash_map.get_server_container(hash(path))

    # res=os.popen(f"sudo docker run --name {replica} --network net1 --network-alias {replica} -e VAR1=v1 -e VAR2=v2 -d server:latest").read()

    # if len(res)==0:
    #     print(f"Unable to start {replica}")
    # else:
    #     print(f"successfully started {replica}")

    if replica in replicas:
        url = f"{replica}:5000/{path}"
        return redirect(url,code=302)
    else:
        response_json = {
            "message": f"<Error> '{path}' endpoint does not exist in server replicas",
            "status" : "Failure"
        }
        return jsonify(response_json), 400



if  __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')