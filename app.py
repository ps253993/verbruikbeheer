from flask import Flask, url_for, redirect, request
import secrets

from src.auth import auth_get, login_post, signup_post, logout_post, authicated
from src.car_management import cars_get, addcar_post, deletecar_post
from src.add_refuel import refuel_get, refuel_post
from src.list_dashboard import dashboard_get, dashboard_post
from src.log import log_get, log_post


app = Flask(__name__)
app.secret_key = secrets.token_hex()

#index
@app.route("/")
def index():
    #ga naar home wanneer username in sessie zit
    if authicated():
        return redirect(url_for("dashboard"))
    else: 
        return redirect(url_for("login"))
    
#login pagina
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return auth_get(request)
    if request.method == 'POST':
        return login_post(request)

@app.route("/signup", methods=['POST'])
def signup():
    return signup_post(request)

#home pagina
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    #check voor username in sessie
    if authicated():
        if request.method == 'GET':
            return dashboard_get(request)
        if request.method == 'POST':
            return dashboard_post(request)
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/add_refuel", methods=['GET', 'POST'])
def add_refuel():
    #check voor username in sessie
    if authicated():
        if request.method == 'POST':
            return refuel_post(request)
    else:
        return redirect(url_for("login"))

#logboek pagina
@app.route("/log", methods=['GET', 'POST'])
def log():
    #check voor username in sessie
    if authicated():
        if request.method == 'GET':
            return log_get(request)
        if request.method == 'POST':
            return log_post(request)
    else:
        return redirect(url_for("login"))

#autos pagina
@app.route("/cars", methods=['GET'])
def cars():
    #check voor username in sessie
    if authicated():
        return cars_get(request)
    else:
        return redirect(url_for("login"))
        
@app.route("/cars/addcar", methods=['POST'])
def addcar():
    #check voor username in sessie
    if authicated():
        return addcar_post(request)
    else:
        return redirect(url_for("login"))

@app.route("/cars/deletecar", methods=['POST'])
def deletecar():
    if authicated():
        return deletecar_post(request)
    else:
        return redirect(url_for("login"))

#pagina voor uitloggen
@app.route("/logout")
def logout():
    if authicated():
        return logout_post(request)
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)