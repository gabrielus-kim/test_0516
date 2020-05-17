from flask import Flask, render_template
from flask import request, session, redirect, abort
import pymysql
from datetime import datetime

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

def get_menu():
    menu=[]
    cur=db.cursor()
    cur.execute(f"""
        select id, title from topic
    """)
    menu_list=cur.fetchall()
    for i in menu_list:
        menu.append(f"""
            <li><a href='/{i['id']}'>{i['title']}</a></li>
            """)
    return '\n'.join(menu)


@app.route('/')
def index():
    menu=''
    if am_I_here() == True:
        message = 'Have a good day'
        menu=get_menu()
    else:
        message = 'login 해주세요 ~'
    return render_template('template.html',
                            owner=who_am_i(),
                            menu=menu,
                            id='wrong number',
                            message=message)

@app.route('/<id>')
def get_post(id):
    cur=db.cursor()
    cur.execute(f"""
        select id, title, description from topic where id ='{id}'
    """)
    title=cur.fetchone()
    return render_template('template.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            id=title['id'],
                            title=title['title'],
                            content=title['description'])

@app.route('/delete/<id>')
def delete_post(id):
    if am_I_here() == False:
        message="게시판 삭제는 log in 후 가능합니다."
        return render_template('template.html',
                            owner=who_am_i(),
                            id='wrong number',
                            message=message) 
    else:
        if id == 'wrong number':    
            message='삭제는 게시물 조회후 삭제 가능합니다..'
        else:
            cur=db.cursor()
            cur.execute(f"""
                delete from topic where id ='{id}'
                """)
            db.commit()
            message='요청하신 게시물이 삭제되었읍니다.'
    return render_template('template.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            id='wrong number',
                            message=message) 

@app.route('/update/<id>', methods=['GET','POST'])
def update_post(id):
    if am_I_here() == False:
        message="게시판 변경은 log in 후 가능합니다."
        return render_template('template.html',
                                owner=who_am_i(),
                                id='wrong number',
                                message=message) 
    if id == 'wrong number':    
        message='게시물 조회후 내용 수정이 가능합니다.'
        return render_template('template.html',
                                owner=who_am_i(),
                                id='wrong number',
                                menu=get_menu(),
                                message=message)  
    if request.method == 'POST':
        cur=db.cursor()
        cur.execute(f"""
            update topic set description='{request.form['content']}'
            where id ='{id}'
            """)
        db.commit() 
        cur=db.cursor()
        message="수정한 내용이 반영되었읍니다."
        return render_template('template.html',
                            owner=who_am_i(),
                            id='wrong number',
                            menu=get_menu(),
                            message=message) 
    else:
        message='내용 수정이 가능합니다.'
        cur=db.cursor()
        cur.execute(f"""
            select id, title, description from topic where id ='{id}'
        """)
        title=cur.fetchone()
    return render_template('update.html',
                    owner=who_am_i(),
                    id=title['id'],
                    title=title['title'],
                    content=title['description'],
                    message=message) 

@app.route('/write', methods=['GET','POST'])
def write():
    if am_I_here() == False:
        message="게시판 작성은 log in 후 가능합니다."
        return render_template('template.html',
                                owner=who_am_i(),
                                id='wrong number',
                                message=message) 
    else:
        message="게시판 작성을 후 등록해주세요"  
    if request.method == 'POST':
        cur=db.cursor()
        cur.execute(f"""
            insert into topic (title, description, created, author_id)
            values ('{request.form['title']}',
                '{request.form['content']}',
                '{datetime.now()}',
                '{session['user']['id']}')
        """)
        db.commit()
        message=f"""
            {request.form['title']} 가 등록되었읍니다.
                """
        return render_template('template.html',
                            owner=who_am_i(),
                            id='wrong number',
                            menu=get_menu(),
                            message=message)

    return render_template('write.html',
                            owner=who_am_i(),
                            id='wrong number',
                            message=message)

@app.route('/login', methods=['GET','POST'])
def login():
    if am_I_here() == True:
        message = '이미 login 상태 입니다.'
        return render_template('template.html',
                                owner=who_am_i(),
                                id='wrong number',
                                menu=get_menu(),
                                message=message)
    else:
        message = 'login 해주세요 ~'
    if request.method == 'POST':
        if am_I_join(request.form['id']) == False:
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
                            id='wrong number',
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
                                id='wrong number',
                                menu=get_menu(),
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
                            id='wrong number',
                            
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
                            id='wrong number',
                            message=message)

@app.route('/favicon.ico')
def favicon():
    return abort(404)

app.run(port='8000')