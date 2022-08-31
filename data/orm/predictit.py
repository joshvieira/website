from sqlalchemy import (
    MetaData,
    Column,
    INTEGER,
    TEXT,
    TIMESTAMP,
    REAL,
    BOOLEAN,
    ForeignKeyConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base

schema_name = "predictit"
meta = MetaData(schema=schema_name)
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
    id_mkt = Column(INTEGER, primary_key=True)
    id_contract = Column(INTEGER, primary_key=True)
    yes_bid = Column(REAL)
    yes_ask = Column(REAL)
    yes_mid = Column(REAL)
    isopen = Column(BOOLEAN)
    __table_args__ = (
        Index("mktid_index", id_mkt),
        ForeignKeyConstraint(
            ["id_mkt", "id_contract"], ["map.id_mkt", "map.id_contract"]
        ),
    )


class Dems(base):  # smaller table for faster query
    __tablename__ = "dems"
    tstamp = Column(TIMESTAMP, primary_key=True)
    id_mkt = Column(INTEGER, primary_key=True)
    id_contract = Column(INTEGER, primary_key=True)
    yes_bid = Column(REAL)
    yes_ask = Column(REAL)
    yes_mid = Column(REAL)
    isopen = Column(BOOLEAN)
    __table_args__ = (
        ForeignKeyConstraint(
            ["id_mkt", "id_contract"], ["map.id_mkt", "map.id_contract"]
        ),
    )


class Pres(base):  # smaller table for faster query
    __tablename__ = "pres"
    tstamp = Column(TIMESTAMP, primary_key=True)
    id_mkt = Column(INTEGER, primary_key=True)
    id_contract = Column(INTEGER, primary_key=True)
    yes_bid = Column(REAL)
    yes_ask = Column(REAL)
    yes_mid = Column(REAL)
    isopen = Column(BOOLEAN)
    __table_args__ = (
        ForeignKeyConstraint(
            ["id_mkt", "id_contract"], ["map.id_mkt", "map.id_contract"]
        ),
    )


if __name__ == "__main__":

    import pandas as pd
    import os
    from sqlalchemy import create_engine
    from cfg.config import get_postgres_uri
    import sqlalchemy
    from sqlalchemy import exc
    from dotenv import load_dotenv

    load_dotenv()

    # Create Postgres db engine
    # Create schema and tables (with key constraints) if they do not exist already
    engine = create_engine(get_postgres_uri())
    if not engine.dialect.has_schema(engine, schema_name):
        engine.execute(sqlalchemy.schema.CreateSchema(schema_name))
    meta.create_all(bind=engine)

    # Populate database tables
    for tablename in ["map", "dems", "pres"]:
        if tablename == "map":
            columns = ["id_mkt", "id_contract", "name_mkt", "name_contract"]
        else:
            columns = [
                "tstamp",
                "id_mkt",
                "id_contract",
                "yes_bid",
                "yes_ask",
                "yes_mid",
                "isopen",
            ]
        data = pd.read_csv(
            os.path.join(os.getenv("POSTGRES_BACKUP_LOCATION"), tablename + ".csv"),
            names=columns,
        )
        try:
            data.to_sql(
                name=tablename,
                con=engine,
                schema=schema_name,
                index=False,
                if_exists="append",
            )
            print(f"{schema_name}.{tablename} data has been uploaded from CSV.")
        except exc.IntegrityError:
            print(f"{schema_name}.{tablename} data already exists.")
            pass
