from flask import Flask, render_template, request, redirect, g, session, url_for, flash, jsonify, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymongo
import datetime
import time
import json
from bson import ObjectId


# 初始化 Flask 類別成為 instance
app = Flask(__name__)
conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/')

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
@app.route('/getfiltertype')
def getfiltertype():
    list1 = ['third', 'nine', 'eleven']
    return jsonify(listfilter = list1)
#-------------------------------------------------------------------------------
#get tstamp
@app.route('/gettstamp')
def gettstamp(): 
    return jsonify(timestamp=time.time())
#-------------------------------------------------------------------------------
@app.route('/checkalive')
def checkalive():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    list1 = list(db.device.find())
    if(list1 != []):
        alive = list1[0].get('alive', False)
    db.device.update_many({},{'$set':{'alive': False}})
    return jsonify(alive=alive)
#-------------------------------------------------------------------------------
@app.route('/systemtime')
def systemtime():
    return Response(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mimetype='text')
#-------------------------------------------------------------------------------
#return  raw data 
@app.route('/getrawdata', methods=['GET', 'POST'])
def getrawdata():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    count = request.args.get("count", type=int)
    if count == None:
        return jsonify(start_oid=None, count=0, value=[], time=[])
    print(count)
    if count == 0:  #Draw New Chart
        datalist = list(db.real_time.find({'time':{'$gte': (datetime.datetime.now() - datetime.timedelta(seconds=1.5))}}))
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
        return jsonify(start_oid=json_start_oid, count=len(valuelist), value=valuelist, time=timelist)
    elif count > 0:   #Update chart
        str_start_oid = request.args.get('start_oid', type=str)
        str1_start_oid =  str_start_oid.replace("\"", "")
        start_oid = ObjectId(str1_start_oid)
        json_start_oid = JSONEncoder().encode(start_oid)
        
        valuelist = []
        datalist = list(db.real_time.find({"_id":{"$gte": start_oid}}).skip(count).max_time_ms(300).limit(500))
        if datalist == []:
            return jsonify(start_oid=json_start_oid, count=count, value=[], time=[])
        valuelist = []
        timelist = []
        for i in datalist:
            if i.get('value', None) != None:
                valuelist.append(i.get('value', None))
                timelist.append(datetime.datetime.timestamp(i.get('time', None)))
        
        
        return jsonify(start_oid=json_start_oid, count=len(valuelist)+count, value=valuelist, time=timelist)

    return jsonify(start_oid=None, count=0, value=[], time=[])
#-------------------------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    return render_template('dashboard.html')

# 判斷自己執行非被當做引入的模組，因為 __name__ 這變數若被當做模組引入使用就不會是 __main__
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True)