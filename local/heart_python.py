import matplotlib.pyplot as plt
import numpy as np
import time
import time, random
import math
import serial
from collections import deque

#append [1, 2, 3] append(4) [1, 2, ,3, 4] append([87, 87]) [1, 2, 3, [87, 87]]
#extend [ 1, 2, 3] extend([87,87]) [1, 2, 3, 87, 87]

#Display loading 
class PlotData:
    def __init__(self, max_entries=30):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axis_yfft = deque(maxlen=max_entries)
    def add(self, x, y):
        self.axis_x.extend(x)
        self.axis_y.extend(y)
    def add_fft(self, value):
        self.axis_yfft.extend(value)

#initial
fig, (ax,ax2) = plt.subplots(2,1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
plt.show(block = False)
plt.setp(line2,color = 'r')
plt.figure(2, figsize=(10,5), dpi=200)



PData = PlotData(500)
ax.set_ylim(0,500)
#ax2.set_ylim(-5,5)



# plot parameters
print ('plotting data...')
# open serial port
strPort='com4'
ser = serial.Serial(strPort, 115200)
ser.flush()

start = time.time()

while True:
    try:
        x_time = []
        y_value = []
        for ii in range(10):

            try:
                data = float(ser.readline())
                x_time.append(time.time() - start)
                y_value.append(data)
                
                
            except:
                pass
        #print(x_time)
        try:
            #print(1/((x_time[9]-x_time[0])/10))
            PData.add_fft(y_value - np.mean(y_value))
            w_hat = np.arange(0, 2*(x_time[9]-x_time[0])*np.pi, np.pi*2/(1/((x_time[9]-x_time[0])/10)))
        
            print(w_hat)
            
            xf = np.fft.fft(y_value)
            print(len(w_hat))
        except:
            pass
        #fft tp signal
        PData.add(x_time, y_value)
        #y_value len = 10 list, list -- fft

        
        

        
        ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
        #ax2.set_xlim(PData.axis_x, PData.axis_x[0]+5)
        line.set_xdata(PData.axis_x)
        line.set_ydata(PData.axis_y)
        line2.set_xdata(w_hat)
        line2.set_ydata(xf)
        fig.canvas.draw()
        fig.canvas.flush_events()

        plt.figure(2)
        plt.plot(w_hat, xf)
        
    except:
        pass