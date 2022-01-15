from flask import Flask,render_template,request,make_response
import mysql.connector
from datetime import datetime
import random

class LinkedList:
    # create cookie for new user
    def __init__(self):        
        self.cookie = ""

    def create_cookie(self,name):
        for i in name:
            if i != " ":
                num = str(int(random.uniform(1,9)))
                self.cookie += i + num
        if len(self.cookie) >= 8:
            self.cookie = self.cookie[0:8]
        else:
            while len(self.cookie) != 8:
                self.cookie += str(int(random.uniform(1,9)))

connection = mysql.connector.connect(user='root', password='', host='localhost', database='form')

cursor = connection.cursor()

app = Flask(__name__)

def is_user_login():
    # find that user login or not
    name = request.headers.get('Cookie')
    if name == None:
        return False
    cok = name.split(";")
    name = cok[len(cok)-1]
    if name[0] == " ":
        name = name[1:]
    sql = "SELECT * from userinfo WHERE id = '%s'"%(name)    
    cursor.execute(sql)
    data1 = cursor.fetchall()
    if len(data1) == 0:
        return False
    if data1[0][6] == 0:
        return False
    return True

def Now_time():
    # change formate of time convert "2021-11-20 13:17:11.661696" to "26 jan 2017 , 11pm"
    time = str(datetime.now())
    date={"01":"jan","02":"feb","03":"mar","04":"apr","05":"may","06":"jun","07":"jul","08":"aug","09":"sep","10":"oct","11":"nov","12":"dec"}
    if int(time[11:13]) > 11:
        hour = str(int(time[11:13])-12)+time[13:16]+"pm"
    else:
        hour = time[11:16]+"am"
    print(time[5:7])
    date_time = time[8:10]+" "+date[time[5:7]]+" "+time[0:4]+" "+hour
    return date_time

@app.route('/')
def index():
    print(dict(request.headers))
    if is_user_login():
        name = request.headers.get('Cookie')
        if name == None:
            return render_template("email.html")
        cok = name.split(";")
        name = cok[len(cok)-1]
        if name[0] == " ":
            name = name[1:]
        sql_user = "SELECT * from userinfo WHERE id = '%s'"%(name)
        cursor.execute(sql_user)
        data = cursor.fetchall()
        if data[0][6] == "1":
            sql = "SELECT * from forms WHERE authorid = '%s'"%(name)
            cursor.execute(sql)
            data = cursor.fetchall()            
            return render_template('index.html',data=data,a=0)
    return  render_template('email.html')

@app.route('/email')
def email():
    msg = "Insert your username and password"
    return render_template('email.html',msg=msg)

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/create-Account',methods=['POST','GET'])
def create_account():
    if request.method == 'POST':
        email = request.form.get('email')
        return render_template('user_form.html',email=email,msg="fill your information")

@app.route('/submit-user-information/<string:email>',methods=['POST',"GET"])
def submit_user_information(email):
    if request.method == "POST":
        name = request.form.get('name')
        user = request.form.get('username')
        password = request.form.get('password')
        if " " in user:
            return render_template('user_form.html',msg="Do not use space in username",email=email)
        node = LinkedList()
        node.create_cookie(name)
        sql = "SELECT * from forms WHERE authorid = '%s'"%(node.cookie)
        cursor.execute(sql)
        data = cursor.fetchall()
        resp = make_response(render_template('index.html',data=data,a=0))
        co = str(email +"="+ node.cookie)
        resp.set_cookie(email, node.cookie)
        sql ="INSERT INTO userinfo (name,username,password,email,id,login) VALUES ('%s','%s','%s','%s','%s','%s');"%(name,user,password,email,co,"1")
        cursor.execute(sql)
        connection.commit()
        return resp

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/create-form',methods=["POST","GET"])
def create_form():
    name = request.headers.get('Cookie')
    if not is_user_login():
        return render_template("email.html")
    title = request.form.get('title')
    small = request.form.get('small')
    large = request.form.get('large')
    title = title.replace(" ","%")    
    smal = ["input"+str(i) for i in range(int(small)+int(large))]
    return render_template('form.html',data=smal,small=small,large=large,title=title)

@app.route('/create-new-form/<string:small>/<string:large>/<string:title>',methods=["GET","POST"])
def create_new_form(small,large,title):
    if request.method == "POST":
        if not is_user_login():
           return render_template('email.html')
        data1 = ""
        for i in range(int(small)+int(large)):
            data = request.form.get("input"+str(i))
            data1+=data+"/split/"
        title = title.replace("%"," ")
        time = Now_time()
        name = request.headers.get('Cookie')
        if name != None:
            cok = name.split(";")
            name = cok[len(cok)-1]
            if name[0] == " ":
                name = name[1:]        
            sql = "INSERT INTO forms (title,date,authorid,smallcolumn,data) VALUES ('%s','%s','%s','%s','%s');"%(title,time,name,small,data1)
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * from forms WHERE authorid = '%s'"%(name)
            cursor.execute(sql)
            data = cursor.fetchall()
            return render_template('index.html',data=data,a=0)
        return  render_template('email.html')

@app.route('/see/<string:id>')
def see(id):
    if not is_user_login():
        return render_template('email.html')
    name = request.headers.get('Cookie')    
    cok = name.split(";")
    name = cok[len(cok)-1]
    if name[0] == " ":
        name = name[1:]
    sql = "SELECT * from forms WHERE id = '%s'"%(id)
    cursor.execute(sql)
    data = cursor.fetchall()
    if data[0][3] == name:
        sql = "SELECT * from filledform WHERE formid = '%s'"%(id)
        cursor.execute(sql)
        data = cursor.fetchall()
        da = []        
        if data != None:
            for i in data:
                sql = "SELECT * from userinfo WHERE id = '%s'"%(i[1])
                cursor.execute(sql)
                data1 = cursor.fetchall()
                if len(data1) != 0:
                    da.append([data1[0][1],i[4],data1[0][2]])
            return render_template("see.html",data=da,id=id)
    return render_template()

@app.route('/search',methods=['GET','POST'])
def search():
    if not is_user_login():
        return render_template('email.html')
    if request.method == "POST":
        name = request.headers.get('Cookie')
        if name == None:
            return render_template('email.html')
        id = int(request.form.get('search'))
        sql = "SELECT * from forms WHERE id = '%d'"%(id)
        cursor.execute(sql)
        data = cursor.fetchall()
        return render_template("index.html",data=data,a = 1)

@app.route('/fillform/<string:id>')
def fill_form(id):
    if not is_user_login():
        return render_template('email.html')
    id = int(id)
    sql = "SELECT * from forms WHERE id = '%d'"%(id)
    cursor.execute(sql)
    data = cursor.fetchall()
    small = int(data[0][4])
    da = data[0][5].split("/split/")
    if da[len(da)-1] == "":
        da.pop()    
    dat = da[0:small]
    data=[]
    for i in range(len(dat)):
        data.append([da[i],"item"+str(i)])
    data1 = []
    for i in range(small,len(da)):
        data1.append([da[i],"item"+str(i)])
    return render_template('fill_form.html',a=0,data=data,data1=data1,small=str(len(da)),large=str(id),msg="fill the form according the question")

@app.route("/submitform/<string:leng>/<string:id>",methods=["GET","POST"])
def submit_form(leng,id):
    if not is_user_login():
        return render_template('email.html')
    leng = int(leng)
    data = ""
    for i in range(leng):
        da = request.form.get('item'+str(i))
        data=data + da + '/split/'
    name = request.headers.get('Cookie')
    if name!=None:
        cok = name.split(";")
        name = cok[len(cok)-1]
        if name[0] == " ":
            name = name[1:]
        time = Now_time()
        sql = "INSERT INTO filledform (clientid,formid,data,date) VALUES ('%s','%s','%s','%s');"%(name,id,data,time)
        cursor.execute(sql)
        connection.commit()        
        sql = "SELECT * from forms WHERE authorid = '%s'"%(name)
        cursor.execute(sql)
        data = cursor.fetchall()
        return render_template('index.html',data=data,a=0)
    sql = "SELECT * from forms WHERE authorid = '%s'"%(name)
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template('index.html',data=data,a=0)

@app.route('/logout')
def logout():
    if not is_user_login():
        return render_template('email.html')
    name = request.headers.get('Cookie')
    if name!=None:
        cok = name.split(";")
        name = cok[len(cok)-1]
        if name[0] == " ":
            name = name[1:]
        sql = "UPDATE userinfo SET login = '%s' WHERE id = '%s'"%("0",name)
        cursor.execute(sql)
        connection.commit()
    return render_template('email.html',msg="insert your email")

@app.route('/login-user')
def login_user():
    return render_template('login.html',msg="insert your username and password")

@app.route('/cheack-username',methods=["GET","POST"])
def cheack_username():
    if request.method == "POST":
        user = request.form.get('user')
        password = request.form.get('password')
        sql = "SELECT * from userinfo WHERE username = '%s'"%(user)
        cursor.execute(sql)
        data = cursor.fetchall()
        if len(data) == 0:
            return render_template('login.html',msg="username is wrong")
        if data[0][3] == password:
            sql = "UPDATE userinfo SET login = '%s' WHERE username = '%s'"%("1",user)
            cursor.execute(sql)
            connection.commit()
            print(data[0][5])
            sql = "SELECT * from forms WHERE authorid = '%s'"%(data[0][5])
            cursor.execute(sql)
            data1 = cursor.fetchall()
            resp = make_response(render_template('index.html',data=data1,a=0))
            name = data[0][5].split("=")
            resp.set_cookie(name[0],name[1])
            return resp
        return render_template('login.html',msg="password is wrong")

@app.route('/see-content/<string:user>/<string:form_id>')
def see_content(user,form_id):
    if not is_user_login():
        return render_template('email.html')
    name = request.headers.get('Cookie')
    if name == None:
        return render_template('emaill.html')
    cok = name.split(";")
    name = cok[len(cok)-1]
    if name[0] == " ":
        name = name[1:]
    sql = "SELECT * from forms WHERE id = '%d'"%(int(form_id))
    cursor.execute(sql)
    data = cursor.fetchall()
    sql = "SELECT * from userinfo WHERE username = '%s'"%(user)
    cursor.execute(sql)
    data1 = cursor.fetchall()
    if data[0][3] != name:
        return render_template("email.html")
    print(data)
    forms = data[0][5].split('/split/')
    if forms[len(forms)-1] == "":
        forms.pop()
    sql = "SELECT * from filledform WHERE clientid = '%s'"%(data1[0][5])
    cursor.execute(sql)
    data2 = cursor.fetchall()
    print(data2)
    value = data2[0][3].split('/split/')
    final_data = []    
    for i in range(len(forms)):
        final_data.append([forms[i],value[i]])
    return render_template('see_user_data.html',data=final_data)

if __name__ == "__main__":
    app.run()