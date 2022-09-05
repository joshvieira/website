import os
from dotenv import load_dotenv

load_dotenv()

TEMP_DIR = os.getenv('TEMP_DIR')


def get_redis_host_and_port():
    return {
        "host": os.getenv("SERVICE_NAME_REDIS", "localhost"),
        "port": 6379
    }


def get_postgres_uri():
    host = os.getenv("SERVICE_NAME_POSTGRES", "localhost")
    port = 5432
    db_name = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
