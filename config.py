from dotenv import load_dotenv
import os
from logger import log

log.info("Getting env vars")
try:
    load_dotenv()
    SERIAL = os.environ.get("serial")
    STORE = os.environ.get("store")
    URL_AUTH = os.environ.get("url_auth")
    URL_TOKEN = os.environ.get("url_token")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
except Exception as e:
    log.error(f"Error getting vars: {e}")
