from flask import Flask, session, url_for, redirect, request
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex()

#test username en password
user = "test"
password = "Password01"

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
        if request.form['username'] == user and request.form["password"] == password: 
            #voeg username aan sessie toe
            session['username'] = request.form['username']
            return redirect(url_for("index"))
        else:
            return "wrong login"
    #weergeef inlog pagina    
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=text name=password>
            <p><input type=submit value=Login>
        </form>
    '''
#home pagina
@app.route("/home")
def home():
    #check voor username in sessie
    if 'username' in session:
        return "home pagina van "+session["username"]
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#logboek pagina
@app.route("/logboek")
def logboek():
    #check voor username in sessie
    if 'username' in session:
        return "logboek pagina van "+session["username"]
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#autos pagina
@app.route("/autos")
def autos():
    #check voor username in sessie
    if 'username' in session:
        return "autos pagina van "+session["username"]
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#pagina voor uitloggen
@app.route("/logout")
def logout():
    #haal username uit sessie
    session.pop('username')
    #ga terug naar index
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)