import pymongo
import time
import numpy as np
import datetime
import collections
from scipy import signal

class real_time_peak_detection():
    def __init__(self, array, lag, threshold, influence):
        self.y = list(array)
        self.length = len(self.y)
        self.lag = lag
        self.threshold = threshold
        self.influence = influence
        self.signals = [0] * len(self.y)
        self.filteredY = np.array(self.y).tolist()
        self.avgFilter = [0] * len(self.y)
        self.stdFilter = [0] * len(self.y)
        self.avgFilter[self.lag - 1] = np.mean(self.y[0:self.lag]).tolist()
        self.stdFilter[self.lag - 1] = np.std(self.y[0:self.lag]).tolist()

    def thresholding_algo(self, new_value):
        self.y.append(new_value)
        i = len(self.y) - 1
        self.length = len(self.y)
        if i < self.lag:
            return 0
        elif i == self.lag:
            self.signals = [0] * len(self.y)
            self.filteredY = np.array(self.y).tolist()
            self.avgFilter = [0] * len(self.y)
            self.stdFilter = [0] * len(self.y)
            self.avgFilter[self.lag - 1] = np.mean(self.y[0:self.lag]).tolist()
            self.stdFilter[self.lag - 1] = np.std(self.y[0:self.lag]).tolist()
            return 0

        self.signals += [0]
        self.filteredY += [0]
        self.avgFilter += [0]
        self.stdFilter += [0]

        if abs(self.y[i] - self.avgFilter[i - 1]) > self.threshold * self.stdFilter[i - 1]:
            if self.y[i] > self.avgFilter[i - 1]:
                self.signals[i] = 1
            else:
                self.signals[i] = -1

            self.filteredY[i] = self.influence * self.y[i] + (1 - self.influence) * self.filteredY[i - 1]
            self.avgFilter[i] = np.mean(self.filteredY[(i - self.lag):i])
            self.stdFilter[i] = np.std(self.filteredY[(i - self.lag):i])
        else:
            self.signals[i] = 0
            self.filteredY[i] = self.y[i]
            self.avgFilter[i] = np.mean(self.filteredY[(i - self.lag):i])
            self.stdFilter[i] = np.std(self.filteredY[(i - self.lag):i])

        return self.signals[i]


conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/', username='sam',password='mongo23392399',authSource='admin',authMechanism='SCRAM-SHA-256')
db = conn['admin']

recent_reading = collections.deque([0, 0, 0, 0 , 0], maxlen=5)
ava_rate =  collections.deque([0, 0, 0], maxlen=3)
datalist = list(db.real_time.find({'time':{"$gte": datetime.datetime.now()-datetime.timedelta(seconds=5)}}).max_time_ms(500))
if(datalist == []):
    exit()
valuelist = []
for i in datalist:
    valuelist.append(i.get('value', 0))
    
detection = real_time_peak_detection(valuelist, 30, 3.5 , 0.3)
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
        valuelist -= np.mean(valuelist)

        for i in valuelist:
            print(detection.thresholding_algo(i))    
        
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            print(e)
            pass

print('done')