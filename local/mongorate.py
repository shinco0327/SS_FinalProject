import pymongo
import datetime
import time
import numpy as np
import collections

recentReading = [0, 0, 0, 0, 0, 0, 0, 0]
HeartrateBuff = collections.deque([0, 0, 0, 0, 0, 0, 0, 0], maxlen=8)
ava_rate = collections.deque([0, 0, 0], maxlen=3)
lastRead = 0
lastBeattime = time.time()
Recenttrend = 0
readingsIndex = 0


conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/')
db = conn['admin']

firstlist = list(db.real_time.find({'time':{'$gte': (datetime.datetime.now() - datetime.timedelta(seconds=1.5))}}).limit(1))
last_oid = None
if(firstlist == [] or firstlist[0].get('_id', None) == None):
    print("No data")
else:
    last_oid = firstlist[0].get('_id', None)
print(last_oid)     

if(firstlist[0].get('time', None) == None):
    lastBeattime = time.time()
else:
    lastBeattime = datetime.datetime.timestamp(firstlist[0].get('time', None))

print(lastBeattime)



while 1:
    try:
        datalist = list(db.real_time.find({"_id":{"$gt": last_oid}}).max_time_ms(300).limit(50))
        for data in datalist:
            newRead = data.get('value', 0)
            #print(newRead)
            delta = newRead - lastRead
            lastRead = newRead

            #Recenttrend = Recenttrend - np.mean(recentReading) + delta
            Recenttrend = Recenttrend - recentReading[readingsIndex] + delta
            recentReading[readingsIndex] = delta
            readingsIndex = (readingsIndex + 1) % len(recentReading)
            #print(Recenttrend)
        
            if(Recenttrend >= 1.95 and datetime.datetime.timestamp(data.get('time', datetime.datetime.now()))-lastBeattime >= 0.150):
                #print(60/(time.time()-lastBeattime))
                currenHearttrate = 60/(datetime.datetime.timestamp(data.get('time', datetime.datetime.now()))-lastBeattime)
                HeartrateBuff.append(currenHearttrate)
                avg = np.average(HeartrateBuff)
                lastBeattime = datetime.datetime.timestamp(data.get('time', datetime.datetime.now()))
                if(currenHearttrate < 200 and currenHearttrate > 50):
                    ava_rate.append(currenHearttrate)
                    print("BEAT: ", "%.2f" % np.average(ava_rate))
        if(datalist != []):
            last_oid = datalist[-1].get("_id", None)
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            print(e)