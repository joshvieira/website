from sqlalchemy import create_engine


def get_sqlalchemy_engine(config):

    s = f'postgresql+psycopg2://{config.USER}:{config.PASS}@localhost:{config.PORT}/{config.NAME}'

    return create_engine(s)
