from cfg.config import Redis, PostgresReadWrite
from data.utils import get_sqlalchemy_engine
from data.core.postgres.predictit import Dems, Pres, Map, Data

from sqlalchemy.orm import sessionmaker
import pandas as pd
import redis
import time
import pyarrow as pa


engine = get_sqlalchemy_engine(PostgresReadWrite)


def get_market_data():

    session = sessionmaker(bind=get_sqlalchemy_engine(PostgresReadWrite))()

    # Democratic Party nomination data
    query_obj = (
        session.query(Dems.tstamp, Dems.yes_mid, Map.name_contract)
               .join(Map, Map.id_contract==Dems.id_contract)
    )
    dems = pd.read_sql(query_obj.statement, engine)
    dems = dems.pivot(index='tstamp', columns='name_contract', values='yes_mid')
    dems = dems.rename(columns={'Mike Bloomberg': 'Michael Bloomberg'})


    # Presidential election data
    query_obj = (
        session.query(Pres.tstamp, Pres.yes_mid, Map.name_contract)
               .join(Map, Map.id_contract==Pres.id_contract)
    )
    pres = pd.read_sql(query_obj.statement, engine)
    pres = pres.pivot(index='tstamp', columns='name_contract', values='yes_mid')
    pres = pres.rename(columns={'Mike Bloomberg': 'Michael Bloomberg'})
    trump_pres = pres.pop('Donald Trump').to_frame()  # deal with Trump separately


    # Republican Party nomination data, limited to just Donald Trump
    query_obj = (
        session.query(Data.tstamp, Data.yes_mid, Map.name_contract)
               .join(Map, Map.id_contract==Data.id_contract)
               .filter(Data.id_mkt==3653)
               .filter(Map.name_contract=='Donald Trump')
    )
    trump_nom = pd.read_sql(query_obj.statement, engine)
    trump_nom = trump_nom.pivot(index='tstamp', columns='name_contract', values='yes_mid')


    # clean up
    session.close()


    dems_prob = pres / dems
    trump_prob = trump_pres / trump_nom
    cand_prob = pd.concat([dems_prob, trump_prob], axis=1)

    nom = pd.concat([dems, trump_nom], axis=1)
    nom_last_day = nom.resample('d').mean().iloc[-1]

    dems_d = dems.resample('d').mean()
    pres_d = pres.resample('d').mean()
    prob_d = cand_prob.clip(0, 1).resample('d').mean()

    context = pa.default_serialization_context()

    market_data = {
        'dems_d': context.serialize(dems_d).to_buffer().to_pybytes(),
        'pres_d': context.serialize(pres_d).to_buffer().to_pybytes(),
        'prob_d': context.serialize(prob_d).to_buffer().to_pybytes()
    }

    return market_data


def push_to_redis(input_data: dict):

    with redis.Redis(port=Redis.PORT) as r:

        for k, v in input_data.items():

            r.set(name=k, value=v)


if __name__ == '__main__':

    while True:
        try:
            push_to_redis(get_market_data())
            print('Successfully uploaded to Redis at ' + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + '.')
        except Exception as e:
            print(e)
            pass
        time.sleep(60 * 5)
