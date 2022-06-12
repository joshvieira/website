from config.pgconfig import Config

from sqlalchemy import create_engine


def get_sqlalchemy_engine(dbname):

    if dbname == 'pg10':

        s = f'postgresql+psycopg2://{Config.PG_USER}:{Config.PG_PASS}@localhost:{Config.PG_PORT}/{dbname}'

        return create_engine(s, use_batch_mode=True)