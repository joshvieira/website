from flask import Flask
import os
from config.flaskconfig import DevConfig, ProdConfig

app = Flask(__name__)

from app import routes

config = ProdConfig()
if os.environ['ENV'] is not None:
    if os.environ['ENV'] == 'dev':
        config = DevConfig()

app.config.from_object(config)