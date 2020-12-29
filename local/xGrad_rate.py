import pymongo
import time
import numpy as np
import datetime
import collections
from scipy import signal
import urllib.request


conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/', username='sam',password='mongo23392399',authSource='admin',authMechanism='SCRAM-SHA-256')
db = conn['admin']

while 1:
    try:
        response=urllib.request.urlopen("http://128.199.118.43:5000/systemtime", timeout=0.5) 
        b=response.read()
        remote_time = datetime.datetime.strptime(str(b,encoding="utf-8"), '%Y-%m-%d %H:%M:%S')
        local_time = datetime.datetime.fromtimestamp(time.time())
        server_time_diff = remote_time - local_time
        break
    except Exception as e:
        print(e)
        print("Can't sync time")
print(server_time_diff)


recent_reading = collections.deque([0, 0, 0, 0 , 0], maxlen=5)
peak_up  = 0
past_t = 0
while 1:
    try:
        print('.')
        datalist = list(db.real_time.find({'time':{"$gte": datetime.datetime.now()+ server_time_diff-datetime.timedelta(seconds=5)}}).max_time_ms(500))
        print('..')
        #datalist = list(db.real_time.find({}).sort('_id', -1).limit(400))
        if datalist == []:
            continue
        #datalist.reverse()
        valuelist = []
        timelist = []
        datalist.reverse()
        for i in datalist:
            valuelist.append(i.get('value', 0))
            timelist.append(datetime.datetime.timestamp(i.get('time', None)))
        #for i in range(len(timelist)):
        #    print(i, ' a: ', timelist[i])
        filt_list = [1/int(11) for i in range(int(11))]
        valuelist = signal.lfilter(filt_list, 1, (valuelist - np.mean(valuelist))).tolist()
        grad_list = np.gradient(valuelist)*5
        for i in range(len(valuelist)):
            #print(grad_list)
            if grad_list[i] < 0.3:
                if peak_up != 0:
                    #print(x_time[i] - time_rate_go_up)
                    if(timelist[i] - peak_up > 0.06):
                        if(timelist[i] - past_t > 0.25 and timelist[i] - past_t < 1.1):
                            print(60/(timelist[i] - past_t))
                        past_t =timelist[i]
                    past_read = timelist[i]
                    peak_up = 0

            else:
                if peak_up == 0:
                    peak_up = timelist[i]
            
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            print(e)
            pass

print('done')