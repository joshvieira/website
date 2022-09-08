import os

from flask import Flask
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

from app import routes


if os.getenv("ENV") == "prod":
    app.config.update(SECRET_KEY=os.getenv("FLASK_SECRET_KEY"))
