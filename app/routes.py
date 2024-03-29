from app import app
from flask import render_template


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/optimal-betting-when-odds-are-random")
def kelly_betting():
    return render_template("optimal-betting-when-odds-are-random.html")
