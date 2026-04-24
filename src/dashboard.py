from datetime import datetime
from flask import session, url_for, redirect, render_template
import sqlite3
import datetime

db = sqlite3.connect("db/verbruikData.db", check_same_thread=False)

def list_fuels(auto):
    fuel = db.execute("SELECT car_fueltype FROM cars WHERE car_name = ? AND user_id = ?", (auto, session['user'])).fetchone()[0]

    if fuel == "Benzine":
        return ["Euro 95", "Euro 98", "Super Plus"]
    elif fuel == "Diesel":
        return ["Diesel", "Biodiesel"]
    elif fuel == "LPG":
        return ["LPG"]


def dashboard_get(request):
    cars = db.execute("SELECT car_name, car_id, car_kilometers FROM cars WHERE user_id = ?", (session['user'],)).fetchall()

    global car, carId
    car = cars[0][0] if cars else None
    carId = cars[0][1] if cars else None
    kilometers = cars[0][2] if cars else None

    minDate = db.execute("SELECT MIN(fuelmoment_date) FROM refuels WHERE car_id = ?", (carId,)).fetchone()[0] if carId else None
    maxDate = datetime.date.today()

    if minDate == None:
        minDate = maxDate

    return render_template("dashboard.html", 
                    cars=cars, 
                    fuelTypes=list_fuels(car), 
                    minDate=minDate, 
                    maxDate=maxDate,
                    maxKilometers=kilometers
                    )

def dashboard_post(request):
    global car, carId
    car = request.form['car_select']
    carId = db.execute("SELECT car_id FROM cars WHERE car_name = ? AND user_id = ?", (car, session['user'])).fetchone()[0]
    
    return dashboard_get(request)

def refuel_post(request):
    
    date = request.form['refuel_date']
    newKilometers = int(request.form['kilometers'])
    oldKilometers = int(db.execute("SELECT car_kilometers FROM cars WHERE car_id = ?", (carId,)).fetchone()[0])
    fueltType = request.form['fuel_type']
    fuelLiters = int(request.form['refuel_liters'])
    fuelUsage = f"1:{str((newKilometers - oldKilometers) / fuelLiters)}"

    if carId:
        print("Toegevoegd")
        db.execute("INSERT INTO refuels (car_id, user_id, fuelmoment_liters, fuelmoment_date, fuelmoment_type, fuelmoment_usage) VALUES (?, ?, ?, ?, ?, ?)",
                   (carId, session['user'], fuelLiters, date, fueltType, fuelUsage))
        db.commit()

    return redirect(url_for("dashboard"))