from database.utils import get_sqlalchemy_engine

from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base


engine = get_sqlalchemy_engine('pg10')
meta = MetaData(bind=engine, schema='predictit')
base = declarative_base(metadata=meta)


class Map(base):
    __table__ = Table('map', meta, autoload=True)

class Data(base):
    __table__ = Table('data', meta, autoload=True)

class Dems(base):
    __table__ = Table('dems', meta, autoload=True)

class Pres(base):
    __table__ = Table('pres', meta, autoload=True)