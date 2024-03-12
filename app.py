from flask import Flask, render_template, session, request, redirect, flash
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
        return redirect("/register")
    else:
        usernameSession = session["username"]
        return render_template('home.html', usernameSession)

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/register-user')
def registerUser():
    usernameRegister = request.form.get("usernameRegister")
    passwordRegister = request.form.get("passwordRegister")
    codeRegister = str(request.form.get("codeRegister"))

    if codeRegister == "bellingham5":
        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM users WHERE LOWER(username) = %s", [usernameRegister.lower()])
        sameUsername = cur.fetchall()
        if not sameUsername:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (usernameRegister, passwordRegister))
            mysql.connection.commit()
            return redirect("/login")
        else:
            flash("This username already exists!")
            return render_template('register.html')

    else:
        flash("Incorrect access code!")
        return render_template('register.html')

    

@app.route("/access")
def access():
    usernameLogin = request.form.get("usernameLogin")
    passwordLogin = request.form.get("passwordLogin")

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE LOWER(username) = %s", [usernameLogin.lower()])
    listInfoUserAccess = cur.fetchall()
    if not usernameLogin:
        flash("Incorrect username!")
        return render_template("login.html")
    else:
        userInfoAccess = listInfoUserAccess[0]

        if userInfoAccess[2] == passwordLogin:
            session["user_id"] = userInfoAccess[0]
            session["username"] = usernameLogin
            return redirect("/")
        else:
            flash("Incorrect password!")
            return render_template("login.html")
