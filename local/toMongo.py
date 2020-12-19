import pymongo
import time
from datetime import datetime


conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/')


database = conn['admin']
real_time = database['real_time']
real_time.insert_one({'value':512 ,'time':datetime.now()})
time.sleep(1)

print('done')