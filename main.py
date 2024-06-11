import requests
import win32com.client
import json
import base64
from datetime import datetime, timedelta
import sys
import jwt
from sqlalchemy import delete, insert
from config import SERIAL, URL_AUTH, URL_TOKEN, STORE
from logger import log, cleanup_logs, logs_path
from models import Token
from database import session_maker

session = session_maker()


def save_token(token_info: dict):
    stmt = delete(Token)
    session.execute(stmt)
    session.commit()

    stmt = insert(Token).values(token_info)
    session.execute(stmt)
    session.commit()


def get_token_info(token: str, token_info: dict):
    decoded = jwt.decode(token, options={"verify_signature": False})
    offset = 10800  # +3 hours
    expiration_date = datetime(1970, 1, 1) + timedelta(seconds=(int(decoded['exp'] + offset)))

    token_info['expiration_date'] = expiration_date.isoformat(sep='T')
    token_info['full_name'] = decoded['full_name']
    token_info['mchd_id'] = str(decoded['mchd_id'])
    token_info['inn'] = str(decoded['inn'])


def get_token():
    log.info(f'CZ. Start')

    CADES_BES = 1
    CAPICOM_ENCODE_BASE64 = 0
    CAPICOM_CURRENT_USER_STORE = 2
    CAPICOM_MY_STORE = STORE
    CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED = 2

    sSerialNumber = SERIAL

    log.info(f'Auth {URL_AUTH}')
    headers = {'accept': 'application/json'}

    response = requests.get(URL_AUTH, headers=headers)

    status = response.status_code

    if status != 200:
        log.error(f'Auth error. Status code {status}. URL {URL_AUTH}')
        sys.exit()

    content = json.loads(response.content)

    data = content['data']

    encoded_data = base64.b64encode(data.encode('ascii'))

    try:
        log.info(f'Getting certificate {sSerialNumber} in store {STORE}')
        oStore = win32com.client.Dispatch("CAdESCOM.Store")
        oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED)
        oCert = ''
        for val in oStore.Certificates:
            if val.SerialNumber == sSerialNumber:
                oCert = val
        oStore.Close
        log.info(f'Get certificate {sSerialNumber}')
    except Exception as e:
        log.error(f"Error getting certificate {sSerialNumber} in store {STORE}")


    try:
        log.info(f'Signing data with certificate {sSerialNumber}')
        oCPSigner = win32com.client.Dispatch("CAdESCOM.CPSigner")
        oSignedData = win32com.client.Dispatch("CAdESCOM.CadesSignedData")

        oCPSigner.Certificate = oCert
        oSignedData.ContentEncoding = 1

        base64_message = encoded_data.decode('ascii')
        oSignedData.Content = base64_message

        sSignedData = oSignedData.SignCades(oCPSigner, CADES_BES, False, CAPICOM_ENCODE_BASE64)

        headers = {'accept': 'application/json',
                   'Content-Type': 'application/json'
                   }

        params = {
            'uuid': content['uuid'],
            'data': sSignedData
        }
    except Exception as e:
        log.error(f'Error signing data: {e}')
    
    log.info(f'Getting token {URL_TOKEN}')
    response = requests.post(URL_TOKEN, headers=headers, json=params)

    status = response.status_code

    if status != 200:
        log.error(f'Error geting token {status}. URL {URL_TOKEN}')
        sys.exit()

    content = json.loads(response.content)

    token_info = {
        'jwt_token': content['token']
    }
    try:
        log.info("Getting info from JWT")
        get_token_info(token_info['jwt_token'], token_info)
    except Exception as e:
        log.error(f"Error while reading JWT: {e}")

    try:
        log.info("Saving info in database")
        save_token(token_info)
    except Exception as e:
        log.error("Error saving info in database: {e}")

    log.info(f'Finish')


if __name__ == '__main__':
    get_token()
    cleanup_logs(logs_path)
