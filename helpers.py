import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import math

from cs50 import SQL
from flask import redirect, render_template, session
from functools import wraps

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cafe.db")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def price(n, v, p, q):
    """
    Determina el precio de una tomada.
    n -> Numero de personas
    v -> volumen de prensa
    p -> precio de la bolsa
    q -> peso de la bolsa
    """
    app_fee = 100
    prensa_fee = 0
    gramos_cafe = int((v*60)/1000)
    precio_gramo = int(p/q)

    costo_taza_cafe = int((gramos_cafe * precio_gramo) / n);
    #Redondeando hacia arriba hasta el proximo multiplo de 50 CLP
    costo_taza_cafe = math.ceil( costo_taza_cafe / 50 ) * 50;
    #Sumas
    costo_taza_cafe = costo_taza_cafe + prensa_fee + app_fee

    return costo_taza_cafe

def username(n):
    query = db.execute("SELECT username FROM users WHERE id=?", n)
    return query[0]["username"]


def idn(name):
    query = db.execute("SELECT * FROM users WHERE username=?", name)
    return query[0]["id"]
