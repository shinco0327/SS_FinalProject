import pymongo
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
import random
import math
from collections import deque
from scipy import signal



class PlotData:
    def __init__(self, max_entries=30):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axis_y_fixed = deque(maxlen=max_entries)
    def add(self, x, y, y_fixed):
        self.axis_x.extend(x)
        self.axis_y.extend(y)
        self.axis_y_fixed.extend(y_fixed)


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




#initial
fig, (ax,ax2) = plt.subplots(2,1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
plt.show(block = False)
plt.setp(line2,color = 'r')



PData = PlotData(500)
ax.set_ylim(-2.5,5)
ax2.set_ylim(-5,5)
start = time.time()




conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/', username='sam',password='mongo23392399',authSource='admin',authMechanism='SCRAM-SHA-256')
db = conn['admin']

firstlist = list(db.real_time.find({'time':{'$gte': (datetime.datetime.now() - datetime.timedelta(seconds=1))}}))
last_oid = None
if(firstlist == [] or firstlist[-1].get('_id', None) == None):
    print("No data")
    exit()
else:
    last_oid = firstlist[-1].get('_id', None)


if(firstlist[0].get('time', None) == None):
    lasttime = time.time()
    exit()
else:
    lasttime = datetime.datetime.timestamp(firstlist[0].get('time', datetime.datetime.now()))

#print(lasttime)
init_value = []
for i in firstlist:
    init_value.append(i.get('value', 0))
time_th = abs(datetime.datetime.timestamp(firstlist[-1].get('time', None))-datetime.datetime.timestamp(firstlist[0].get('time', None)))
print((time_th/len(firstlist)))
init_filt = signal.lfilter([1/7, 1/7, 1/7,1/7, 1/7, 1/7,1/7], 1, (init_value - np.mean(init_value))).tolist()
detect = real_time_peak_detection(init_filt, 20, 3, 0.8)
time_rate_go_up = 0
while 1:
    try:
        x_time = []
        y_value = []
        datalist = list(db.real_time.find({"_id":{"$gt": last_oid}}).max_time_ms(500).limit(200))
        if(datalist == []):
            continue
        for i in datalist:
            x_time.append(datetime.datetime.timestamp(i.get('time',datetime.datetime.now())) - lasttime)
            y_value.append(i.get('value', 0))
        d_list = []
        y_filt = signal.lfilter([1/7, 1/7, 1/7,1/7, 1/7, 1/7,1/7], 1, (y_value - np.mean(y_value))).tolist()
        #for i in  y_filt:
            #d_list.append(detect.thresholding_algo(i ))
            #d_list.append(np.gradient())
        g_list = []
        for i in np.gradient(y_filt)*5:
            if i < 1:
                g_list.append(0)
                #if time_rate_go_up != 0:
                #    print(time.time() - time_rate_go_up)
                #    time_rate_go_up = 0 
            else:
                g_list.append(i)
                #if time_rate_go_up == 0:
                #    time_rate_go_up = time.time()
        PData.add(x_time,  y_filt, g_list)
        
        #print(x)
        #print(z)
        
        ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
        ax2.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
        
        line.set_xdata(PData.axis_x)
        line.set_ydata(PData.axis_y)
        line2.set_xdata(PData.axis_x)
        line2.set_ydata(PData.axis_y_fixed)
        fig.canvas.draw()
        fig.canvas.flush_events()

        
        
        
        
        
        time.sleep(0.5)
        
        #calculate here!!!!!!!!!!!!!!!!!!!!!!!
        if(datalist !=[]):
            last_oid = datalist[-1].get("_id", None)
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            print(e)