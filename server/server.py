from flask import (Flask,request,jsonify,render_template,abort,url_for,json)
import sqlite3
import mysql.connector
import os
from assist import *
# import logging 

# logging.basicConfig(filename="serverLog.log",format='%(asctime)s %(message)s',filemode = 'w')

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

app = Flask(__name__,template_folder='.')
 
# connected=False
# while not connected:
#     try:
#         mydb = mysql.connector.connect(host="localhost",user="root",password="abc")
#         connected=True
#     except Exception:
#         pass
# print("Connection Established...")

# logger.info("Initializing Database")
queryHandler = SQLHandler()
# logger.info("Initialized Database and Databse Connected")


@app.route('/')
def index():
    return "Welcome to HELLO WORLD"


# @app.route('/<name>')
# def print_name(name):
#     return 'Hi, {}'.format(name)

@app.route('/home',methods = ['GET'])
def home():
    server_id = os.getenv('SERVER_ID', 'Unknown')
    response_json = {
        "message": f"Hello from : {server_id}",
        "status" : "successful"
        }
    return jsonify(response_json),200


@app.route('/heartbeat',methods = ['GET'])
def heartbeats():
    return jsonify({"Response": " "}),200

@app.route('/drop',methods = ['DELETE'])
def dropDB():
    try :
        queryHandler.DropDB("shardDB")
        print("Datbase Deleted")
        return jsonify("Datbase Deleted"),200
    except Exception as e:
        return jsonify(e),200
    
##############################################
shard_configurations = {}
@app.route('/config', methods=['POST'])
def configure_shards():
    try:
        payload_json = request.get_json()
        schema = payload_json.get('schema')
        shardsName = payload_json.get('shards', [])
        # Validate payload structure
        if 'schema' not in payload_json or 'shards' not in payload_json:
            return jsonify({"error": "Invalid payload structure"}), 400

        columnsName = payload_json['schema']['columns']
        dtypes = payload_json['schema']['dtypes']
        for shard in shardsName:
            tabName = queryHandler.hasTable(tabname=shard,columns=columnsName,dtypes=dtypes)
            shard_configurations[shard] = f"Server0:{shard} configured"
        response_json = {
            "message": ", ".join(shard_configurations.values()),
            "status" : "success"
        }
        return jsonify(response_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Placeholder for shard data
shard_data = {}

@app.route('/copy', methods=['GET'])
def copy_shard_data():
    try:
        payload_json = request.get_json()
        shardsName = payload_json.get('shards', [])

        # Validate payload structure
        if 'shards' not in payload_json:
            return jsonify({"error": "Invalid payload structure"}), 400

        shards = payload_json['shards']
        response_data = {}
        c=0
        for shard in shardsName:
            res,res_c = queryHandler.Copy(shard)
            c+=res_c
            print(res)
            response_data[shard] = str(res)
        
        if c==0:
             
            response_json = {
                **response_data,
                "status": "failure"
            }
        else:
            response_json = {
                **response_data,
                "status": "success"
            }
        return jsonify(response_json), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/read', methods=['POST'])
def read_shard_data():
    try:
        payload_json = request.get_json()
        shardName = payload_json.get('shard')
        studID = payload_json.get('Stud_id')
        # Validate payload structure
        if 'shard' not in payload_json or 'Stud_id' not in payload_json:
            return jsonify({"error": "Invalid payload structure"}), 400
        low, high = studID['low'], studID['high']
        if low>high:
            return jsonify({"error": "Invalid High and Low Value."}), 400
    
        res,flag = queryHandler.Read(shardName,low,high)
        if flag:
            response_json = {
                "data": res,
                "status": "success"
            }
        else:

            response_json = {
                "error": res,
                "status": "failure"
            }
        return jsonify(response_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500 


@app.route('/write', methods=['POST'])
def write_shard_data():
    shard_index = {}
    payload_json = request.get_json()
    shardName = payload_json.get('shard')
    currID = payload_json.get('curr_idx')
    newData = payload_json.get('data')

    # Validate payload structure
    if 'shard' not in payload_json or 'curr_idx' not in payload_json or 'data' not in payload_json:
        return jsonify({"error": "Invalid payload structure"}), 400
    
    error = queryHandler.Insert(table_name=shardName,row=newData)
    if error:
        return jsonify({"error": str(error)}),404
    shard_index[shardName] = currID + len(newData)

    response_json = {
        "message": "Data entries added",
        "current_idx": shard_index[shardName],
        "status": "success"
    }
    return jsonify(response_json), 200

@app.route('/update', methods=['PUT'])
def update_shard_data():
    payload_json = request.get_json()
    shardName = payload_json.get('shard')
    studID = payload_json.get('Stud_id')
    updateData = payload_json.get('data')

    # Validate payload structure
    if 'shard' not in payload_json or 'Stud_id' not in payload_json or 'data' not in payload_json:
        return jsonify({"error": "Invalid payload structure"}), 400
    
    count,flag = queryHandler.checkIfIdExists(shardName,studID)
    if flag == 0:
        return jsonify({"error": str(count)}), 404
    elif count == 0 :
        return jsonify({"error": f"Data entry for Stud_id:{studID} not found"})
    

    error = queryHandler.Update(shardN=shardName,updatedData=updateData,studID=studID)
    if error:
        return jsonify({"error": str(error)}), 404
    else:
        response_json = {
            "message": f"Data entry for Stud_id:{studID} updated",
            "status": "success"
        }
        return jsonify(response_json), 200
shard_data = {}

@app.route('/del', methods=['DELETE'])
def delete_data_entry():
    payload_json = request.get_json()
    shardName = payload_json.get('shard')
    studID = payload_json.get('Stud_id')

    # Validate payload structure
    if 'shard' not in payload_json or 'Stud_id' not in payload_json:
        return jsonify({"error": "Invalid payload structure"}), 400
    
    count,flag = queryHandler.checkIfIdExists(shardName,studID)
    if flag == 0:
        return jsonify({"error": str(count)}), 404
    elif count == 0 :
        return jsonify({"error": f"Data entry for Stud_id:{studID} not found"})
    
    error = queryHandler.Delete(shardName,studID)
    if error:
        response_json = {
            "message": f"Data entry with Stud_id:{studID} is not removed -",
            "error" : error,
            "status": "failure"
        }
    else:
        response_json = {
            "message": f"Data entry with Stud_id:{studID} removed",
            "status": "success"
        }
    return jsonify(response_json), 200

if  __name__ == '__main__':
    # app.run(debug=True,host='0.0.0.0')
    app.run(host='0.0.0.0',port=5000,debug=True)

