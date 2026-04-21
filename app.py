from flask import Flask, session, url_for, redirect, request, render_template
import secrets
import sqlite3
import requests
from werkzeug.security import check_password_hash, generate_password_hash

db = sqlite3.connect("verbruikData.db", check_same_thread=False)

app = Flask(__name__)
app.secret_key = secrets.token_hex()

#index
@app.route("/")
def index():
    #ga naar home wanneer username in sessie zit
    if 'user' in session:
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))

#login pagina
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        #username = db.execute("SELECT user_name FROM users WHERE user_name = ?", (request.form['username'],)).fetchone()
        password = db.execute("SELECT user_password FROM users WHERE user_name = ?", (request.form['username'],)).fetchone()
        #auth = db.execute("SELECT * FROM users WHERE user_name = ? AND user_password = ?", (request.form['username'], password)).fetchone()
        try:
            auth = check_password_hash(password[0], request.form['password'])
        except:
            auth = False

        #check voor juiste login gegevens
        if auth == True and request.form['btn'] == "Inloggen":
            #voeg user id aan sessie toe
            session['user'] = db.execute("SELECT user_id FROM users WHERE user_name = ?", (request.form['username'],)).fetchone()[0]
            return redirect(url_for("index"))   
        elif request.form['username'] != "" and request.form['password'] != "" and request.form['btn'] == "Aanmelden":

            #check of username al in database staat
            if password == None:
                # Voeg nieuwe gebruiker toe aan database
                db.execute(
                            "INSERT INTO users (user_name, user_password) VALUES (?, ?)", 
                            (request.form['username'], generate_password_hash(request.form['password']))
                           )
                db.commit()
                #zeg dat account is aangemaakt
                return render_template("login.html", status="Account aangemaakt!")
            else:
                #anders zeg dat account al bestaat
                return render_template("login.html", status="Username al in gebruik!")
            
    #weergeef inlog pagina    
    return render_template("login.html")

#home pagina
@app.route("/home", methods=['GET', 'POST'])
def home():
    #check voor username in sessie
    if 'user' in session:
        return render_template("dashboard.html")
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#logboek pagina
@app.route("/log", methods=['GET', 'POST'])
def log():
    #check voor username in sessie
    if 'user' in session:
        return render_template("log.html")
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#autos pagina
@app.route("/cars", methods=['GET', 'POST'])
def cars():
    #check voor username in sessie
    if 'user' in session:

        message = ""
        #als er op toevoegen word geklikt
        if request.method == 'POST':

            license_plate = str(request.form['license_plate']).upper()

            carInfo = requests.get(
                                    url="https://opendata.rdw.nl/resource/m9d7-ebf2.json",
                                    params={"$query":f"SELECT merk, handelsbenaming WHERE kenteken = '{license_plate}'"}
                                   )
            carFuel = requests.get(
                                    url="https://opendata.rdw.nl/resource/8ys7-d773.json",
                                    params={"$query":f"SELECT brandstof_omschrijving WHERE kenteken = '{license_plate}'"}
                                   )

            if carInfo.status_code != 200 or carFuel.status_code != 200 or len(carInfo.json()) == 0 or len(carFuel.json()) == 0:
                message = "Er is een fout opgetreden bij het ophalen van de gegevens!"
            elif db.execute("SELECT car_licenseplate FROM cars WHERE car_licenseplate = ?", (license_plate,)).fetchone():
                message = "Auto is al een keer toegevoegd!"
            else:
                for car in carInfo.json():
                    carName = car['merk'].lower().capitalize() + " " + car['handelsbenaming'].lower().capitalize()
                for fuel in carFuel.json():
                    fuelType = fuel['brandstof_omschrijving'].lower().capitalize()
        
                db.execute("INSERT INTO cars (user_id, car_name, car_licenseplate, car_meters, car_fueltype, car_maxliter) VALUES (?, ?, ?, ?, ?, ?)", 
                        (session['user'], carName, license_plate, request.form["kilometers"], fuelType, request.form["max_liters"]))
                db.commit()

        #laat lijst zien op pagina
        cars = db.execute("SELECT * FROM cars WHERE user_id = ?", (session['user'],)).fetchall()

        html = ""
        for car in cars:
            html += f"""
            <tr>
            <td>{car[2]}</td>
            <td>{car[3]}</td>
            <td>{car[4]}</td>
            <td>{car[5]}</td>
            <td>{car[7]}</td>
            <td>
                <form method='post' action='/deletecar'>
                    <input type='hidden' name='car_id' value='{car[0]}'><button class='btn' type='submit'>Verwijderen</button>
                </form>
            </td>
            </tr>
            """
        return render_template("cars.html", table=html, message=message)
    else:
        #anders terug naar login
        return redirect(url_for("login"))

@app.route("/deletecar", methods=['POST'])
def deletecar():
    if 'user' in session:
        car_id = request.form['car_id']
        db.execute("DELETE FROM cars WHERE car_id = ? AND user_id = ?", (car_id, session['user']))
        db.commit()
        return redirect(url_for("cars"))
    else:
        #anders terug naar login
        return redirect(url_for("login"))

#pagina voor uitloggen
@app.route("/logout")
def logout():
    if 'user' in session:
        #haal username uit sessie
        session.pop('user')

        #ga terug naar index
        return redirect(url_for("index"))
    else:
        #anders terug naar login
        return redirect(url_for("login"))   

if __name__ == "__main__":
    app.run(debug=True)