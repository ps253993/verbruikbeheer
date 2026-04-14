from flask import Flask, session, url_for, redirect, request, render_template
import secrets
import sqlite3
import hashlib

db = sqlite3.connect("verbruikData.db", check_same_thread=False)

app = Flask(__name__)

app.secret_key = secrets.token_hex()

def check_user(username, password):
    #check of username en password in database staan
    pswrd = hashlib.sha256(password.encode()).hexdigest()
    user = db.execute("SELECT * FROM users WHERE user_name = ? AND user_password = ?", (username, pswrd)).fetchone()

    if user:
        return True
    else:
        return False

#index
@app.route("/")
def index():
    #ga naar home wanneer username in sessie zit
    if 'username' in session:
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))

#login pagina
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        #check voor juiste login gegevens
        if check_user(request.form['username'], request.form['password']) and request.form['btn'] == "login": 
            #voeg username aan sessie toe
            session['username'] = request.form['username']
            return redirect(url_for("index"))
        elif request.form['username'] != "" and request.form['password'] != "" and request.form['btn'] == "signup":
            #check of username al in database staat
            user = db.execute("SELECT user_name FROM users WHERE user_name = ?", (request.form['username'],)).fetchone()
        
            if user == None:
                #hash wachtwoord
                pswrd = hashlib.sha256(request.form['password'].encode()).hexdigest()
                # Voeg nieuwe gebruiker toe aan database
                db.execute("INSERT INTO users (user_name, user_password) VALUES (?, ?)", (request.form['username'], pswrd))
                db.commit()
                #zeg dat account is aangemaakt
                return render_template("login.html", status="Account aangemaakt!")
            else:
                #anders zeg dat account al bestaat
                return render_template("login.html", status="Username al in gebruik!")
            
    #weergeef inlog pagina    
    return render_template("login.html")

#home pagina
@app.route("/home")
def home():
    #check voor username in sessie
    if 'username' in session:
        return render_template("dashboard.html")
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#logboek pagina
@app.route("/logboek")
def logboek():
    #check voor username in sessie
    if 'username' in session:
        return render_template("log.html")
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#autos pagina
@app.route("/autos")
def autos():
    #check voor username in sessie
    if 'username' in session:
        return render_template("autos.html")
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#pagina voor uitloggen
@app.route("/logout")
def logout():
    if 'username' in session:
        #haal username uit sessie
        session.pop('username')
        #ga terug naar index
        return redirect(url_for("index"))
    else:
        #anders terug naar login
        return redirect(url_for("login"))   

if __name__ == "__main__":
    app.run(debug=True)