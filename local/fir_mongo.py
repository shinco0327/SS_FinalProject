import pymongo
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
import time, random
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




#initial
fig, (ax,ax2,ax3) = plt.subplots(3,1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
line3, = ax3.plot(np.random.randn(100))
plt.show(block = False)
plt.setp(line2,color = 'r')
plt.setp(line3,color = 'b')


PData = PlotData(500)
ax.set_ylim(-5,1000)
ax2.set_ylim(-5,5)
ax3.set_ylim(0,1)
start = time.time()




recentReading = [0, 0, 0, 0, 0, 0, 0, 0]
HeartrateBuff = deque([0, 0, 0, 0, 0, 0, 0, 0], maxlen=8)
ava_rate = deque([0, 0, 0], maxlen=3)
lastRead = 0
lasttime = time.time()
Recenttrend = 0
readingsIndex = 0


conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/')
db = conn['admin']

firstlist = list(db.real_time.find({'time':{'$gte': (datetime.datetime.now() - datetime.timedelta(seconds=1))}}).limit(1))
last_oid = None
if(firstlist == [] or firstlist[0].get('_id', None) == None):
    print("No data")
    exit()
else:
    last_oid = firstlist[0].get('_id', None)


if(firstlist[0].get('time', None) == None):
    lasttime = time.time()
    exit()
else:
    lasttime = datetime.datetime.timestamp(firstlist[0].get('time', datetime.datetime.now()))

print(lasttime)



while 1:
    try:
        x_time = []
        y_value = []
        datalist = list(db.real_time.find({"_id":{"$gt": last_oid}}).max_time_ms(500).limit(500))
        if(datalist == []):
            continue
        for i in datalist:
            x_time.append(datetime.datetime.timestamp(i.get('time',datetime.datetime.now())) - lasttime)
            y_value.append(i.get('value', 0))
        #calculate here!!!!!!!!!!!!!!!!!!!!!!!
        y = signal.lfilter([1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11,1/11, 1/11], 1, (y_value-np.mean(y_value)))
        PData.add(x_time, y_value, y)
        f =np.arange(0, 125, 1)
        fs = 1/((x_time[len(x_time)-1]-x_time[0])/len(x_time))
        z = [] 
        t = np.arange(0, len(y_value)/fs, 1/fs) 
        for i in range(0,125):
            x = np.cos(2*np.pi*i*t)
            y = signal.lfilter([1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11,1/11, 1/11], 1, x)
            z.append(max(y))   

        #print(x)
        #print(z)
        
        ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
        ax2.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
        
        line.set_xdata(PData.axis_x)
        line.set_ydata(PData.axis_y)
        line2.set_xdata(PData.axis_x)
        line2.set_ydata(PData.axis_y_fixed)
        line3.set_xdata(f)
        line3.set_ydata(z)
        fig.canvas.draw()
        fig.canvas.flush_events()

        
        
        
        
        
        
        
        #calculate here!!!!!!!!!!!!!!!!!!!!!!!
        if(datalist !=[]):
            last_oid = datalist[-1].get("_id", None)
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            print(e)