import os
import time
from datetime import datetime
import gzip

import requests
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

from cfg.config import PostgresReadWrite
from predictit import store


def run():
    """
    Download all market data from predictit.com every minute and then
    (1) Save data to disk as compressed json if minute ends in 0 or 5
    (2) Write to postgres tables
    :return:
    """

    url = 'https://www.predictit.org/api/marketdata/all/'

    try:

        r = requests.get(url)

        # save immediately
        fn0 = 'TEMP' + datetime.now().strftime("%Y%m%d%H%M%S") + '.json.gz'
        with gzip.open('./predictit/temp/' + fn0, 'w') as f:
            f.write(r.content)

        # get timestamp from the file
        data = r.json()['markets']
        t = data[0]['timeStamp']
        t = t.replace('-', '').replace(':', '').split('.', 1)[0]
        is_5th_minute = pd.Timestamp(t).minute % 5 == 0
        fn = t + '.json.gz'

        # if this is data we haven't seen before,
        # (1) save to appropriate raw output directory
        # (2) upload data to postgres
        output_dir = './predictit/output/' + fn[:6] + '/'
        if is_5th_minute and not os.path.exists(output_dir + fn):

            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)

            # raw data
            os.replace('./predictit/temp/' + fn0, output_dir + fn)

            # postgres
            con = psycopg2.connect(
                dbname=PostgresReadWrite.NAME,
                user=PostgresReadWrite.USER,
                password=PostgresReadWrite.PASS,
                port=PostgresReadWrite.PORT
            )
            cur = con.cursor()

            map, values = store.prep_mktdata(data)

            sql_map = 'INSERT INTO map (id_mkt, id_contract, name_mkt, name_contract) VALUES %s ON CONFLICT (id_mkt, id_contract) DO NOTHING'
            execute_values(cur, sql_map, map)

            sql_data = 'INSERT INTO data (tstamp, id_mkt, id_contract, yes_bid, yes_ask, yes_mid, isopen) VALUES %s'
            execute_values(cur, sql_data, values)

            con.commit()
            cur.close()
            con.close()
            print('Inserted records for ' + t)

        else:  # don't let temp directory get cluttered
            os.remove('./predictit/temp/' + fn0)

    except Exception as e:

        print(e)


if __name__ == '__main__':
    while True:
        run()
        time.sleep(60)

