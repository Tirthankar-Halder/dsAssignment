from flask import Flask, request, jsonify
import sqlite3
conn = sqlite3.connect('studTable.db')

app = Flask(__name__)

# Endpoint to initialize shard tables in the server database
@app.route('/config', methods=['POST'])
def initialize_shards():
    # Implement initialization logic here
    # Parse request payload
    payload = request.json
    schema = payload.get('schema')
    shards = payload.get('shards')
    sh=[0 for i in range(len(shards))]

    cursor = conn.cursor()
    for sh,i in shards,range(len(shards)):
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{sh}'")
        # Fetch one row, if the table exists, it will return a non-empty result
        result_sh = cursor.fetchone()
        if result_sh:
            sh[i]=1
        
        """ else :
            cursor.execute('''CREATE TABLE IF NOT EXISTS ? (
                            ? ? PRIMARY KEY AUTOINCREMENT,
                            ? ? NOT NULL,
                            ? ? NOT NULL,
                            CONSTRAINT id_range CHECK (? BETWEEN 000000 AND 1000000),
                        )''',(sh,schema["columns"][0],'INTEGER' if schema["dtypes"][0]=="Number" else 'INT', schema["columns"][1],
                             'TEXT' if schema["dtypes"][1]=="string" else 'TEXT',schema["columns"][2],'TEXT' if schema["dtypes"][2]=="string" else 'FLOAT',schema["columns"][0]))
            cursor.commit() """
        cursor.execute(f"SELECT Server_id FROM MapT WHERE ")
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "message": "",
        "status": "success"
    }), 200

# Endpoint to send heartbeat responses
@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return '', 200

# Endpoint to copy data entries corresponding to one shard table in the server container
@app.route('/copy', methods=['GET'])
def copy_data():
    # Implement copying logic here
    # Parse request payload
    payload = request.json
    shards = payload.get('shards')
    
    # Copy data for specified shards
    # Implement your logic here
    
    return jsonify({
        "message": "Data copied successfully",
        "status": "success"
    }), 200

# Endpoint to read data entries from a shard in a particular server container
@app.route('/read', methods=['POST'])
def read_data():
    # Implement reading logic here
    # Parse request payload
    payload = request.json
    shard_id = payload.get('shard')
    stud_id_range = payload.get('Stud_id')
    
    # Read data for specified shard and range of Stud ids
    # Implement your logic here
    
    return jsonify({
        "data": data,  # Provide the actual data read from the database
        "status": "success"
    }), 200

# Endpoint to write data entries in a shard in a particular server container
@app.route('/write', methods=['POST'])
def write_data():
    # Implement writing logic here
    # Parse request payload
    payload = request.json
    shard_id = payload.get('shard')
    curr_idx = payload.get('curr_idx')
    data = payload.get('data')
    
    # Write data for specified shard
    # Implement your logic here
    
    return jsonify({
        "message": "Data entries added",
        "status": "success"
    }), 200

# Endpoint to update a particular data entry in a shard in a particular server container
@app.route('/update', methods=['PUT'])
def update_data():
    # Implement updating logic here
    # Parse request payload
    payload = request.json
    shard_id = payload.get('shard')
    stud_id = payload.get('Stud_id')
    data = payload.get('data')
    
    # Update data for specified shard and Stud id
    # Implement your logic here
    
    return jsonify({
        "message": "Data entry updated",
        "status": "success"
    }), 200

# Endpoint to delete a particular data entry in a shard in a particular server container
@app.route('/del', methods=['DELETE'])
def delete_data():
    # Implement deletion logic here
    # Parse request payload
    payload = request.json
    shard_id = payload.get('shard')
    stud_id = payload.get('Stud_id')
    
    # Delete data for specified shard and Stud id
    # Implement your logic here
    
    return jsonify({
        "message": "Data entry removed",
        "status": "success"
    }), 200

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
