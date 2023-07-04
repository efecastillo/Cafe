import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# The local python scripts
from helpers import apology, login_required, price, username, idn

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cafe.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """This is the welcoming site, must show some summary"""
    query = db.execute("SELECT capacity FROM users JOIN prensas ON prensas.owner_id = users.id ")
    prensa_info=""
    if query:
        prensa_info=query[0]["capacity"]

    return render_template("index.html", username = username(session["user_id"]) , french = prensa_info)
                           


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        testing = db.execute("SELECT * FROM users WHERE username=?", username)
        if not username:
            return apology("username can't be blank ><")
        if testing:
            return apology("username already in use!")
        password = request.form.get("password")
        password_copy = request.form.get("confirmation")
        if not password or password != password_copy or not password_copy:
            return apology("Password invalid! Double check.")

        #Add to the user table
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/bolsa", methods=["GET", "POST"])
@login_required
def bolsa():
    """Registrar bolsa de cafe"""
    if request.method=="POST":
        origin = request.form.get("origin")
        price = request.form.get("price")
        toaster = request.form.get("toaster")
        grams = request.form.get("grams")
         
        #Checar que recibe un numero como precio
        if not price.isdigit():
            return apology("Precio debe ser un numero entero, por ejemplo 2500")
        #Checar que recibe un numero como gramos
        if not grams.isdigit():
            return apology("Gramos debe ser un numero entero, por ejemplo 1000")
        #Checar que es mayor que 1000
        price = int(price)
        if price < 1000:
            return apology("Precio esta raro")
        
        # Ojo con el uso de datetime aqui
        db.execute("INSERT INTO bolsas (user_id, origin, toaster, price, grams, date, active) VALUES (?,?,?,?,?,?,?)", session["user_id"], origin, toaster, int(price), int(grams), datetime.datetime.now(), "YES")
        return redirect("/")
    else:
        return render_template("bolsa.html")

@app.route("/prensa", methods=["GET", "POST"])
@login_required
def prensa():
    """Registrar prensa francesa"""
    if request.method=="POST":
        capacity = request.form.get("capacity")
         
        #Checar que recibe un numero como precio
        if not capacity.isdigit():
            return apology("Volumen debe ser un numero entero, por ejemplo 600")
        #Checar que es mayor que 1000
        capacity = int(capacity)
        if capacity <= 0:
            return apology("Capacidad esta rara")
        
        # Ojo con el uso de datetime aqui
        db.execute("INSERT INTO prensas (owner_id, capacity) VALUES (?,?)", session["user_id"], capacity)
        return redirect("/")
    else:
        return render_template("prensa.html")

@app.route("/ronda", methods=["GET", "POST"])
@login_required
def ronda():
    """Registrar ronda de cafe"""
    
    #Creamos todas las listas necesarias para las opciones
    db_miembros = db.execute("SELECT username FROM users");
    miembros = [entry["username"] for entry in db_miembros]
    prensas = db.execute("SELECT username, capacity, owner_id, prensas.id FROM users JOIN prensas ON prensas.owner_id = users.id ORDER BY prensas.id")
    bolsas = db.execute("SELECT origin, toaster, id, user_id FROM bolsas ORDER BY id")
    

    if request.method=="POST":
        #Aca se asume que da los ID de las cosas
        prensa = request.form.get("prensa")
        bolsa = request.form.get("bolsa")

        #Quienes tomaron
        tomadores=[]
        for miembro in miembros:
            if request.form.get(miembro, default=False, type=bool):
                tomadores.append(miembro)

        if len(tomadores) == 0:
            return apology("Tiene que escoger almenos un miembro!")
        
        if not prensa:
            return apology("Tiene que escoger prensa")

        if not bolsa:
            return apology("Tiene que escoger bolsa")

        #Procesar esta info y botar precios
        costo = price(len(tomadores), prensas[prensa]["capacity"], bolsas[bolsa]["price"], bolsas[bolsa]["grams"])
        
        #Agregar la ronda
        db.execute("INSERT INTO rondas VALUES (?,?,?,?) ", prensa, bolsa, costo, datetime.datetime.now())
        ronda_id = db.execute("SELECT COUNT(*) from rondas")[0]["COUNT(*)"]
        #Agregar las incidencias 
        for miembro in miembros:
            db.execute("INSERT INTO incidencias (ronda_id, user_id) VALUES (?,?,?,?) ", ronda_id, idn(miembro))  

        #Crear facturas en un csv TODO
        
        return redirect("/")
    else:
        return render_template("ronda.html", prensas = prensas, bolsas = bolsas, miembros = miembros)

@app.route("/history")
@login_required
def history():
    """Mostrar historial reciente de rondas de cafe"""
    return apology("TODO")




@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        queried_symbol = request.form.get("symbol")
        info = lookup(queried_symbol)
        if info == None:
            return apology("Symbol out of whack.")
        else:
            name = info["name"]
            price = info["price"]
            symbol = info["symbol"]

        return render_template("quoted.html", name = name, price = usd(price), symbol = symbol)
    else:
        return render_template("quote.html")

