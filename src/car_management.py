from flask import session, render_template
import sqlite3
import requests

db = sqlite3.connect("db/verbruikData.db", check_same_thread=False)

def get_rdwData(license_plate):
    carInfo = requests.get(
                            url="https://opendata.rdw.nl/resource/m9d7-ebf2.json",
                            params={"$query":f"SELECT merk, handelsbenaming WHERE kenteken = '{license_plate}'"}
                            )
    carFuel = requests.get(
                            url="https://opendata.rdw.nl/resource/8ys7-d773.json",
                            params={"$query":f"SELECT brandstof_omschrijving WHERE kenteken = '{license_plate}'"}
                            )

    if carInfo.status_code != 200 or carFuel.status_code != 200 or len(carInfo.json()) == 0 or len(carFuel.json()) == 0:
        return None
    else:
        for car in carInfo.json():
            carName = car['merk'].lower().capitalize() + " " + car['handelsbenaming'].lower().capitalize()
        for fuel in carFuel.json():
            fuelType = fuel['brandstof_omschrijving'].lower().capitalize()
        
        return (carName, fuelType)

def cars_get(request, message=""):
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
            <form method='post' action='/cars/deletecar'>
                <input type='hidden' name='car_id' value='{car[0]}'><button class='btn' type='submit'>Verwijderen</button>
            </form>
        </td>
        </tr>
        """
    return render_template("cars.html", table=html, message=message)

def addcar_post(request):
    license_plate = str(request.form['license_plate']).upper()
    rdwData = get_rdwData(license_plate)
    message = ""

    if rdwData == None:
        message = "Er is een fout opgetreden bij het ophalen van de gegevens!"
    elif db.execute("SELECT car_licenseplate FROM cars WHERE car_licenseplate = ?", (license_plate,)).fetchone():
        message = "Auto is al een keer toegevoegd!"

    db.execute("INSERT INTO cars (user_id, car_name, car_licenseplate, car_kilometers, car_fueltype, car_maxliter) VALUES (?, ?, ?, ?, ?, ?)", 
            (session['user'], rdwData[0], license_plate, request.form["kilometers"], rdwData[1], request.form["max_liters"]))
    db.commit()

    return cars_get(request, message)

def deletecar_post(request):
    car_id = request.form['car_id']
    db.execute("DELETE FROM cars WHERE car_id = ? AND user_id = ?", (car_id, session['user']))
    db.commit()
    return cars_get(request)