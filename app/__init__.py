import os

from flask import Flask
from dotenv import load_dotenv

from cfg.config import FlaskDev, FlaskProd

load_dotenv()
app = Flask(__name__)

from app import routes


app.config.from_object(
    FlaskProd() if os.getenv("ENV", default="dev") == "prod" else FlaskDev()
)
