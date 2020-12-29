import pymongo
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
import random
import math
from collections import deque
from scipy import signal
import urllib.request



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
fig, (ax,ax2) = plt.subplots(2,1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
plt.show(block = False)
plt.setp(line2,color = 'r')



PData = PlotData(500)
ax.set_ylim(-2.5,5)
ax2.set_ylim(-5,5)
start = time.time()


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

conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/', username='sam',password='mongo23392399',authSource='admin',authMechanism='SCRAM-SHA-256')
db = conn['admin']

firstlist = list(db.real_time.find({'time':{'$gte': (datetime.datetime.now() + server_time_diff - datetime.timedelta(seconds=1))}}))
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


time_rate_go_up = 0
past_t = 0
while 1:
    try:
        x_time = []
        y_value = []
        datalist = list(db.real_time.find({"_id":{"$gt": last_oid}}).max_time_ms(500).limit(200))
        if(datalist == []):
            continue
        for i in datalist:
            x_time.append(datetime.datetime.timestamp(i.get('time',datetime.datetime.now()+ server_time_diff)) - lasttime)
            y_value.append(i.get('value', 0))
        d_list = []
        filt_list = [1/int(11) for i in range(int(11))]
        y_filt = signal.lfilter(filt_list, 1, (y_value - np.mean(y_value))).tolist()
        #for i in  y_filt:
            #d_list.append(detect.thresholding_algo(i ))
            #d_list.append(np.gradient())
        g_list = []
        grad = np.gradient(y_filt)*5
        #print(len(y_filt),'   grad:', len(np.gradient(y_filt)) )
        for i in range(len(y_filt)):
            if grad[i] < 0.8:
                g_list.append(0)
                #print(grad[i])
                if time_rate_go_up != 0:
                    #print(x_time[i] - time_rate_go_up)
                    if(x_time[i] - time_rate_go_up > 0.06):
                        if(x_time[i] - past_t > 0.25 and x_time[i] - past_t < 1.1):
                            print(60/(x_time[i] - past_t))
                        past_t = x_time[i]
                    time_rate_go_up = 0 
            else:
                g_list.append(grad[i])
                if time_rate_go_up == 0:
                    time_rate_go_up = x_time[i]
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