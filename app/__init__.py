from flask import Flask
import os
from config.flaskconfig import DevConfig, ProdConfig

app = Flask(__name__)

from app import routes

if os.environ['ENV'] == 'prod':
    config = ProdConfig()
else:
    config = DevConfig()
app.config.from_object(config)