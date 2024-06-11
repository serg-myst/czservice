from dotenv import load_dotenv
import os
import logging

load_dotenv()

SERIAL = os.environ.get('serial')
URL_AUTH = os.environ.get('url_auth')
URL_TOKEN = os.environ.get('url_token')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

FILE_LOG = 'cz_service.log'
logging.basicConfig(level=logging.INFO, filename=FILE_LOG,
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')
LOGGER = logging.getLogger('cz_service')
