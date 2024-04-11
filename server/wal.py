import os
import json
import shutil
from datetime import datetime


class WriteAheadLog:
    def __init__(self, logFileName):
        # self.log_dir = log_dir
        # os.makedirs(log_dir, exist_ok=True)
        self.log_file =  f"{logFileName}.log"
        self.temp_log_file = f"{logFileName}_temp.log"
        with open(self.log_file,'w'):pass
        with open(self.temp_log_file,'w'):pass

    def append(self, endpoint,payload):
        with open(self.temp_log_file, 'a') as f:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data = {"Time" : now, "endpoint": endpoint, "payload": payload}
            f.write(json.dumps(data) + '\n')

    def commit(self,endpoint,payload):
        with open(self.log_file, 'a') as f:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data = {"Time" : now, "endpoint": endpoint, "payload": payload}
            f.write(json.dumps(data) + '\n')

    def flush(self):
        shutil.move(self.temp_log_file, self.log_file)

    def read(self):
        with open(self.log_file, 'r') as f:
            for line in f:
                yield json.loads(line)

    def clear(self):
        os.remove(self.log_file)

