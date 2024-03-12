from flask import Flask, render_template, session, request, redirect
import os
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

app.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
app.config["MYSQL_USER"] = os.getenv('MYSQL_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')
app.config["MYSQL_DB"] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

@app.route('/')
def home():
    if session.get('username') is None:

        usernameTest = "This is a test"
        passwordTest = "This is also a test"

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO main (username, password) VALUES (%s, %s)", (usernameTest, passwordTest))
        mysql.connection.commit()

        return redirect("/register")
    else:
        usernameSession = session["username"]
        return render_template('home.html', usernameSession)

@app.route("/register")
def register():
    return render_template('register.html')

@app.route('/register-user')
def registerUser():
    #usernameRegister = request.form.get("usernameRegister")
    #passwordRegister = request.form.get("passwordRegister")

    
        
    return redirect("/login")

@app.route("/access")
def access():
    #usernameLogin = request.form.get("usernameLogin")
    #passwordLogin = request.form.get("passwordLogin")

    

    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")
