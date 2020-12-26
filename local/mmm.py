from scipy import signal
from collections import deque
import serial
import math
import random
import time
import numpy as np
import matplotlib.pyplot as plt


# [] append [[1,2,3], [4,5,6,7],[],[],[],[],[],[],[],[],[],[]] [1,2,3] [4,5,6,7]
# [] extend [1,2,3,4,5,6,7] [1,2,3] [4,5,6,7]
# Display loading


class PlotData:
    def __init__(self, max_entries=30):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_x_freq = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axis_yff = deque(maxlen=max_entries)
        self.axis_yff2 = []

    def add(self, x, x_freq, y, yff):
        self.axis_x.extend(x)
        self.axis_x_freq.extend(x_freq)
        self.axis_y.extend(y)
        self.axis_yff.extend(yff)


# initial
fig, (ax, ax2, ax3) = plt.subplots(3, 1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
line3, = ax3.plot(np.random.randn(100))
plt.show(block=False)
plt.setp(line2, color='r')
plt.setp(line3, color='b')


PData = PlotData(1000)
ax.set_ylim(0, 500)
ax2.set_ylim(-5, 5)


# plot parameters
print('plotting data...')
# open serial port
strPort = 'com3'
ser = serial.Serial(strPort, 115200)
ser.flush()

start = time.time()

while True:

    y_value = []
    datafilter_max = []
    time_value = []

    for ii in range(1000):

        try:
            data = float(ser.readline())
            time_value.append(time.time() - start)
            y_value.append(data)

        except:
            pass
    datafilter = signal.lfilter([1/13, 1/13, 1/13, 1/13, 1/13, 1/13, 1/13,
                                 1/13, 1/13, 1/13, 1/13, 1/13, 1/13], 1, (y_value - np.mean(y_value)))
    datafilter_max.append(np.max(datafilter))
    datafft = np.fft.fft(y_value - np.mean(y_value))

    try:
        fs = 1/(abs(time_value[-1]-time_value[0])/len(time_value))
        t = np.arange(0, datafft.size/fs, 1/fs)
        f = t*fs/(datafft.size/fs)
        ff2 = abs(datafft)

        xf = np.argmax(ff2)
        ax3.set_ylim(0, len(f/2))
        PData.add(time_value, f, y_value, datafilter)

        ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
        ax2.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
        ax3.set_xlim(0, f[-1])

        line.set_xdata(PData.axis_x)
        line.set_ydata(PData.axis_y)
        line2.set_xdata(PData.axis_x)
        line2.set_ydata(PData.axis_yff)
        xxx = 0
        yyy = 0
        for i in f:
            if (i < 0.7):
                xxx += 1
            if(i > 3):
                break
            yyy += 1
        line3.set_xdata(f)
        line3.set_ydata(ff2)
        fig.canvas.draw()
        fig.canvas.flush_events()
    except:
        continue
        pass
    print(fs)
    print(f[np.argmax(ff2[:int(len(ff2)/2)])]*60)