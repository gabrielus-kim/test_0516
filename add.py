from flask import Flask, render_template
from flask import request, session, redirect
import pymysql

db=pymysql.connect(
    user='root',
    passwd='avante',
    host='localhost',
    db='web',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

app=Flask(__name__,
        static_folder='static',
        template_folder='template')

app.config['ENV']='Development'
app.config['DEBUG']=True
app.secret_key='who are you?'

def who_am_i():
    return session['user']['name'] if 'user' in session else 'Everyone !!'

def am_I_here():
    return True if 'user' in session else False

def am_I_join(id):
    cur=db.cursor()
    cur.execute(f"""
        select name from author where name = '{id}'
    """)
    user=cur.fetchone()
    return False if user is None else True


@app.route('/')
def index():
    if am_I_here() == True:
        message = 'Have a good day'
    else:
        message = 'login 해주세요 ~'
    return render_template('template.html',
                            owner=who_am_i(),
                            message=message)


@app.route('/login', methods=['GET','POST'])
def login():
    if am_I_here() == True:
        message = '이미 login 상태 입니다.'
        return render_template('template.html',
                                owner=who_am_i(),
                                message=message)
    else:
        message = 'login 해주세요 ~'
    if request.method == 'POST':
        cur=db.cursor()
        cur.execute(f"""
            select id, name from author where name = '{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            message = "등록이 안된 login ID 입니다."
            return render_template('login.html',
                                    owner=who_am_i(),
                                    message=message)
        else:
            cur=db.cursor()
            cur.execute(f"""
                select id, name, password from author
                where name='{request.form['id']}' 
                    and password=SHA2('{request.form['pw']}',256)
            """) 
            password=cur.fetchone()
            if password is None:
                message = '패스워드를 확인해 주세요'
            else:
                session['user']=password
                return redirect('/')
    return render_template('login.html',
                            owner=who_am_i(),
                            message=message)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/join', methods=['GET','POST'])
def join():
    if am_I_here() == True:
        message = '이미 회원 가입 상태 입니다.'
        return render_template('template.html',
                                owner=who_am_i(),
                                message=message)
    else:
        message = '회원가입을 해주세요 ~'
    if request.method == 'POST':
        if am_I_join(request.form['id']) == True:
            message = '이미 회원 가입 하셨읍니다. 확인 부탁드립니다.'
        else:
            cur=db.cursor()
            cur.execute(f"""
                insert into author (name, password, profile)
                values ('{request.form['id']}',
                SHA2('{request.form['pw']}',256),
                '{request.form['pf']}')
            """)
            db.commit()
            return redirect('/')
    return render_template('join.html',
                            owner=who_am_i(),
                            message=message)
@app.route('/withdraw')
def withdraw():
    if am_I_here() == False:
        message = 'login 하신후 회원 탈퇴 부탁드립니다.'
    else:
        cur=db.cursor()
        cur.execute(f"""
            delete from author where name='{session['user']['name']}'
        """)
        db.commit()
        message=f"""{session['user']['name']}님이 정상적으로 회원 탈퇴되셨읍니다."""
        
        session.pop('user', None)
    return render_template('template.html',
                            owner=who_am_i(),
                            message=message)

app.run(port='8000')