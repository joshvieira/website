from sqlalchemy import MetaData, Column, INTEGER, TEXT, TIMESTAMP, REAL, BOOLEAN, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base

from data.core.postgres import engine

meta = MetaData(bind=engine, schema='predictit')
base = declarative_base(metadata=meta)


class Map(base):
    __tablename__ = "map"
    id_mkt = Column(INTEGER, primary_key=True)
    id_contract = Column(INTEGER, primary_key=True)
    name_mkt = Column(TEXT)
    name_contract = Column(TEXT)


class Data(base):
    __tablename__ = "data"
    tstamp = Column(TIMESTAMP, primary_key=True)
    id_mkt = Column(INTEGER, ForeignKey(Map.id_mkt), primary_key=True)
    id_contract = Column(INTEGER, ForeignKey(Map.id_contract), primary_key=True)
    yes_bid = Column(REAL)
    yes_ask = Column(REAL)
    yes_mid = Column(REAL)
    isopen = Column(BOOLEAN)
    __table_args__ = (Index('mktid_index', id_mkt), )


class Dems(base):  # smaller table for faster query
    __tablename__ = "dems"
    tstamp = Column(TIMESTAMP, primary_key=True)
    id_mkt = Column(INTEGER, ForeignKey(Map.id_mkt), primary_key=True)
    id_contract = Column(INTEGER, ForeignKey(Map.id_contract), primary_key=True)
    yes_bid = Column(REAL)
    yes_ask = Column(REAL)
    yes_mid = Column(REAL)
    isopen = Column(BOOLEAN)


class Pres(base):  # smaller table for faster query
    __tablename__ = "pres"
    tstamp = Column(TIMESTAMP, primary_key=True)
    id_mkt = Column(INTEGER, ForeignKey(Map.id_mkt), primary_key=True)
    id_contract = Column(INTEGER, ForeignKey(Map.id_contract), primary_key=True)
    yes_bid = Column(REAL)
    yes_ask = Column(REAL)
    yes_mid = Column(REAL)
    isopen = Column(BOOLEAN)
