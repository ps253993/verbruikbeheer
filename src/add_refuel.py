from flask import Flask, session, url_for, redirect, request, render_template
import secrets
import sqlite3
import requests
from werkzeug.security import check_password_hash, generate_password_hash

db = sqlite3.connect("verbruikData.db", check_same_thread=False)

def refuel_get(request):
    return render_template("dashboard.html")

def refuel_post(request):
    cars = db.execute("SELECT car_name FROM cars WHERE user_id = ?", (session['user'],)).fetchall()
    
    cars_html = ""
    for car in cars:
        cars_html += f"<option name='car_select' value='{car[0]}'>{car[0]}</option>"

    if request.method == 'POST':
        print(request.form['car_select'])

    return render_template("dashboard.html", cars=cars_html)

