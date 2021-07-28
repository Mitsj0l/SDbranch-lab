import json
from datetime import datetime

import central.authentication.check_config
import central.authentication.database
import requests


def central_authentication():
    print("Starting the API token retrieval")
    try:
        get_xcsrf = requests.post(
            url=central.authentication.check_config.central_instance +
            "/oauth2/authorize/central/api/login",
            params={
                "client_id": central.authentication.check_config.app_clientid,
            },
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "username": central.authentication.check_config.app_username,
                "password": central.authentication.check_config.app_password
            })
        )
        # print(get_xcsrf.url)
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=get_xcsrf.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=get_xcsrf.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    csrf_token = get_xcsrf.cookies['csrftoken']
    csrf_session_token = get_xcsrf.cookies['session']
    print("This is my API CSRF token: ", csrf_token)
    print("This is my API CSRF Session token: ", csrf_session_token)

    try:
        get_authcode = requests.post(
            url=central.authentication.check_config.central_instance +
            "/oauth2/authorize/central/api",
            params={
                "client_id": central.authentication.check_config.app_clientid,
                "response_type": "code",
                "scope": "all",
            },
            headers={
                "Content-Type": "application/json",
                "X-CSRF-token": csrf_token,
                "Cookie": "csrftoken=" + csrf_token + "; session=" + csrf_session_token,
            },
            data=json.dumps({
                "customer_id": central.authentication.check_config.app_customerid
            })
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=get_authcode.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=get_authcode.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    get_authcode_json = get_authcode.json()
    authcode = get_authcode_json['auth_code']
    try:
        getaccesstoken = requests.post(
            url=central.authentication.check_config.central_instance + "/oauth2/token",
            params={
                "client_id": central.authentication.check_config.app_clientid,
                "grant_type": "authorization_code",
                "client_secret": central.authentication.check_config.app_clientsecret,
                "code": authcode,
            },
            headers={
                "Cookie": "csrftoken=" + csrf_token + "; session=" + csrf_session_token,
            },
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=getaccesstoken.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=getaccesstoken.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    getaccesstoken_json = getaccesstoken.json()
    token_refresh = getaccesstoken_json['refresh_token']
    token_access = getaccesstoken_json['access_token']
    token_expiry = getaccesstoken_json['expires_in']
    timestamp = datetime.now().isoformat(' ', 'seconds')
    central.authentication.database.database_updatetokens(central.authentication.check_config.app_clientid, central.authentication.check_config.app_customerid, central.authentication.check_config.app_clientsecret, csrf_token, csrf_session_token, authcode,
                                                          token_access,
                                                          timestamp)
    return token_refresh, token_access, token_expiry, csrf_token, csrf_session_token
