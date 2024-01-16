from flask import (Flask,request,jsonify,render_template,abort,url_for,json)
import sqlite3
import os
app = Flask(__name__,template_folder='.')

@app.route('/')
def index():
    return "Welcome to HELLO WORLD"


@app.route('/<name>')
def print_name(name):
    return 'Hi, {}'.format(name)

@app.route('/home/',methods = ['GET'])
def home():
    server_id = os.getenv('SERVER_ID', 'Unknown')
    response_json = {
        "message": f"Hello from server : {server_id}",
        "status" : "successful"
        }
    return jsonify(response_json),200

@app.route('/heartbeat',methods = ['GET'])
def heartbeats():
    return jsonify({"Response": " "}),200

    
if  __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
