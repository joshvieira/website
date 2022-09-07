from app import app
from flask import render_template


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/optimal-betting-when-odds-are-random")
def hello():
    return render_template("optimal-betting-when-odds-are-random.html")
