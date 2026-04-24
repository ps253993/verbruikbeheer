from flask import Flask, session, url_for, redirect, request, render_template
import secrets
import sqlite3
import requests
from werkzeug.security import check_password_hash, generate_password_hash

db = sqlite3.connect("db/verbruikData.db", check_same_thread=False)

def log_get(request):
    return render_template("log.html")

def log_post(request):
    pass