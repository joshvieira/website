from flask import Flask
import os
from config.flaskconfig import DevConfig, ProdConfig

app = Flask(__name__)

from app import routes

config = ProdConfig()
try:
    if os.environ['ENV'] == 'dev':
        config = DevConfig()
except KeyError:
    pass

app.config.from_object(config)