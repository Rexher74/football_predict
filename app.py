from flask import Flask, render_template, session, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB

mysql = MySQL(app)

@app.route('/')
def home():
    if session.get('username') is None:
        testU = "test_username"
        testP = "test_password"
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO main (username, password) VALUES (%s, %s)", (testU, testP))
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
    username = request.form.get("usernameRegister")
    password = request.form.get("passwordRegister")

    alreadyExistsUsername = False

    with open("users.txt", "r") as file:
        usernameLine = True
        for line in file.readlines():
            if usernameLine and line == username:
                alreadyExistsUsername = True
            usernameLine = not usernameLine
    
    if (alreadyExistsUsername):
        return redirect("/register-user")
    
    else:
        with open("users.txt", "w") as file:
            file.write(f'{username}\n{password}\n')

        return redirect("/login")

@app.route("/access")
def access():
    usernameLogin = request.form.get("usernameLogin")
    passwordLogin = request.form.get("passwordLogin")

    with open("users.txt", "r") as file:
        usernameLine = True
        lines = file.readlines()
        for i, line in enumerate(lines):
            if usernameLine and line == usernameLogin and lines[i+1] == passwordLogin:
                session["username"] = usernameLogin
                return redirect("/")
            usernameLine = not usernameLine

    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")
