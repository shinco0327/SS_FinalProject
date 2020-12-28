from flask import Flask, render_template, request, redirect, g, session, url_for, flash, jsonify, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymongo
import datetime
import time
import json
import threading
from bson import ObjectId
import numpy as np
import collections
#For signal processing
from scipy import signal
#End of signal processing

# 初始化 Flask 類別成為 instance
app = Flask(__name__)
#conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/')
conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/', username='sam',password='mongo23392399',authSource='admin',authMechanism='SCRAM-SHA-256')
print(conn)
#-----------------------------------------------------------------------------------
app.secret_key= b'%\xab\x9ei\xd6b\x8a\xab\xcd\xb1\xda\x87\x0e\xbd\xae\xb6_\xfd\x98\xf8v\xf2\x8dZ'
login_manger=LoginManager()
login_manger.session_protection='strong'
login_manger.init_app(app)

class User(UserMixin):
    pass

#For ObjectID to json
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

#-------------------------------------------------------------------------------
def check_user():
    user = current_user.get_id()
    try:
        user = user.split('_')
    except:
        logout()
        return None,None
    db = conn[user[0]]
    return user,db
#-------------------------------------------------------------------------------
#對照是否有此用戶
def user_list(user):
    db =conn[user]
    for user_find in db.users.find({'username': user}):
        return user_find
#-------------------------------------------------------------------------------
#如果用戶存在則構建一新用戶類對象，並使用user_id當id
@login_manger.user_loader
def load_user(user):
    user_info =user_list(user)
    if user_info is not None:
        curr_user = User()
        curr_user.id = user_info['username']
        
        return curr_user
#-------------------------------------------------------------------------------
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=60)
    session.modified = True
    g.user = current_user 

# 路由和處理函式配對
@app.route('/')
def index():
    user,db = check_user()
    if(db == None):
        return redirect('/login') 
    return redirect('/dashboard')
#-------------------------------------------------------------------------------
@app.route('/login')
def login():  
    flash('Please login') 
    print(request.args.get("error", default=False, type=bool))
    if request.args.get("error", default=False, type=bool) == True:
        print("Wrong password")
        flash('Wrong infornation!!')
    return render_template('login.html') 
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#loginauth
@app.route('/loginauth',methods=['GET','POST'])
def loginauth():
    if request.method == 'POST':      
        username = request.form.get('inputUsername',type=str)
        if(username!=''):
            user_info = user_list(username)
            print(user_info)
            #驗證帳號
            if user_info is not None and request.form['inputPassword'] == user_info['password']:
                curr_user = User()
                curr_user.id = user_info['username']
                #通過flask-login的login_user方法登入用戶
                login_user(curr_user)
                user,db = check_user()
                return redirect('/dashboard')
                
        flash('Wrong infornation!!')
        return redirect(url_for('login', error=True))
#-------------------------------------------------------------------------------
#logout
@app.route('/logout')
def logout():
    user = current_user
    user.authenticated = False
    session.clear()
    logout_user()
    #return redirect('login.html') 
    return redirect(url_for('login'))

#-------------------------------------------------------------------------------
@app.route('/getfiltertype')
def getfiltertype():
    list1 = ['3-pt', '5-pt', '7-pt','9-pt', '11-pt', '15-pt']
    return jsonify(listfilter = list1)
#-------------------------------------------------------------------------------
#get tstamp
@app.route('/gettstamp')
def gettstamp(): 
    return jsonify(timestamp=time.time())
#-------------------------------------------------------------------------------
@app.route('/checkalive')
def checkalive():
    global alive
    return jsonify(alive=alive)
#-------------------------------------------------------------------------------
@app.route('/systemtime')
def systemtime():
    return Response(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mimetype='text')
#-------------------------------------------------------------------------------
#return  raw data 
@app.route('/getgraphdata', methods=['GET', 'POST'])
def getgraphdata():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    count = request.args.get("count", type=int)
    graphmode = request.args.get('graphmode', type=str)
    if count == None or graphmode == None or graphmode == '':
        return jsonify(start_oid=None, count=0, value=[], time=[])
    #print(count)
    print(graphmode)
    if count == 0:  #Draw New Chart
        datalist = list(db.real_time.find({'time':{'$gte': (datetime.datetime.now() - datetime.timedelta(seconds=1))}}))
        print(datalist)
        if datalist == []:
            return jsonify(start_oid=None, count=0, value=[], time=[])
        json_start_oid = JSONEncoder().encode(datalist[0].get('_id', ''))
        valuelist = []
        timelist = []
        for i in datalist:
            if i.get('value', None) != None:
                valuelist.append(i.get('value', None))
                timelist.append(datetime.datetime.timestamp(i.get('time', None)))
        fix_valuelist = []
        if(graphmode == "RAW"):
            fix_valuelist = valuelist
        else:
            fix_valuelist = (valuelist - np.mean(valuelist)).tolist()
            if(graphmode == "DCF"):
                pass
            elif(graphmode[0:3] == "LPF"):
                if(graphmode == "LPFButter"):
                    fs = 1/(abs(timelist[0] - timelist[-1])/len(valuelist))
                    print(timelist)
                    sos = signal.butter(10, 10, 'lp', fs=fs, output='sos')
                    fix_valuelist = signal.sosfilt(sos, fix_valuelist).tolist()
                elif(graphmode[0:5] == "LPFpt"):
                    print("It's ", graphmode[5:])
                    filt_list = [1/int(graphmode[5:]) for i in range(int(graphmode[5:]))]
                    fix_valuelist = signal.lfilter(filt_list, 1, fix_valuelist).tolist()

        return jsonify(start_oid=json_start_oid, count=len(valuelist), value=fix_valuelist, time=timelist)
    elif count > 0:   #Update chart
        str_start_oid = request.args.get('start_oid', type=str)
        str1_start_oid =  str_start_oid.replace("\"", "")
        start_oid = ObjectId(str1_start_oid)
        json_start_oid = JSONEncoder().encode(start_oid)
        
        valuelist = []
        datalist = list(db.real_time.find({"_id":{"$gte": start_oid}}).skip(count).max_time_ms(300).limit(100))
        if datalist == []:
            return jsonify(start_oid=json_start_oid, count=count, value=[], time=[])
        valuelist = []
        timelist = []
        for i in datalist:
            if i.get('value', None) != None:
                valuelist.append(i.get('value', None))
                timelist.append(datetime.datetime.timestamp(i.get('time', None)))
        fix_valuelist = []
        if(graphmode == "RAW"):
            fix_valuelist = valuelist
        else:
            fix_valuelist = (valuelist - np.mean(valuelist))
            if(graphmode == "DCF"):
                fix_valuelist = fix_valuelist.tolist()
            elif(graphmode[0:3] == "LPF"):
                if(graphmode == "LPFButter"):
                    fs = 1/(abs(timelist[0] - timelist[-1])/len(valuelist))
                    sos = signal.butter(10, 10, 'lp', fs=fs, output='sos')
                    fix_valuelist = signal.sosfilt(sos, fix_valuelist).tolist()
                elif(graphmode[0:5] == "LPFpt"):
                    print("It's ", graphmode[5:])
                    filt_list = [1/int(graphmode[5:]) for i in range(int(graphmode[5:]))]
                    fix_valuelist = signal.lfilter(filt_list, 1, fix_valuelist).tolist()
        return jsonify(start_oid=json_start_oid, count=len(valuelist)+count, value=fix_valuelist, time=timelist)

    return jsonify(start_oid=None, count=0, value=[], time=[])
#-------------------------------------------------------------------------------
#return  raw data 
@app.route('/getspectrum', methods=['GET', 'POST'])
def getspectrum():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    graphmode = request.args.get('graphmode', type=str)
    if graphmode == None or graphmode == '':
        return jsonify(value=[], freq=[])
    datalist = list(db.real_time.find({'time':{"$gte": datetime.datetime.now()-datetime.timedelta(seconds=5)}}).max_time_ms(500))
    if datalist == []:
        return jsonify(value=[], freq=[])
    valuelist = []
    freqlist = []
    timelist = []
    fftlist = []
    for i in datalist:
        valuelist.append(i.get('value', 0))
        timelist.append(datetime.datetime.timestamp(i.get('time', None)))
    fs = 1/(abs(timelist[-1] - timelist[0])/len(timelist))
    freqlist = np.arange(0, fs, fs/len(timelist)).tolist()
    if(len(freqlist) > len(valuelist)):
        del freqlist[-1]
    elif(len(valuelist) > len(freqlist)):
        del valuelist
    freqlist = [ '%.2f' % elem for elem in freqlist ]
    if(graphmode == "RAW"):
        fftlist = np.fft.fft(valuelist)
    elif(graphmode == "DCF"):
        fftlist = np.fft.fft(valuelist - np.mean(valuelist))
    elif(graphmode[0:3] == "LPF"):
        if(graphmode == "LPFButter"):
            sos = signal.butter(10, 10, 'lp', fs=fs, output='sos')
            fix_valuelist = signal.sosfilt(sos, valuelist - np.mean(valuelist))
            fftlist = np.fft.fft(fix_valuelist)
        elif(graphmode[0:5] == "LPFpt"):
            filt_list = [1/int(graphmode[5:]) for i in range(int(graphmode[5:]))]
            fix_valuelist = signal.lfilter(filt_list, 1, valuelist - np.mean(valuelist))
            fftlist = np.fft.fft(fix_valuelist)
    fftlist = abs(fftlist).tolist()
    
    return jsonify(value= fftlist[:int(len(fftlist)/2)], freq= freqlist[:int(len(freqlist)/2)])
    #-------------------------------------------------------------------------------
#return  raw data 
@app.route('/gethistorygraph', methods=['GET', 'POST'])
def gethistorygraph():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    count = request.args.get("count", type=int)
    str_record_oid = request.args.get('record_oid', type=str)
    str1_record_oid =  str_record_oid.replace("\"", "")
    record_oid = ObjectId(str1_record_oid)
    json_record_oid = JSONEncoder().encode(record_oid)
    graphmode = request.args.get('graphmode', type=str)
    comparemode = request.args.get('comparemode', 'OFF',type=str)
    interval = request.args.get('interval', 0.5,type=float)
    if count == None or graphmode == None:
        return jsonify(record_oid=None, count=0, value=[], time=[])
    #print(count)
    #print(graphmode)
    first_elem = list(db.history_realtime.find({'record_oid': record_oid}).skip(count).sort('_id', 1).limit(1))
    if(first_elem ==  []):
        return jsonify(count=count, value=[], time=[])
    start_time = first_elem[0]['time']
    datalist = list(db.history_realtime.find({'time':{'$gte': start_time,'$lt': start_time+datetime.timedelta(seconds=interval)}}))
    if(datalist == []):
        return jsonify(count=count, value=[], time=[])
    valuelist = []
    timelist = []
    for i in datalist:
        if i.get('value', None) != None:
            valuelist.append(i.get('value', None))
            timelist.append(datetime.datetime.timestamp(i.get('time', None)))
    fix_valuelist = []
    comparelist = []
    if(graphmode == "RAW"):
        fix_valuelist = valuelist
    else:
        fix_valuelist = (valuelist - np.mean(valuelist))
        if(graphmode == "DCF"):
            fix_valuelist = fix_valuelist.tolist()
        elif(graphmode[0:3] == "LPF"):
            if(graphmode == "LPFButter"):
                fs = 1/(abs(timelist[0] - timelist[-1])/len(valuelist))
                sos = signal.butter(10, 10, 'lp', fs=fs, output='sos')
                fix_valuelist = signal.sosfilt(sos, fix_valuelist).tolist()
            elif(graphmode[0:5] == "LPFpt"):
                filt_list = [1/int(graphmode[5:]) for i in range(int(graphmode[5:]))]
                fix_valuelist = signal.lfilter(filt_list, 1, fix_valuelist).tolist()
    if(comparemode == 'OFF'):
        return jsonify(count=count+len(valuelist), value=fix_valuelist, time=timelist)
    elif(comparemode == "RAW"):
        comparelist = valuelist
    else:
        comparelist = (valuelist - np.mean(valuelist))
        if(comparemode == "DCF"):
            comparelist = comparelist.tolist()
        elif(comparemode[0:3] == "LPF"):
            if(comparemode == "LPFButter"):
                fs = 1/(abs(timelist[0] - timelist[-1])/len(valuelist))
                sos = signal.butter(10, 10, 'lp', fs=fs, output='sos')
                comparelist = signal.sosfilt(sos, comparelist).tolist()
            elif(comparemode[0:5] == "LPFpt"):
                filt_list = [1/int(comparemode[5:]) for i in range(int(comparemode[5:]))]
                comparelist = signal.lfilter(filt_list, 1, comparelist).tolist()
    return jsonify(count=count+len(valuelist), value=fix_valuelist, comparevalue=comparelist, time=timelist)
#-------------------------------------------------------------------------------
@app.route('/savechartrecord')
def savechartrecord():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    try:    
        str_reference_oid = request.args.get('reference_oid', type=str)
        reference_oid = ObjectId(str_reference_oid.replace("\"", ""))
        reference_end = request.args.get("reference_end", type=int)
        start_position = request.args.get('start_position', type=int)
        record_name = request.args.get('record_name', type=str)
        subject_name = request.args.get('subject_name', type=str)
        remarks = request.args.get('remarks', type=str)
        heartrate = request.args.get("heartrate", 0,type=float)
        if(record_name == '' or record_name == None):
            return jsonify(successful=False)
        datalist = list(db.real_time.find({"_id":{"$gte": reference_oid}}).skip(start_position).limit(reference_end+1-start_position))
        #print(datalist)
        if(heartrate > 50):
            _id = db.history_overview.insert_one({'record_name': record_name, 'subject_name':subject_name, 'remarks': remarks,'count': len(datalist), 'time': datalist[0].get('time', datetime.datetime.now()),
            'heartrate':heartrate})
        else:
            _id = db.history_overview.insert_one({'record_name': record_name, 'subject_name':subject_name, 'remarks': remarks,'count': len(datalist), 'time': datalist[0].get('time', datetime.datetime.now())})
        for i in datalist:
            i['record_oid'] = _id.inserted_id
        db.history_realtime.insert_many(datalist)
        return jsonify(successful=True)
    except Exception as e:
        print('savehistory error: ',e)
        return jsonify(successful=False)
#-------------------------------------------------------------------------------   
#Get list of history record
@app.route('/gethistorylist')
def gethistorylist():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    historylist = list(db.history_overview.find({}))
    for i in historylist:
        i['_id'] = JSONEncoder().encode(i.get('_id', None))
        i['time'] = i.get('time', datetime.datetime.now()).strftime("%Y/%m/%d, %H:%M:%S")
    return jsonify(historylist=historylist)
#-------------------------------------------------------------------------------   
@app.route('/dashboard')
def dashboard():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    
    return render_template('dashboard.html')
#-------------------------------------------------------------------------------
@app.route('/history')
def history():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    return render_template('history.html')
#-------------------------------------------------------------------------------
@app.route('/about')
def about():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    return render_template('about.html')
#-------------------------------------------------------------------------------
#real_time
@app.route('/realtime')
def realtime():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    return render_template('realtime.html')

#-------------------------------------------------------------------------------
#get calculated heart rated
@app.route('/getheartrate')
def getheartrate():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    global heartrate
    return jsonify(heartrate=heartrate)

#-------------------------------------------------------------------------------
#get frequency response
@app.route('/getfreqresponse')
def getfreqresponse():
    global glob_fs
    graphmode = request.args.get('graphmode', type=str)
    if(graphmode=='' or graphmode==None):
        return jsonify(amp=[], freq=[])
    amplist = []
    freqlist = []
    t = np.arange(0, 1, 1/glob_fs)

    freqlist = np.arange(0, int(glob_fs/2),1)
    for i in freqlist:
        x = np.cos(2*np.pi*i*t)
        if(graphmode[0:3] == "LPF"):
            if(graphmode == "LPFButter"):
                sos = signal.butter(10, 10, 'lp', fs=glob_fs, output='sos')
                y = signal.sosfilt(sos, x)
            elif(graphmode[0:5] == "LPFpt"):
                filt_list = [1/int(graphmode[5:]) for i in range(int(graphmode[5:]))]
                y = signal.lfilter(filt_list, 1, x)
            amplist.append(max(y))
    return jsonify(value=amplist, freq=freqlist.tolist())

#-------------------------------------------------------------------------------
#Thread will calculate heartrate
heartrate = {'heartrate': 0, 'mode': 'unauth'}
glob_fs = 125
def thread_calt_heart_rate(db):
    global heartrate
    recent_reading = collections.deque([0, 0, 0, 0 , 0], maxlen=5)
    ava_rate =  collections.deque([0, 0, 0], maxlen=3)
    while 1:
        try:
            datalist = list(db.real_time.find({'time':{"$gte": datetime.datetime.now()-datetime.timedelta(seconds=5)}}).max_time_ms(500))
            #datalist = list(db.real_time.find({}).sort('_id', -1).limit(400))
            if datalist == []:
                heartrate = {'heartrate': 0, 'mode': 'disconnect'}
                continue
            valuelist = []
            timelist = []
            for i in datalist:
                valuelist.append(i.get('value', 0))
                timelist.append(datetime.datetime.timestamp(i.get('time', None)))
            fs = 1/(abs(timelist[-1] - timelist[0])/len(timelist))
            global glob_fs 
            glob_fs = fs
            f = np.arange(0, fs, fs/len(timelist))
            valuelist = signal.lfilter([1/3, 1/3, 1/3], 1, (valuelist - np.mean(valuelist)))
            value_fft = np.fft.fft(valuelist)
            x_skip = 0
            for i in f:
                if(i < 0.92):
                    x_skip += 1
            value_fft = abs(value_fft)
            rate = f[np.argmax( value_fft[x_skip: int(len(value_fft)/2)] )+x_skip]*60
            ava_rate.append(rate)
            rate = np.average(ava_rate)
            recent_reading.append(rate)
            if(rate > 800):
                heartrate = {'heartrate': 0, 'mode': 'standby'}
            else:
                first_num = recent_reading[0]
                for i in recent_reading:
                    if abs(first_num - i) > 10:
                        heartrate = {'heartrate': 0, 'mode': 'measuring'}
                        break
                else:
                    heartrate = {'heartrate': "%.2f" % rate, 'mode': 'done'}
            
        except Exception as e:
            print(e)
            pass
    """ recentReading = [0, 0, 0, 0, 0, 0, 0, 0]
    HeartrateBuff = collections.deque([0, 0, 0, 0, 0, 0, 0, 0], maxlen=8)
    ava_rate = collections.deque([0, 0, 0], maxlen=3)
    lastRead = 0
    lastBeattime = time.time()
    lastreturntime = time.time()
    Recenttrend = 0
    readingsIndex = 0
    while 1:
        firstlist = list(db.real_time.find({'time':{'$gte': (datetime.datetime.now() - datetime.timedelta(seconds=2))}}).limit(1))
        last_oid = None
        if(firstlist == [] or firstlist[0].get('_id', None) == None):
            heartrate = {'heartrate': 0, 'mode': 'disconnect'}
            continue
        else:
            last_oid = firstlist[0].get('_id', None)
          

        if(firstlist[0].get('time', None) == None):
            lastBeattime = time.time()
        else:
            lastBeattime = datetime.datetime.timestamp(firstlist[0].get('time', None))

        heartrate = {'heartrate': 0, 'mode': 'measuring'}


        while 1:
            try:
                datalist = list(db.real_time.find({"_id":{"$gt": last_oid}}).max_time_ms(300).limit(50))
            except:
                break
            for data in datalist:
                newRead = data.get('value', 0)
                #print(newRead)
                delta = newRead - lastRead
                lastRead = newRead

                #Recenttrend = Recenttrend - np.mean(recentReading) + delta
                Recenttrend = Recenttrend - recentReading[readingsIndex] + delta
                recentReading[readingsIndex] = delta
                readingsIndex = (readingsIndex + 1) % len(recentReading)
                #print(Recenttrend)
            
                if(Recenttrend >= 1.95 and datetime.datetime.timestamp(data.get('time', datetime.datetime.now()))-lastBeattime >= 0.150):
                    #print(60/(time.time()-lastBeattime))
                    currenHearttrate = 60/(datetime.datetime.timestamp(data.get('time', datetime.datetime.now()))-lastBeattime)
                    HeartrateBuff.append(currenHearttrate)
                    avg = np.average(HeartrateBuff)
                    lastBeattime = datetime.datetime.timestamp(data.get('time', datetime.datetime.now()))
                    if(currenHearttrate < 200 and currenHearttrate > 50):
                        ava_rate.append(currenHearttrate)
                        #print("BEAT: ", "%.2f" % np.average(ava_rate))
                        heartrate = {'heartrate': "%.2f" % np.average(ava_rate), 'mode': 'done'}
                        lastreturntime = time.time()
            if(time.time() - lastreturntime >= 5):
                heartrate = {'heartrate': 0, 'mode': 'measuring'}
                break

            if(datalist != []):
                last_oid = datalist[-1].get("_id", None) """
    
        
#-------------------------------------------------------------------------------
#Thread will detect device offline
alive = False
def thread_checkalive(db):
    global alive
    offline_count = 0
    while(1):
        list1 = list(db.device.find())
        if(list1 != []):
            d_state = list1[0].get('alive', False)
            if d_state == True:
                offline_count = 0
            else:
                offline_count +=1
        db.device.update_many({},{'$set':{'alive': False}})
        alive = False if (offline_count >= 4) else True
        time.sleep(2.5)
#-------------------------------------------------------------------------------

# 判斷自己執行非被當做引入的模組，因為 __name__ 這變數若被當做模組引入使用就不會是 __main__
if __name__ == '__main__':
    t1 = threading.Thread(target=thread_calt_heart_rate, args=(conn['admin'],))
    t1.daemon = True
    t1.start()
    t2 = threading.Thread(target=thread_checkalive, args=(conn['admin'],))
    t2.daemon = True
    t2.start()
    app.run(host="0.0.0.0", port="5000", debug=True)