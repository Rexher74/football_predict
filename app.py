from flask import Flask, render_template, session, request, redirect
app = Flask(__name__)

@app.route('/')
def home():
    if session.get('username') is None:
        return render_template('register.html')
    else:
        usernameSession = session["username"]
        return render_template('home.html', usernameSession)

@app.route('/register-user')
def registerUser():
    username = request.form.get("usernameRegister")
    password = request.form.get("passwordRegister")

    alreadyExistsUsername = False

    with open("users.txt", "r") as file:
        usernameLine = True
        for line in file.readlines():
            if username and line == username:
                alreadyExistsUsername = True
            usernameLine = not usernameLine
    
    if (alreadyExistsUsername):
        return redirect("/register-user")
    
    else:
        with open("users.txt", "w") as file:
            file.write(f'{username}\n{password}\n')

        return redirect("/login")

@app.route("/login")
def login():
    usernameLogin = request.form.get("usernameLogin")
    passwordLogin = request.form.get("passwordLogin")

    with open("users.txt", "r") as file:
        username = True
        lines = file.readlines()
        for i, line in enumerate(lines):
            if username and line == usernameLogin and lines[i+1] == passwordLogin:
                session["username"] = usernameLogin
                return redirect("/")
            usernameLine = not usernameLine
    
    return redirect("/login")
