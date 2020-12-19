import pymongo
import time
from datetime import datetime
import serial

strPort='com3'
ser = serial.Serial(strPort, 115200)
ser.flush()

conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/')


db = conn['admin']
real_time = db.real_time
while 1:
    try:
        data = float(ser.readline())
        print(data)
        real_time.insert_one({'value':data ,'time':datetime.now()})
        db.device.update_many({},{'$set':{'alive': True}})
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
             pass

print('done')