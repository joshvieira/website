import os
from dotenv import load_dotenv

load_dotenv()
TEMP_FOLDER = os.getenv("TEMP_FOLDER")
