from flask import session, url_for, redirect, render_template
import sqlite3
import datetime

db = sqlite3.connect("db/verbruikData.db", check_same_thread=False)

def log_get(request=None):

    cars = db.execute("SELECT car_name, car_id, car_kilometers FROM cars WHERE user_id = ?", (session['user'],)).fetchall()

    car = request.form['car_select'] if request and 'car_select' in request.form else None

    #global carId

    if car:
        carId = db.execute("SELECT car_id FROM cars WHERE car_name = ? AND user_id = ?", (car, session['user'])).fetchone()[0]
    elif cars:
        car = cars[0][0]
        carId = cars[0][1]
    else:
       return redirect(url_for("cars"))

    maxDate = datetime.date.today()
    minDate = db.execute("SELECT MIN(fuelmoment_date) FROM refuels WHERE car_id = ?", (carId,)).fetchone()[0]
    startDate = request.form['start_date'] if request and 'start_date' in request.form else maxDate

    refuels = db.execute("""select fuelmoment_id, fuelmoment_date, fuelmoment_liters, fuelmoment_usage, fuelmoment_type 
                         from refuels 
                         where car_id = ?
                         and fuelmoment_date between ? and ?
                         order by fuelmoment_date desc""",
                         (carId, minDate, startDate)).fetchall()

    return render_template("log.html", 
                           refuels=refuels, 
                           cars=cars,
                           minDate=minDate,
                           maxDate=maxDate,
                           selectedDate=startDate,
                           selectedCar=car)

def log_post(request):
    return log_get(request)

def deleteRefuel_post(request):
    refuel_id = request.form['refuel_id']
    db.execute("DELETE FROM refuels WHERE fuelmoment_id = ? AND user_id = ?", (refuel_id, session['user']))
    db.commit()
    return redirect(url_for("log"))