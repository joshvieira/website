import os


class DevConfig(object):
    DEBUG = True
    SERVER_NAME = 'localhost:5000'
    BOKEH_PORT = 5006
    REDIS_PORT = 6379


class ProdConfig(DevConfig):
    DEBUG=False
    SECRET_KEY = 'secret_key'