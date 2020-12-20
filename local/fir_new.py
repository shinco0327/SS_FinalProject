import matplotlib.pyplot as plt
import numpy as np
import time
import time, random
import math
import serial
from collections import deque
from scipy import signal
from scipy.signal import medfilt
from scipy.ndimage.filters import convolve

#append [1, 2, 3] append(4) [1, 2, ,3, 4] append([87, 87]) [1, 2, 3, [87, 87]]
#extend [ 1, 2, 3] extend([87,87]) [1, 2, 3, 87, 87]

#Display loading 
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
ax.set_ylim(-5,5)
ax2.set_ylim(-5,5)
ax3.set_ylim(0,1)


# plot parameters
print ('plotting data...')
# open serial port
strPort='com8'
ser = serial.Serial(strPort, 115200)
ser.flush()

start = time.time()
total = 0
count = 0
old_fs = 0

while True:
    try:
        x_time = []
        y_value = []
        for ii in range(10):

            try:
                data = float(ser.readline())
                x_time.append(time.time() - start)
                y_value.append(data)
                total += data
                count += 1
                
                
            except:
                pass
        ava = total / count
        y_pretty = y_value - np.full(len(y_value), ava)
        fs = 1/((x_time[len(x_time)-1]-x_time[0])/len(x_time))
        fs = (fs+old_fs)/2
        old_fs = fs
        print(fs)
        sos = signal.butter(6, 3.8, 'lowpass', fs=(fs), output='sos')
        y = signal.sosfilt(sos, y_pretty)
        y *= np.exp(8.5)
        #y1 = signal.lfilter([1/9, 1/9, 1/9,1/9, 1/9, 1/9,1/9, 1/9, 1/9], 1, y)
        #y = signal.lfilter([1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11,1/11, 1/11], 1, y_pretty)
        if count > 9:
            total = 0
            count = 0
        PData.add(x_time, y_pretty, y)
        f =np.arange(0, 125, 1)
        z = [] 
        t = np.arange(0, len(y_value)/fs, 1/fs) 
        for i in range(0,125):
            x = np.cos(2*np.pi*i*t)
            y = signal.lfilter([1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11,1/11, 1/11], 1, x)
            z.append(max(y))   

        
        
        
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

        
        
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            pass