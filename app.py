from flask import Flask, render_template, session, request, redirect, flash, make_response, jsonify
import requests
from bs4 import BeautifulSoup
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import os

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

app.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
app.config["MYSQL_USER"] = os.getenv('MYSQL_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')
app.config["MYSQL_DB"] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

def getGames(jornada):
    URL = "https://www.elmundo.es/deportes/futbol/primera-division/calendario.html"
    ID = f"jornada{jornada}"
    
    gameList = []

    r = requests.get(URL)

    soup = BeautifulSoup(r.text, features='html.parser')

    resJornada = soup.find('table', id=ID).find('tbody')
    for el in resJornada:
        for e in el:
            try:
                if (e.get_text() != "\n"):
                    if e["class"][0] != "resultado":
                        gameList.append([e.get_text().replace("\n", ""), e.find("img")["src"]])
                    else:
                        gameList.append(e.get_text().replace("\n", ""))
            except:
                pass
    
    resList = []

    index = 0

    while (index < len(gameList)):
        resList.append([gameList[0+index], gameList[1+index], gameList[2+index]])
        index += 3

    return resList

def updateTimeMatchday(currentJornada):
    # End Matchday
    dataTime = getGames(currentJornada+1)

    newTime = dataTime[-1][-2]

    newTimeFormated = datetime.strptime(newTime, "%d/%m %H:%M")

    newTimeFormated = newTimeFormated.replace(year=2024)

    newTimeFormated = newTimeFormated + timedelta(hours=3)

    # Start Matchday

    newTimeStart = dataTime[0][-2]

    newTimeFormatedStart = datetime.strptime(newTimeStart, "%d/%m %H:%M")

    newTimeFormatedStart = newTimeFormatedStart.replace(year=2024)

    newTimeFormatedStart = newTimeFormatedStart - timedelta(hours=1)

    return [newTimeFormated, newTimeFormatedStart]

def getValRes(res):
    # Dividir la cadena en dos números
    goals = res.split('-')
    num_local = int(goals[0])
    num_visitor = int(goals[1])

    # Verificar cuál número es mayor
    if num_local > num_visitor:
        return 1  # El número de la izquierda es mayor
    elif num_local < num_visitor:
        return 2  # El número de la derecha es mayor
    else:
        return 0  # Los números son iguales

dictPoints = {
    0: 0,
    1: 1,
    2: 2,
    3: 5,
    4: 10,
    5: 20,
    6: 50,
    7: 100,
    8: 250,
    9: 500,
    10: 1000,
}

@app.route('/')
def home():
    if session.get('username') is None and session.get('user_id') is None:
        return redirect("/register")
    else:
        usernameSession = session["username"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT value, matchday FROM matchdaydata WHERE type = 0")
        dataMatchDay = cur.fetchall()[0]

        gamesCurentMatchday = getGames(dataMatchDay[1])

        if datetime.now() > dataMatchDay[0]:
            nextDate = updateTimeMatchday(dataMatchDay[1])
            cur = mysql.connection.cursor()
            cur.execute("UPDATE matchdaydata SET matchday = matchday + 1, value = %s WHERE type = 0", [nextDate[0]])
            mysql.connection.commit()

            cur = mysql.connection.cursor()
            cur.execute("UPDATE matchdaydata SET matchday = matchday + 1, value = %s WHERE type = 1", [nextDate[1]])
            mysql.connection.commit()

            correctResults = []

            for match in gamesCurentMatchday:
                correctResults.append(getValRes(match[1]))

            cur = mysql.connection.cursor()
            cur.execute("SELECT user_id, g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, username FROM predictions WHERE matchday = %s", [dataMatchDay[1]])
            allPredictions = cur.fetchall()

            for userPred in allPredictions:
                numCorrects = 0
                for i in range(10):
                    if correctResults[i] == userPred[i+1]:
                        numCorrects+=1
                pointsToGive = dictPoints[numCorrects]

                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO points (user_id, username, points, matchday) VALUES (%s, %s, %s, %s)", (userPred[0], userPred[11], pointsToGive, dataMatchDay[1]))
                mysql.connection.commit()

                cur = mysql.connection.cursor()
                cur.execute("UPDATE users SET points = points + %s WHERE id = %s", (pointsToGive, userPred[0]))
                mysql.connection.commit()

        cur = mysql.connection.cursor()
        cur.execute("SELECT g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 FROM predictions WHERE user_id=%s", [session["user_id"]])
        currentpredictions = cur.fetchall()

        if not currentpredictions:
            predictsToPass = []
        else:
            currentpredictions = currentpredictions[0]
            predictsToPass = []
            for pred in currentpredictions:
                predictsToPass.append(pred)

        cur = mysql.connection.cursor()
        cur.execute("SELECT username, points FROM users ORDER BY points DESC")
        usersToLoad = cur.fetchall()

        return render_template('home.html', usernameSession = usernameSession, usersToLoad = usersToLoad, GCMD = gamesCurentMatchday, CP = predictsToPass, MD_Home = dataMatchDay[1])

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/register-user', methods=["POST"])
def registerUser():
    usernameRegister = request.form.get("usernameRegister")
    passwordRegister = request.form.get("passwordRegister")
    codeRegister = request.form.get("codeRegister")

    if not usernameRegister.isalnum():
        flash("Username can only contain letters and numbers!")
        return redirect("/register")
    else:
        if codeRegister == "realoviedoaprimera":
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
                return redirect("/register")

        else:
            flash("Incorrect access code!")
            return redirect("/register")


@app.route("/access", methods=["POST"])
def access():
    usernameLogin = request.form.get("usernameLogin")
    passwordLogin = request.form.get("passwordLogin")

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE LOWER(username) = %s", [usernameLogin.lower()])
    listInfoUserAccess = cur.fetchall()
    if not listInfoUserAccess:
        flash("Incorrect username!")
        return redirect("/login")
    else:
        userInfoAccess = listInfoUserAccess[0]

        if userInfoAccess[2] == passwordLogin:
            session["user_id"] = userInfoAccess[0]
            session["username"] = usernameLogin
            return redirect("/")
        else:
            flash("Incorrect password!")
            return redirect("/login")
        
@app.route("/save-prediction", methods=["POST"])
def savePrediction():
    if request.method == "POST":
        data = request.json["dataPrediction"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT matchday FROM matchdaydata WHERE type = %s", [0])
        matchdayToPost = cur.fetchall()[0][0]

        cur = mysql.connection.cursor()
        cur.execute("SELECT value FROM matchdaydata WHERE type = 1")
        limitToPost = cur.fetchall()[0][0]

        if (limitToPost > datetime.now()):
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM predictions WHERE user_id = %s AND matchday = %s", (session["user_id"], matchdayToPost))
            userMatchdayCurrentPost = cur.fetchall()

            if not userMatchdayCurrentPost:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO predictions (user_id, username, matchday, g1, g2, g3, g4, g5, g6, g7, g8, g9, g10) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (session["user_id"], session["username"], matchdayToPost,
                            data["g1"], data["g2"], data["g3"], data["g4"], data["g5"], data["g6"], data["g7"], data["g8"], data["g9"], data["g10"]))
                mysql.connection.commit()

            else:
                cur = mysql.connection.cursor()
                cur.execute("UPDATE predictions SET g1=%s, g2=%s, g3=%s, g4=%s, g5=%s, g6=%s, g7=%s, g8=%s, g9=%s, g10=%s WHERE user_id = %s AND matchday = %s", (data["g1"], data["g2"], data["g3"], data["g4"], data["g5"], data["g6"], data["g7"], data["g8"], data["g9"], data["g10"], session["user_id"], matchdayToPost))
                mysql.connection.commit()

            return make_response(jsonify("Prediction updated successfully!"))
        
        else:
            return make_response(jsonify("You are out of time!"))
        
@app.route("/signout")
def signOut():
    session.clear()
    return redirect("/")

@app.route("/user/<string:usernameToLoad>/<int:matchDayToLoad>")
def getUser(usernameToLoad, matchDayToLoad):

    cur = mysql.connection.cursor()
    cur.execute("SELECT g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 FROM predictions WHERE username=%s AND matchday = %s", (usernameToLoad, matchDayToLoad))
    basePredictionUser = cur.fetchall()

    if not basePredictionUser:
        gamesMacthDaySelected = []
        basePredictionUser = []

        return render_template("prediction-user.html", UL = usernameToLoad, MDTL = matchDayToLoad, BP = basePredictionUser, GMD = gamesMacthDaySelected)
    else:
        basePredictionUser = basePredictionUser[0]
        gamesMacthDaySelected = getGames(matchDayToLoad)

        predictsToPass = []
        for pred in basePredictionUser:
            predictsToPass.append(pred)

        return render_template("prediction-user.html", UL = usernameToLoad, MDTL = matchDayToLoad, BP = predictsToPass, GMD = gamesMacthDaySelected)
    

@app.route("/loadClassification", methods=["POST"])
def loadClassification():

    dataMD = request.json["newVal"]

    if dataMD == "general":
        cur = mysql.connection.cursor()
        cur.execute("SELECT username, points FROM users ORDER BY points DESC")
        usersToLoad = cur.fetchall()

        cur = mysql.connection.cursor()
        cur.execute("SELECT matchday FROM matchdaydata WHERE type = 0")
        dataMD = cur.fetchall()[0][0]

    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT username, points FROM points WHERE matchday=%s ORDER BY points DESC", [dataMD])
        usersToLoad = cur.fetchall()


    return render_template("table_classification.html", usersToLoad = usersToLoad, MD_Home = dataMD)
