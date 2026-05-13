from flask import session, url_for, redirect, render_template, send_file, after_this_request
import sqlite3
import xlsxwriter
import csv
import os
from tempfile import TemporaryDirectory
import datetime
import io

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

    print(cars)

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

fieldnames = ["Date", "Car_Licenseplate", "Car_Name", "Fuel_Type", "Fuel_Liters", "Fuel_Usage"]

def export_xlsx(data, minDate, maxDate):
    tempDir = TemporaryDirectory()
    filePath = f"{tempDir.name}/exportId{session['user']}.xlsx"
    workbook = xlsxwriter.Workbook(filePath)
    worksheet = workbook.add_worksheet()

    for row, fieldName in enumerate(fieldnames):
        worksheet.write(0,row,fieldName)

    for row, (date, carLicenseplate, carName, fuelType, fuelLiters, fuelUsage) in enumerate(data):
        row += 1
        worksheet.write(row,0,date)
        worksheet.write(row,1,carLicenseplate)
        worksheet.write(row,2,carName)
        worksheet.write(row,3,fuelType)
        worksheet.write(row,4,fuelLiters)
        worksheet.write(row,5,fuelUsage)

    workbook.close()

    with open(filePath, "rb") as f:
            file_bytes = f.read()
            
    @after_this_request
    def cleanup(response):
        print("cleanup")
        tempDir.cleanup()
        return response

    downloadName = f"Export_{minDate}_{maxDate}.xlsx"

    return send_file(path_or_file=io.BytesIO(file_bytes),as_attachment=True,download_name=downloadName)

def export_csv(data, minDate, maxDate):
    tempDir = TemporaryDirectory()
    dataList = []

    filePath =  filePath = os.path.join(tempDir.name, f"exportId{session['user']}.csv")

    for (date, carLicenseplate, carName, fuelType, fuelLiters, fuelUsage) in data:
        dataList.append({"Date": date, 
                        "Car_Licenseplate": carLicenseplate, 
                        "Car_Name": carName,
                        "Fuel_Type": fuelType,
                        "Fuel_Liters": fuelLiters,
                        "Fuel_Usage": fuelUsage,
                        })

    with open(filePath, 'x', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataList)


    with open(filePath, "rb") as f:
            file_bytes = f.read()


    @after_this_request
    def cleanup(response):
        print("cleanup")
        tempDir.cleanup()
        return response

    downloadName = f"Export_{minDate}_{maxDate}.csv"

    return send_file(path_or_file=io.BytesIO(file_bytes),as_attachment=True,download_name=downloadName)


def export_post(request):

    minDate = request.form["mindate"]
    maxDate = request.form["maxdate"]

    data = db.execute("""
                        select r.fuelmoment_date, 
                        c.car_name, 
                        c.car_licenseplate, 
                        r.fuelmoment_type, 
                        r.fuelmoment_liters, 
                        r.fuelmoment_usage 
                        from refuels r, cars c
                        where c.car_id = r.car_id
                        and r.car_id = ?
                        and fuelmoment_date between ? and ?
                        order by fuelmoment_date desc""", 
                        (carId, minDate, maxDate)).fetchall()

    if request.form["export_format"] == "xlsx":
        return export_xlsx(data, minDate, maxDate)
    elif request.form["export_format"] == "csv":
        return export_csv(data, minDate, maxDate)