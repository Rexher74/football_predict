from flask import Flask, render_template, session, request, redirect

app = Flask(__name__)

class User:
    def __init__(self, username, password):
        self.id = len(users)
        self.username = username
        self.password = password

# Users List
users = []

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

@app.route('/register-user')
def registerUser():
    usernameRegister = request.form.get("usernameRegister")
    passwordRegister = request.form.get("passwordRegister")

    alreadyExistsUsername = False
    indexIter = 0
    
    while alreadyExistsUsername and indexIter < len(users):
        if users[indexIter].username == usernameRegister:
            alreadyExistsUsername = True
        indexIter += 1
    
    if (alreadyExistsUsername):
        return redirect("/register-user")
    
    else:
        newUser = User(usernameRegister, passwordRegister)
        users.append(newUser)
        
        return redirect("/login")

@app.route("/access")
def access():
    usernameLogin = request.form.get("usernameLogin")
    passwordLogin = request.form.get("passwordLogin")

    for user in users:
        if user.username == usernameLogin and user.password == passwordLogin:
            session["username"] = usernameLogin
            return redirect("/")

    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")
