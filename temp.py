from bson.objectid import ObjectId
from flask import Flask,render_template,request
import json
import pymongo
from datetime import date, datetime
import smtplib
import random

class user:
    def __init__(self,name,login):
        self.name = name
        self.login = login

def Now_time():
    # change formate of time convert "2021-11-20 13:17:11.661696" to "26 jan 2017 , 11pm"
    time = str(datetime.now())
    date={"1":"jan","2":"feb","3":"mar","4":"apr","5":"may","6":"jun","7":"jul","8":"aug","9":"sep","10":"oct","11":"nov","12":"dec"}
    if int(time[11:13]) > 11:
        hour = str(int(time[11:13])-12)+time[13:16]+"pm"
    else:
        hour = time[11:16]+"am"
    date_time = time[8:10]+" "+date[time[5:7]]+" "+time[0:4]+" "+hour
    return date_time

with open("config.json","r") as f:
    params = json.load(f)["params"]

user_login = user("login",0)

client = pymongo.MongoClient(params["mongo_address"])
    
db = client[params["database_name"]]
collection_task = db['tasks']
collection_otp = db['otp']
collection_user = db['user']

app = Flask(__name__)

@app.route("/")
def index():
    # Home page
    if user_login.login == 1:
        all_data = collection_task.find()
        return render_template("index.html",data=all_data)
    return render_template("email.html",msg=params["default_msg_email"])

@app.route("/update/<string:id>")
def update_todo(id):
    # Update the list
    if user_login.login == 1:
        id = ObjectId(id)
        update_data = collection_task.find_one({"_id":id})
        return render_template("update.html",data=update_data,id=id)
    return render_template("email.html",msg=params["default_msg_email"])

@app.route("/update_task/<string:id>",methods=["POST","GET"])
def update_task(id):
    # Update the database
    if user_login.login == 1:
        all_data = collection_task.find()
        if request.method == "POST":
            id = ObjectId(id)
            title = request.form.get("title")
            message = request.form.get("message")
            if message == None:
                message = " "
            prev = {"_id":id}
            nextt = {'$set':{"title":title,"message":message}}
            collection_task.update_one(prev,nextt)
        return render_template("index.html",data=all_data)
    return render_template("email.html",msg=params["default_msg_email"])

@app.route("/add_todo")
def add_todo():
    # Add new todo in list
    if user_login.login == 1:
        return render_template("add_todo.html")
    return render_template("email.html",msg=params["default_msg_email"])

@app.route("/add_new_todo",methods=["GET","POST"])
def add_todo_in_database():
    # Add todo in database
    if user_login.login == 1:
        all_data = collection_task.find()
        if request.method == "POST":
            title = request.form.get("title")
            message = request.form.get("message")
            date = Now_time()
            if message == None:
                message = " "
            data = {"title":title,"message":message,"date":date,"complete":0}
            collection_task.insert_one(data)
        return render_template("index.html",data=all_data)
    return render_template("email.html",msg=params["default_msg_email"])

@app.route("/otp",methods=["GET","POST"])
def otp():
    # send otp to email
    if request.method == "POST":
        email = request.form.get('email')
        if email != None:
            try:
                content = random.uniform(100000,999999)
                content = str(int(content))
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.ehlo()
                server.starttls()
                server.login(params["email_id"],params["email_password"])
                server.sendmail(params["email_id"],email,content)
                collection_otp.delete_many({"email":email})
                otp_data = {"email":email,"otp":content,"time":Now_time()}
                collection_otp.insert_one(otp_data)
                return render_template("otp.html",email=email)
            except Exception as e:
                return render_template("email.html",msg=e)
    return render_template("email.html",msg=params["default_msg_email"])

@app.route("/otp-verification/<string:email>",methods=["GET","POST"])
def otp_verification(email):
    # Cheack otp is right or wrong by user
    if request.method == "POST":
        otp = str(request.form.get('otp'))
        email_data = collection_otp.find_one({"email":email})
        print(email_data["otp"])
        if str(email_data["otp"]) == otp:
            collection_otp.delete_one({"email":email})
            return render_template("form.html",email=email)
        collection_otp.delete_one({"email":email})
    return render_template("email.html",msg=params["otp_is_wrong"])
    
@app.route("/email")
def email():
    # Email verification
    return render_template("email.html",msg=params["default_msg_email"])

@app.route("/delete/<string:id>")
def delete(id):
    # Delete task from database
    if user_login.login == 1:
        id = ObjectId(id)
        collection_task.delete_one({"_id":id})
        all_data = collection_task.find()
        return render_template("index.html",data=all_data)
    return render_template("email.html",msg=params["default_msg_email"])

@app.route("/complete/<string:id>")
def complete(id):
    # Mark task to complete
    if user_login.login == 1:
        id = ObjectId(id)
        task_data = collection_task.find_one({"_id":id})
        prev = {"_id":id}
        if task_data["complete"] == 0:
            nextt = {'$set':{"complete":1}}
        else:
            nextt = {'$set':{"complete":0}}
        collection_task.update(prev,nextt)
        all_data = collection_task.find()
        return render_template("index.html",data=all_data)
    return render_template('email.html',msg=params["default_msg_email"])

@app.route("/submit-user-information/<string:email>",methods=["GET","POST"])
def submit_information(email):
    # add user information in database
    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        user_data = {"name":name,"email":email,"password":password}
        user_login.name = name
        user_login.login = 1
        collection_user.insert_one(user_data)
        all_data = collection_task.find()
        return render_template("index.html",data=all_data)
    return render_template('email.html',msg=params["default_msg_email"])

@app.route("/logout")
def logout():
    # logout from user account
    user_login.login = 1
    return render_template("email.html",msg=params["default_msg_email"])

@app.route('/login')
def login():
    return render_template("login.html")

@app.route("/cheack-username",methods=["GET","POST"])
def cheack_username():
    # Cheack username and password give by user in login
    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get("password")
        data_user = collection_user.find_one({"name":name})
        if data_user == None:
            return render_template("login.html",msg=params["msg_user_wrong_username"])
        if data_user["password"] == password:
            all_data = collection_task.find()
            user_login.login = 1
            return render_template("index.html",data=all_data)
        return render_template("login.html",msg=params["msg_user_wrong_pas"])
    return render_template("email.html",msg=params["default_msg_email"])

if "__main__" == __name__:
    app.run()