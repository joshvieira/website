import pandas as pd
import sqlite3
import pickle

DBDIR = 'C:/Users/Josh/Dropbox/projects/predictit/db/doris.db'
con = sqlite3.connect(DBDIR)

mkt_pres = "Who will win the 2020 U.S. presidential election?"  # 3698
mkt_dem = "Who will win the 2020 Democratic presidential nomination?"  # 3633


# ----- DEMOCRATIC NOMINATION DATA -----
CUTOFF = 0.05
RULE = '1H' # average over every 5 mins

# contract mapper
q = 'select id_market, id_contract, name_contract from map where name_market="' + mkt_dem + '"'
candidates = pd.read_sql(q, con)
dem_map = dict(zip(candidates['id_contract'], candidates['name_contract']))

# market data
q_data = 'select * from data where id_market=3633'
d = pd.read_sql(q_data, con, parse_dates={'tstamp': '%Y%m%d%H%M%S'})
d['mid'] = (d['yes_bid'] + d['yes_ask']) / 2

# whittle down, calculate rolling window
ts_dem = d.pivot(index='tstamp', columns='id_contract', values='mid')
ok = (ts_dem >= CUTOFF).all()
ts_dem = ts_dem.loc[:, ok] \
    .rename(columns=dem_map) \
    .resample(RULE).mean()


# ----- PRESIDENTIAL ELECTION DATA -----

CUTOFF_PRES = 0.025
RULE_PRES = '1H' # average over every 5 mins

# contract mapper
q = 'select id_market, id_contract, name_contract from map where name_market="' + mkt_pres + '"'
candidates = pd.read_sql(q, con)
pres_map = dict(zip(candidates['id_contract'], candidates['name_contract']))

# market data
q_data = 'select * from data where id_market=3698'
d = pd.read_sql(q_data, con, parse_dates={'tstamp': '%Y%m%d%H%M%S'})
d['mid'] = (d['yes_bid'] + d['yes_ask']) / 2

# whittle down, calculate rolling window
ts_pres = d.pivot(index='tstamp', columns='id_contract', values='mid')
ok = (ts_pres >= CUTOFF_PRES).all()
ts_pres = ts_pres.loc[:, ok] \
    .rename(columns=pres_map) \
    .resample(RULE_PRES).mean()


# --- CALCULATE CONDITIONAL PROBABILITY ---
dem_pres = ts_pres.copy()[ts_dem.columns]
condprob = (dem_pres / ts_dem)

import matplotlib.pyplot as plt
condprob.plot()
plt.legend(loc='best')

dem_pres.copy().resample('30T').mean()
dem_pres.plot()
plt.legend(loc='lower left')

ts_cond = condprob.copy()

with open('C:/Users/Josh/Dropbox/projects/website/data/pres.p', 'wb') as handle:
    pickle.dump([ts_dem, ts_pres, ts_cond], handle, protocol=pickle.HIGHEST_PROTOCOL)