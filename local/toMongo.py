import pymongo
import time
from datetime import datetime
import serial
import urllib.request
import threading

def push_mongo():
    global update_dict
    while 1:
        try:
            if update_dict != []:
                db.real_time.insert_many(update_dict)
                update_dict = []
            time.sleep(0.01)
            db.device.update_many({},{'$set':{'alive': True}})
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            else:
                pass

strPort='com4'
ser = serial.Serial(strPort, 115200)
ser.flush()

while 1:
    try:
        response=urllib.request.urlopen("http://128.199.118.43:5000/systemtime", timeout=0.5) 
        b=response.read()
        remote_time = datetime.strptime(str(b,encoding="utf-8"), '%Y-%m-%d %H:%M:%S')
        local_time = datetime.fromtimestamp(time.time())
        server_time_diff = remote_time - local_time
        break
    except Exception as e:
        print(e)
        print("Can't sync time")

conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/')

update_dict = []
db = conn['admin']

thread_push_mongo = threading.Thread(target=push_mongo)
thread_push_mongo.daemon = True
thread_push_mongo.start()

while 1:
    try:
        data = float(ser.readline())
        update_dict.append({'value':data ,'time':datetime.now()})
        print(data)
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
             pass

print('done')