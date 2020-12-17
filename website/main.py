from flask import Flask, render_template, request, redirect, g, session, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymongo
import datetime
import time


# 初始化 Flask 類別成為 instance
app = Flask(__name__)
conn = pymongo.MongoClient('mongodb://0.0.0.0:27017/')

#-----------------------------------------------------------------------------------
app.secret_key='zxcasdqwe123'
login_manger=LoginManager()
login_manger.session_protection='strong'
login_manger.init_app(app)

class User(UserMixin):
    pass
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
        return render_template('login.html') 
    return render_template('dashboard.html')
#-------------------------------------------------------------------------------
@app.route('/login')
def login():   
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
                print(session)
                curr_user = User()
                curr_user.id = user_info['username']
                #通過flask-login的login_user方法登入用戶
                login_user(curr_user)
                
                return redirect('/dashboard')
                
        flash('Wrong infornation!!')
        return redirect(url_for('login'))
#-------------------------------------------------------------------------------
#logout
@app.route('/logout')
def logout():
    user = current_user
    user.authenticated = False
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
#get tstamp
@app.route('/gettstamp')
def gettstamp(): 
    return jsonify(timestamp=time.time())

@app.route('/dashboard')
def dashboard():
    user,db = check_user()
    if(db ==None):
        return redirect(url_for('login')) 
    return render_template('dashboard.html')

# 判斷自己執行非被當做引入的模組，因為 __name__ 這變數若被當做模組引入使用就不會是 __main__
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True)