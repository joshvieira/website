from config.flaskconfig import ProdConfig
from config.pgconfig import Config
import psycopg2
import pandas as pd
import redis
import time
import pyarrow as pa


def get_market_data():

    # postgres
    con = psycopg2.connect(
        dbname=Config.PG_DBNAME,
        user=Config.PG_USER,
        password=Config.PG_PASS,
        port=Config.PG_PORT
    )
    cur = con.cursor()

    # sql
    sql_pres = 'SELECT tstamp, yes_mid, map.name_contract FROM dems ' \
               'INNER JOIN map ' \
               'ON dems.id_contract = map.id_contract ' \
               'WHERE map.id_mkt=3698;'
    pres = pd.read_sql(sql_pres, con)
    pres = pres.pivot(index='tstamp', columns='name_contract', values='yes_mid')

    sql_dems = 'SELECT tstamp, yes_mid, map.name_contract FROM pres ' \
               'INNER JOIN map ' \
               'ON pres.id_contract = map.id_contract ' \
               'WHERE map.id_mkt=3633;'
    dems = pd.read_sql(sql_dems, con)
    dems = dems.pivot(index='tstamp', columns='name_contract', values='yes_mid')

    sql_trump_nom = """
                    SELECT tstamp, yes_mid, map.name_contract from data 
                    INNER JOIN map 
                    ON data.id_contract = map.id_contract 
                    WHERE data.id_mkt = 3653 
                    AND map.name_contract = 'Donald Trump'
                    """
    trump_nom = pd.read_sql(sql_trump_nom, con)
    trump_nom = trump_nom.pivot(index='tstamp', columns='name_contract', values='yes_mid')

    sql_trump_pres = """
                     SELECT tstamp, yes_mid, map.name_contract from data 
                     INNER JOIN map 
                     ON data.id_contract = map.id_contract 
                     WHERE data.id_mkt = 3698 
                     AND map.name_contract = 'Donald Trump'
                     """
    trump_pres = pd.read_sql(sql_trump_pres, con)
    trump_pres = trump_pres.pivot(index='tstamp', columns='name_contract', values='yes_mid')

    dems_prob = pres / dems
    trump_prob = trump_pres / trump_nom
    cand_prob = pd.concat([dems_prob, trump_prob], axis=1)

    dems_d = dems.resample('d').mean()
    pres_d = pres.resample('d').mean()
    prob_d = cand_prob.clip(0, 1).resample('d').mean()

    cur.close()
    con.close()

    context = pa.default_serialization_context()

    market_data = {
        'dems_d': context.serialize(dems_d).to_buffer().to_pybytes(),
        'pres_d': context.serialize(pres_d).to_buffer().to_pybytes(),
        'prob_d': context.serialize(prob_d).to_buffer().to_pybytes()
    }

    return market_data


def push_to_redis(input_data: dict):

    r = redis.Redis(port=ProdConfig.REDIS_PORT)

    for k, v in input_data.items():
        r.set(name=k, value=v)

    r.close()


if __name__ == '__main__':

    while True:
        try:
            m = get_market_data()
            push_to_redis(m)
            print('Successfully uploaded to Redis at ' + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + '.')
        except Exception as e:
            print(e)
            pass
        time.sleep(60 * 5)