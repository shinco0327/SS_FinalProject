import pymongo
import time
from datetime import datetime


conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/')


db = conn['admin']
real_time = db.real_time
while 1:
    try:
        real_time.insert_one({'value':512 ,'time':datetime.now()})
        db.device.update_many({},{'$set':{'alive': True}})
        time.sleep(1)
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
             pass

print('done')