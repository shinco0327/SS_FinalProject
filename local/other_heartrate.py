import pymongo
import time
import numpy as np
import datetime
import collections
from scipy import signal


conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/', username='sam',password='mongo23392399',authSource='admin',authMechanism='SCRAM-SHA-256')
db = conn['admin']

recent_reading = collections.deque([0, 0, 0, 0 , 0], maxlen=5)
ava_rate =  collections.deque([0, 0, 0], maxlen=3)
while 1:
    try:
        datalist = list(db.real_time.find({'time':{"$gte": datetime.datetime.now()-datetime.timedelta(seconds=5)}}).max_time_ms(500))
        #datalist = list(db.real_time.find({}).sort('_id', -1).limit(400))
        if datalist == []:
            continue
        valuelist = []
        timelist = []
        for i in datalist:
            valuelist.append(i.get('value', 0))
            timelist.append(datetime.datetime.timestamp(i.get('time', None)))
        fs = 1/(abs(timelist[-1] - timelist[0])/len(timelist))
        f = np.arange(0, fs, fs/len(timelist))
        #valuelist = signal.lfilter([1/3, 1/3, 1/3], 1, (valuelist - np.mean(valuelist)))
        T = (abs(timelist[-1] - timelist[0])/len(timelist))
        sos = signal.butter(10, 10, 'lp', fs=fs, output='sos')
        valuelist = signal.sosfilt(sos, valuelist)
        #print(fs)
        Period = abs(timelist[-1] - timelist[0])/len(timelist)
        #print(1.1/Period)
        #print(signal.find_peaks(valuelist, height=0.5, threshold=1.1))
        Fs = np.arange(0, 100, 1)
        t = np.arange(0, 1, 1/100)
        for i in Fs:
            print(i)
            x = np.cos(2*np.pi*i*t)
            print(x)
        #print(np.max(np.gradient(valuelist)))
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            print(e)
            pass

print('done')