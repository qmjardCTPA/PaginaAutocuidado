from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave__para_autocuidado")

# Conexión a mongo
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["autocuidado"]
users_collection = db["usuarios"]

#dbpassw: f2R8wiTNztgN6fpr jaredlcctpa_db_user

bcrypt = Bcrypt(app)


@app.route("/")
def home():
    if "user" in session:
        return render_template("index.html", username=session["user"])
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = users_collection.find_one({"username": username})

        if user and bcrypt.check_password_hash(user["password"], password):
            session["user"] = username
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("home"))
        else:
            flash("Usuario o contraseña incorrectos.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if users_collection.find_one({"username": username}):
            flash("El usuario ya existe. Intenta con otro nombre.", "error")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        users_collection.insert_one({
            "username": username,
            "password": hashed_password
        })

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))

def handler(event, context):
    return app(event, context)


