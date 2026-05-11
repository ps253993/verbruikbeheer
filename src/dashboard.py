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


def dashboard_get(request = None):
    cars = db.execute("SELECT car_name, car_id, car_kilometers FROM cars WHERE user_id = ?", (session['user'],)).fetchall()

    car = request.form['car_select'] if request and 'car_select' in request.form else None

    global carId, avrUsage

    if car:
        carId = db.execute("SELECT car_id FROM cars WHERE car_name = ? AND user_id = ?", (car, session['user'])).fetchone()[0]
        kilometers = db.execute("SELECT car_kilometers FROM cars WHERE car_id = ?", (carId,)).fetchone()[0]
    elif cars:
        car = cars[0][0]
        carId = cars[0][1]
        kilometers = cars[0][2]
    else:
       return redirect(url_for("cars"))

    minDate = db.execute("SELECT MIN(fuelmoment_date) FROM refuels WHERE car_id = ?", (carId,)).fetchone()[0] if carId else None
    maxDate = datetime.date.today()

    lastRefuelDate = db.execute("SELECT fuelmoment_date FROM refuels WHERE car_id = ? ORDER BY fuelmoment_date DESC LIMIT 1", (carId,)).fetchone()
    lastUsage = db.execute("SELECT fuelmoment_usage FROM refuels WHERE car_id = ? ORDER BY fuelmoment_date DESC LIMIT 1", (carId,)).fetchone()
    avrUsage = db.execute("SELECT AVG(CAST(SUBSTR(fuelmoment_usage, 3) AS FLOAT)) FROM refuels WHERE car_id = ?", (carId,)).fetchone()[0]

    fuelMoments = db.execute("SELECT fuelmoment_date, fuelmoment_usage FROM refuels WHERE car_id = ? ORDER BY fuelmoment_date ASC", (carId,)).fetchall()
    fuelDates = [str(moment[0]) for moment in fuelMoments]
    fuelUsages = [float(moment[1].replace("1:","")) for moment in fuelMoments]

    print(fuelDates, fuelUsages)

    if minDate == None:
        minDate = maxDate

    return render_template("dashboard.html", 
                    cars=cars, 
                    fuelTypes=list_fuels(car), 
                    minDate=minDate, 
                    maxDate=maxDate,
                    maxKilometers=kilometers,
                    lastRefuelDate=lastRefuelDate[0] if lastRefuelDate else None,
                    lastUsage=lastUsage[0] if lastUsage else None,
                    avrUsage= "1:"+str(round(avrUsage, 1)) if avrUsage else None,
                    activeCar=car,
                    fuelDates=fuelDates,
                    fuelUsages=fuelUsages
                    )

def dashboard_post(request):
    return dashboard_get(request)

def refuel_post(request):
    
    date = request.form['refuel_date']
    newKilometers = int(request.form['kilometers'])
    oldKilometers = int(db.execute("SELECT car_kilometers FROM cars WHERE car_id = ?", (carId,)).fetchone()[0])
    fueltType = request.form['fuel_type']
    fuelLiters = int(request.form['refuel_liters'])
    fuelUsage = f"1:{str(round((newKilometers - oldKilometers) / fuelLiters, 1))}"

    if carId:
        print("Toegevoegd")
        db.execute("INSERT INTO refuels (car_id, user_id, fuelmoment_liters, fuelmoment_date, fuelmoment_type, fuelmoment_usage) VALUES (?, ?, ?, ?, ?, ?)",
                   (carId, session['user'], fuelLiters, date, fueltType, fuelUsage))
        if avrUsage:
                db.execute("UPDATE cars SET car_kilometers = ?, car_avrfuelusage = ? WHERE car_id = ?", 
                        (newKilometers, "1:"+str(round(avrUsage, 1)), carId))
        else:
            db.execute("UPDATE cars SET car_kilometers = ?, car_avrfuelusage = ? WHERE car_id = ?", 
                        (newKilometers, fuelUsage, carId))
        db.commit()

    return redirect(url_for("dashboard"))