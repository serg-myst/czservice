import requests
import win32com.client
import json
import base64
from datetime import datetime, timedelta
import sys
import jwt
from sqlalchemy import delete, insert
from config import SERIAL, URL_AUTH, URL_TOKEN, STORE, URL_AUTH_SUZ, URL_TOKEN_SUZ, OMSID
from config import LOGGER as log
from models import Token
from database import session_maker

session = session_maker()


def save_token(token_info: dict, token_type: int):

    stmp_type = 'CZ' if token_type == 0 else 'SUZ'

    stmt = delete(Token).where(Token.token_type == stmp_type)
    session.execute(stmt)
    session.commit()

    stmt = insert(Token).values(token_info)
    session.execute(stmt)
    session.commit()


def get_token_info(token: str, token_info: dict, token_type: int):
    if token_type == 0:
        decoded = jwt.decode(token, options={"verify_signature": False})
        offset = 10800  # +3 hours
        expiration_date = datetime(1970, 1, 1) + timedelta(seconds=(int(decoded['exp'] + offset)))

        token_info['token_type'] = 'CZ'
        token_info['expiration_date'] = expiration_date.isoformat(sep='T')
        token_info['full_name'] = decoded['full_name']
        token_info['mchd_id'] = str(decoded['mchd_id'])
        token_info['inn'] = str(decoded['inn'])
    else:
        offset = 32400
        expiration_date = datetime.now() + timedelta(seconds=(offset))
        token_info['token_type'] = 'SUZ'
        token_info['expiration_date'] = expiration_date.isoformat(sep='T')
        token_info['full_name'] = ''
        token_info['mchd_id'] = ''
        token_info['inn'] = ''


def get_token(token_type: int):
    log.info(f'CZ. Start - {datetime.now()}. TYPE {token_type}')

    CADES_BES = 1
    CAPICOM_ENCODE_BASE64 = 0
    CAPICOM_CURRENT_USER_STORE = 2
    CAPICOM_MY_STORE = STORE
    CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED = 2

    sSerialNumber = SERIAL

    headers = {'accept': 'application/json'}

    if token_type == 0:
        post_url = URL_AUTH
    else:
        post_url = URL_AUTH_SUZ

    response = requests.get(post_url, headers=headers)

    status = response.status_code

    if status != 200:
        log.error(f'Error. Status code {status}. URL {URL_AUTH}. TYPE {token_type}')
        sys.exit()

    content = json.loads(response.content)

    data = content['data']

    encoded_data = base64.b64encode(data.encode('ascii'))

    oStore = win32com.client.Dispatch("CAdESCOM.Store")
    oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED)
    oCert = ''
    for val in oStore.Certificates:
        if val.SerialNumber == sSerialNumber:
            oCert = val
    oStore.Close

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

    if token_type == 0:
        post_url = URL_TOKEN
    else:
        post_url = f'{URL_TOKEN_SUZ}/{OMSID}'

    response = requests.post(post_url, headers=headers, json=params)

    status = response.status_code

    if status != 200:
        log.error(f'Error. Status code {status}. URL {post_url}. TYPE {token_type}')
        sys.exit()

    content = json.loads(response.content)

    token_info = {
        'jwt_token': content['token']
    }

    get_token_info(token_info['jwt_token'], token_info, token_type)

    save_token(token_info, token_type)

    log.info(f'CZ. Stop -  {datetime.now()}. TYPE {token_type}')


if __name__ == '__main__':
    # 0 - cz token, 1 - suz token
    get_token(0)
    get_token(1)
