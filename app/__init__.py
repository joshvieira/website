from flask import Flask
import os
from cfg.config import FlaskDev, FlaskProd

app = Flask(__name__)

from app import routes

config = FlaskProd() if os.environ.get("ENV") == "prod" else FlaskDev()

app.config.from_object(config)
