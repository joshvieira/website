from data.utils import get_sqlalchemy_engine

__all__ = ["engine"]


engine = get_sqlalchemy_engine("pg10")
