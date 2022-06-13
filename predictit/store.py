import os
import gzip
import json
import psycopg2
from psycopg2.extras import execute_values
from cfg.config import PostgresReadWrite

DATAPATH = 'C:/Users/Josh/Dropbox/projects/predictit_bkp/'


def prep_mktdata(fulldata: list):

    map = set()
    data = list()

    # initial format: '2019-03-03T13:58:47.2612891'
    tstamp = fulldata[0]['timeStamp']
    tstamp = tstamp.split('T')
    tstamp = tstamp[0] + ' ' + tstamp[1].split('.')[0]

    # loop through each betting market
    for i in range(len(fulldata)):

        mkt = fulldata[i]

        # market information
        id_mkt = mkt['id']
        name_mkt = mkt['name']
        isopen = {'Open': True}.get(mkt['status'], False)

        # loop through each contract
        for j in range(len(mkt['contracts'])):
            c = mkt['contracts'][j]

            id_contract = c['id']
            name_contract = c['name']
            yes_bid = {None: 0.0}.get(c['bestSellYesCost'], c['bestSellYesCost'])
            yes_ask = {None: 1.0}.get(c['bestBuyYesCost'], c['bestBuyYesCost'])
            yes_mid = 0.5 * (yes_bid + yes_ask)

            # schema of map: id_mkt, id_contract, name_mkt, name_contract
            map.add((id_mkt, id_contract, name_mkt, name_contract))

            # schema of data: time, id_mkt, id_contract, yes_bid, yes_ask, yes_mid, isopen
            data.append((tstamp, id_mkt, id_contract, yes_bid, yes_ask, yes_mid, isopen))

    return map, data


def prep_block_mktdata(datadir):

    map = set()
    data = list()

    for fn in os.listdir(datadir):

        print('Extracting data from ' + fn)
        with gzip.open(datadir + fn) as f:
            fulldata = json.load(f)['markets']

        map1, data1 = prep_mktdata(fulldata)

        map = map.union(map1)
        data.extend(data1)

    return list(map), data


if __name__ == '__main__':

    con = psycopg2.connect(
        dbname=PostgresReadWrite.NAME,
        user=PostgresReadWrite.USER,
        password=PostgresReadWrite.PASS,
    )
    cur = con.cursor()

    map, data = prep_block_mktdata(DATAPATH + '201901/')

    execute_values(cur, 'INSERT INTO map (id_mkt, id_contract, name_mkt, name_contract) VALUES %s ON CONFLICT (id_mkt, id_contract) DO NOTHING', map)
    con.commit()
    execute_values(cur, 'INSERT INTO data (tstamp, id_mkt, id_contract, yes_bid, yes_ask, yes_mid, isopen) VALUES %s', data)
    con.commit()

    con.close()
