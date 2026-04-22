from flask import session, url_for, redirect, render_template
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

db = sqlite3.connect("db/verbruikData.db", check_same_thread=False)

def auth_get(request,status=""):
    return render_template("login.html", status=status)

def login_post(request):
    password = db.execute("SELECT user_password FROM users WHERE user_name = ?", (request.form['username'],)).fetchone()
    
    if password == None or check_password_hash(password[0], request.form['password']) == False:
        return auth_get(request, status="Foutieve login gegevens!")

    # user is altijd ingellogd hier
    session['user'] = db.execute("SELECT user_id FROM users WHERE user_name = ?", (request.form['username'],)).fetchone()[0]
    return redirect(url_for("index"))   

def signup_post(request):
    user =  db.execute("SELECT * FROM users WHERE user_name = ?", (request.form['username'],)).fetchone()

    #check of username al in database staat
    if user == None:
        
        # Voeg nieuwe gebruiker toe aan database
        db.execute(
                    "INSERT INTO users (user_name, user_password) VALUES (?, ?)", 
                    (request.form['username'], generate_password_hash(request.form['password']))
                    )
        db.commit()

        #zeg dat account is aangemaakt
        return auth_get(request, status="Account aangemaakt!")
    else:
        #anders zeg dat account al bestaat
        return auth_get(request, status="Gebruikersnaam al in gebruik!")
    
def logout_post(request):    
    session.pop('user', None)
    return auth_get(request)

def authicated(request):
    if 'user' in session:
        return True
    else:
        return auth_get(request)