
import time
from datetime import datetime
import serial
import collections
import numpy as np




strPort='com8'
ser = serial.Serial(strPort, 115200)
ser.flush()

recentReading = [0, 0, 0, 0, 0, 0, 0, 0]
HeartrateBuff = collections.deque([0, 0, 0, 0, 0, 0, 0, 0], maxlen=8)
ava_rate = collections.deque([0, 0, 0], maxlen=3)
lastRead = 0
lastBeattime = time.time()
Recenttrend = 0
readingsIndex = 0

while 1:
    try:
        newRead = int(ser.readline())
        delta = newRead - lastRead
        lastRead = newRead

        #Recenttrend = Recenttrend - np.mean(recentReading) + delta
        Recenttrend = Recenttrend - recentReading[readingsIndex] + delta
        recentReading[readingsIndex] = delta
        readingsIndex = (readingsIndex + 1) % len(recentReading)
        #print(Recenttrend)
    
        if(Recenttrend >= 1.95 and time.time()-lastBeattime >= 0.150):
            #print(60/(time.time()-lastBeattime))
            currenHearttrate = 60/(time.time()-lastBeattime)
            HeartrateBuff.append(currenHearttrate)
            avg = np.average(HeartrateBuff)
            lastBeattime = time.time()
            if(currenHearttrate < 200 and currenHearttrate > 50):
                ava_rate.append(currenHearttrate)
                print("BEAT: ", "%.2f" % np.average(ava_rate))
                
            
        
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            print(e)
            pass

print('done')