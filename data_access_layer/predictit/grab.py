import os
import time
from datetime import datetime
import gzip

import requests
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

from cfg.config import get_postgres_uri
from data_access_layer.predictit import store, TEMP_FOLDER


PREDICTIT_API_ENDPOINT = "https://www.predictit.org/api/marketdata/all/"
INTERVAL = 5  # only save data every 5th minute


def run():
    """
    Download all market data from predictit.com every minute and then
    (1) Save data to disk as compressed json
    (2) Write to postgres tables
    """

    try:

        r = requests.get(PREDICTIT_API_ENDPOINT)

        # save immediately
        fn0 = "TEMP" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json.gz"
        with gzip.open(os.path.join(TEMP_FOLDER, fn0), "w") as f:
            f.write(r.content)

        # get timestamp from the file
        data = r.json()["markets"]
        t = data[0]["timeStamp"]
        t = t.replace("-", "").replace(":", "").split(".", 1)[0]
        is_5th_minute = pd.Timestamp(t).minute % INTERVAL == 0

        # Upload data to Postgres
        if is_5th_minute:

            # postgres
            con = psycopg2.connect(get_postgres_uri())
            cur = con.cursor()

            map, values = store.prep_mktdata(data)

            sql_map = "INSERT INTO predictit.map (id_mkt, id_contract, name_mkt, name_contract) VALUES %s ON CONFLICT (id_mkt, id_contract) DO NOTHING"
            execute_values(cur, sql_map, map)

            sql_data = "INSERT INTO predictit.data (tstamp, id_mkt, id_contract, yes_bid, yes_ask, yes_mid, isopen) VALUES %s"
            execute_values(cur, sql_data, values)

            con.commit()
            cur.close()
            con.close()
            print("Inserted records for " + t)

        # Remove the file so directory does not get cluttered
        os.remove(os.path.join(TEMP_FOLDER, fn0))

    except psycopg2.Error as e:
        print(e)
        # Ignore database errors and keep downloading and saving the files
        pass


if __name__ == "__main__":
    while True:
        run()
        time.sleep(60)
