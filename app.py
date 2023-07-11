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
    """Bienvenida"""
    query = db.execute("SELECT capacity FROM users JOIN prensas ON prensas.owner_id = users.id WHERE users.id=?", session["user_id"])
    queri = db.execute("SELECT origin, toaster, bolsas.id AS numero FROM users JOIN bolsas ON bolsas.user_id = users.id WHERE users.id = ?", session["user_id"])
    prensa_info=""
    bolsa_info=""
    if query:
        prensa_info=query[0]["capacity"]
    if queri:
        bolsa_info = queri

    # Mostrar las ultimas transacciones de todo el club
    rondas = db.execute("SELECT origin, toaster, cost, rondas.date AS fecha FROM bolsas JOIN rondas ON bolsas.id = rondas.bolsa_id ORDER BY rondas.date DESC LIMIT 5")

    return render_template("index.html", username = username(session["user_id"]) , french = prensa_info, rondas = rondas, bolsas = bolsa_info)
                           


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
    prensas = db.execute("SELECT username, capacity, owner_id, prensas.id AS prensa_id FROM users JOIN prensas ON prensas.owner_id = users.id ORDER BY prensas.id")
    bolsas = db.execute("SELECT * FROM bolsas ORDER BY id")
    

    if request.method=="POST":
        #Aca se asume que da los ID de las cosas
        prensa = int( request.form.get("prensa"))
        bolsa = int( request.form.get("bolsa") )

        #Quienes tomaron
        tomadores=[]
        for miembro in miembros:
            if request.form.get(miembro, default=False, type=bool):
                tomadores.append(miembro)

        if len(tomadores) == 0:
            return apology("Tiene que escoger almenos un miembro!")

        #Agregar invitado
        if request.form.get("guest"):
            invitador = request.form.get("guest")
            cantidad = request.form.get("cantidad")
            cantidad = int(cantidad)
            for i in range(cantidad):
                tomadores.append(invitador)

        #Procesar esta info y botar precios
        costo = price(len(tomadores), prensas[prensa-1]["capacity"], bolsas[bolsa-1]["price"], bolsas[bolsa-1]["grams"])
        
        #Agregar la ronda
        db.execute("INSERT INTO rondas (prensa_id, bolsa_id, cost, date) VALUES (?,?,?,?) ", prensa, bolsa, costo, datetime.datetime.now())
        ronda_id = db.execute("SELECT COUNT(*) from rondas")[0]["COUNT(*)"]
        #Agregar las incidencias 
        for tomador in tomadores:
            db.execute("INSERT INTO incidencias (ronda_id, user_id) VALUES (?,?) ", ronda_id, idn(tomador))  

        return redirect("/")
    else:
        return render_template("ronda.html", prensas = prensas, bolsas = bolsas, miembros = miembros)

@app.route("/factura")
@login_required
def factura():
    """Mostrar historial reciente de rondas de cafe"""
    bolsas = db.execute("SELECT origin, toaster, price AS precio, date AS fecha, grams AS gramos FROM bolsas JOIN users ON bolsas.user_id = users.id ORDER BY fecha DESC WHERE users.id=?", session["user_id"])
    tazas = db.execute("SELECT origin, toaster, cost, rondas.date AS fecha FROM rondas JOIN bolsas ON rondas.bolsa_id = bolsas.id JOIN incidencias ON incidencias.ronda_id = rondas.id JOIN users ON incidencias.user_id = users.id ORDER BY fecha DESC WHERE users.id = ? ", session["user_id"])

    bono = db.execute("SELECT SUM(price) FROM bolsas WHERE user_id=?", session["user_id"])[0]["SUM(price)"]
    total_tazas = db.execute("SELECT SUM(cost) FROM rondas JOIN incidencias ON incidencias.ronda_id = rondas.id WHERE incidencias.user_id = ? ", session["user_id"])[0]["SUM(cost)"]
    total_final = int(total_tazas)-int(bono)
    return render_template("factura.html", bolsas = bolsas, tazas = tazas, username = username(session["user_id"]), bono = bono, total_tazas = total_tazas, total_final = total_final )


@app.route("/bolsas")
@login_required
def bolsas():
    """Ver todas las bolsas disponibles"""
    bolsas = db.execute("SELECT origin, toaster, price AS precio, date AS fecha, users.id AS miembro, active, grams AS gramos FROM bolsas JOIN users ON bolsas.user_id = users.id ")

    bolsas_activas = []
    bolsas_pasadas = []
    for bolsa in bolsas:
        if bolsa["active"]=="YES":
            bolsas_activas.append(bolsa)
        else:
            bolsas_pasadas.append(bolsa)

    return render_template("bolsas.html", activas = bolsas_activas, pasadas = bolsas_pasadas)




@app.route("/cerrar", methods=["GET", "POST"])
@login_required
def cerrar():
    """Cerrar bolsa de cafe"""
    cafe = int(request.form.get("cafe"))
    
    db.execute("UPDATE bolsas SET active = 'NO' WHERE id=? ", cafe)
    return redirect("/")
