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

@app.route('/')
def index():
    return "Welcome to ShardManager"


if  __name__ == '__main__':
    # app.run(debug=True,host='0.0.0.0')
    app.run(host='0.0.0.0',port=5000,debug=True)
