import ast
import json
import pickle
import urllib
import urllib.parse as urlparse
from datetime import datetime
from urllib.parse import parse_qs

import central.authentication.check_config
import central.authentication.database
import httplib2
import hyper
import pandas as pd
import requests
from bs4 import BeautifulSoup
from hyper.contrib import HTTP20Adapter
from requests.models import PreparedRequest

session = requests.session()
username = central.authentication.check_config.app_username
password = central.authentication.check_config.app_password
customer_id = central.authentication.check_config.app_customerid

central_portal = str(central.authentication.check_config.central_portal)
central_portal_fqdn = str(
    central.authentication.check_config.central_portal_fqdn)
central_instance = str(central.authentication.check_config.central_instance)
central_ui_url = str(central.authentication.check_config.central_ui_url)
central_ui_fqdn = str(central.authentication.check_config.central_ui_fqdn)


def frontend_auth():
    print("Starting the frontend token retrieval")
####################################################################################
# 1st API call - check if username exists
####################################################################################
    try:
        print("1 - Check if username exists")
        response = requests.post(
            url=central_portal + "/platform/login/validate/userid",
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            },
            data={
                "userid": username,
                "language": "en_US",
            },
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
# 2nd API call - Post SSO and Receive SSO URL Params
####################################################################################
    try:
        print("2 - Post SSO and Receive SSO URL Params")
        url = central_portal + "/platform/login/aruba/sso"
        session.mount(url, HTTP20Adapter())
        response1 = session.post(
            url=url,
            params={
                "username": username,
            },
            headers={

            },
            data={
                "pf.username": username,
            },
        )

        response1_header = dict(response1.headers)

        location_url = response1_header[b'location'].decode('utf-8')
        global_session = response1_header[b'set-cookie'].decode('utf-8')

        base_hostname = urlparse.urlparse(location_url).hostname
        base_path = urlparse.urlparse(location_url).path
        base_server = "https://" + base_hostname + base_path
        base_query = urlparse.urlparse(location_url)

        params_new = parse_qs(base_query.query)

    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
# 3rd API call - Get SSO URL + Tokens
####################################################################################
    try:
        print("3 - Get SSO URL + Tokens")
        session.mount(base_server, HTTP20Adapter())

        response3 = session.get(
            url=base_server,
            params=params_new,
            headers={
                "Referer": central_portal + "/platform/login/user",
                "Cookie": global_session,
            },
        )

        cookie0 = response3.raw.headers['set-cookie'][0].decode('utf-8')
        cookie1 = response3.raw.headers['set-cookie'][1].decode('utf-8')
        cookie2 = response3.raw.headers['set-cookie'][2].decode('utf-8')
        cookie3 = response3.raw.headers['set-cookie'][3].decode('utf-8')
        cookiejar = cookie0 + "; " + cookie1 + "; " + cookie2 + "; " + cookie3

        location_3rd_API = response3.headers[b'location'].decode('utf-8')

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response3.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response3.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
# 4th API call - GET SSO
####################################################################################
    try:
        print("4 - Get SSO to user-mapping")
        session.mount(location_3rd_API, HTTP20Adapter())
        response4 = session.get(
            url=location_3rd_API,
            headers={

            },
        )

    except requests.exceptions.RequestException:
        print('HTTP Request failed')

###################################################################################
#  5th API call - POST Credentials to IDP
###################################################################################
    try:
        print("5 - POST Credentials to IDP")
        session.mount(location_3rd_API, HTTP20Adapter())
        response5 = session.post(
            url=location_3rd_API,
            headers={
                "Cookie": cookiejar,
            },
            data={
                "pf.ok": "",
                "pf.cancel": "",
                "pf.username": username,
                "pf.pass": password,
            },
        )

        cookie0 = response5.raw.headers['set-cookie'][0].decode('utf-8')
        cookie1 = response5.raw.headers['set-cookie'][1].decode('utf-8')
        cookie2 = response5.raw.headers['set-cookie'][2].decode('utf-8')
        cookiejar = cookie0 + "; " + cookie1 + "; " + cookie2

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response5.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response5.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    soup = BeautifulSoup(response5.content, features="html.parser")
    # print(soup.prettify())
    try:
        saml_code = soup.find('input', {'name': 'SAMLResponse'}).get('value')
        print("5 - Found the SAML Response code.")
    except:
        print("5 - SAML Response code noth found...")


####################################################################################
# 6th API call - POST SSO ACS
####################################################################################
    try:
        print("6 - Post to SSO ACS")
        api_6th_url = "https://sso.arubanetworks.com/sp/ACS.saml2"
        session.mount(api_6th_url, HTTP20Adapter())
        response6 = session.post(
            url=api_6th_url,
            headers={
                "Cookie": cookiejar,
            },
            data={
                "RelayState": central_portal + "/platform/login/user",
                "SAMLResponse": saml_code
            }
        )

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response6.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response6.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    soup6 = BeautifulSoup(response6.content, features="html.parser")
    # print(soup.prettify())
    try:
        ref_code = soup6.find('input', {'name': 'REF'}).get('value')
        # print(ref_code)
        print("6 - Found the SAML REF Code")
    except:
        print("6 - SAML REF Code noth found...")


####################################################################################
# 7th API call - POST to Aruba Central
####################################################################################
    try:
        print("7 - Logging into Central")
        # print("Old global session token: ",global_session)
        api_7th_url = central_portal + "/platform/login/user"
        session.mount(api_7th_url, HTTP20Adapter())
        response7 = session.post(
            url=api_7th_url,
            headers={
#                 "Host": central_portal_fqdn, # With Central 2.5.3 this will cause an issue with mounting the HTTP2 session.
                "Cookie": global_session,
            },
            data={
                "REF": ref_code,
                "TargetResource": api_7th_url,
            },
        )

        raw_response = response7.raw.headers
        cookie0 = response7.raw.headers['set-cookie'][0].decode('utf-8')
        cookie1 = response7.raw.headers['set-cookie'][1].decode('utf-8')
        cookiejar = cookie0 + "; " + cookie1

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

####################################################################################
# 8th API call - Redirect to Customer portal
####################################################################################
    try:
        print("8 - Redirecting to Central customer list")
        api_8th_url = central_portal + "/platform/login/redirect/customer"

        session.mount(api_8th_url, HTTP20Adapter())
        response8 = session.get(
            url=api_8th_url,
            headers={
                "Host": central_portal_fqdn,
                "Cookie": cookiejar,
            },
        )

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response8.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response8.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

####################################################################################
# 9th API call - Getting Permissions from customer portal
####################################################################################
    try:
        print("9 - Getting Permissions from customer portal")
        api_9th_url = central_portal + "/platform/login/customers"
        session.mount(api_9th_url, HTTP20Adapter())
        response9 = requests.get(
            url=api_9th_url,
            headers={
                "Cookie": cookiejar,
            },
        )

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response9.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response9.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    customerlist = response9.json()
    df2 = pd.json_normalize(customerlist['customers_list'])

    print("Logged in user: ", customerlist['email_id'])
    print("The account has permission to the following accounts:")
    print(df2[['name', 'id', 'created_at', 'email', 'region']])

####################################################################################
# 10th API call - Selecting the user Frontend account in Admin panel
####################################################################################
    try:
        print("10 - Selecting the user Frontend account in Admin panel")
        api_10th_url = central_portal + "/platform/login/customers/selection"
        session.mount(api_10th_url, HTTP20Adapter())
        response10 = requests.post(
            url=api_10th_url,
            headers={
                "Content-Type": "application/json;charset=utf-8",
                "Host": central_portal_fqdn,
                "Cookie": cookiejar,
            },
            data=json.dumps({
                "cid": customer_id
            })
        )
        print("Selected Customer Account ID (CID): ", customer_id)
        csrf_admin_token = response10.cookies['csrftoken']
        csrf_admin_global_session_token = response10.cookies['global-session']

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response10.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response10.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
# 11th API call - Get Token for Admin UI Frontend
####################################################################################
    try:

        print("11 - Get Token for Admin UI Frontend")
        # print(cookiejar)
        api_11th_url = central_portal + "/platform/frontend/"
        session.mount(api_11th_url, HTTP20Adapter())

        response11 = requests.get(
            url=api_11th_url,
            headers={
                "Host": central_portal_fqdn,
                "Cookie": cookiejar,
            },
        )
        cookie0 = response11.headers['Set-Cookie']
        cookiejar = cookie0

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response11.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response11.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
# 12th API call - Get Token for NMS
####################################################################################
    try:
        print("12 - Get Token for NMS App")
        api_12th_url = central_portal + "/platform/login/apps/nms/launch"

        session.mount(api_12th_url, HTTP20Adapter())
        response12 = session.get(
            url=api_12th_url,
            params={
            },
            headers={
                "Cookie": cookiejar,
            },
        )
        cookie0 = response12.raw.headers['set-cookie'][0].decode('utf-8')
        location_url = response12.raw.headers['location'][0].decode('utf-8')
        base_server = "https://" + base_hostname + base_path
        base_query = urlparse.urlparse(location_url)
        params_new = parse_qs(base_query.query)

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response12.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response12.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
# 13th API call - Get Session Token for frontend new XCSRF Tokens
####################################################################################
    try:
        print("13 - Redirecting to Central NMS Frontend")
        api_13th_url = central_ui_url + "/login"

        session.mount(api_13th_url, HTTP20Adapter())
        response13 = session.get(
            url=api_13th_url,
            params=params_new,
            headers={

            },
        )

        cookie0 = response13.raw.headers['set-cookie'][0].decode('utf-8')
        cookiejar = cookie0
        location_url = response13.raw.headers['location'][0].decode('utf-8')

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response13.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response13.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

####################################################################################
# 14th API call - Get XCSRF Token for frontend
####################################################################################
    try:
        print("14 - Get XCSRF Token for frontend")
        api_14th_url = location_url

        session.mount(api_14th_url, HTTP20Adapter())
        response14 = requests.get(
            url=api_14th_url,
            headers={
                "Host": central_ui_fqdn,
                "Cookie": cookiejar,
                "Referer": central_portal + "/platform/frontend/",
            },
        )

        csrf_token = response14.cookies['csrftoken']
        csrf_session_token = response14.cookies['session']
        print("This is the final Frontend NMS CSRF token: ", csrf_token)
        print("This is the final Frontend NMS CSRF Session token: ",
              csrf_session_token)
        cookiejar = "csrftoken=" + csrf_token + "; session=" + csrf_session_token

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response14.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response14.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    print("15 - Request Central Keep-alive")
    try:
        api_15th_url = central_ui_url + "/admin/user/keepalive"
        response = requests.post(
            url=api_15th_url,
            headers={
                "Host": central_ui_fqdn,
                "X-Csrf-Token": csrf_token,
                "Origin": central_ui_url,
                "Dnt": "1",
                "Referer": central_ui_url + "/frontend/",
                "Cookie": cookiejar,
            },
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    timestamp = datetime.now().isoformat(' ', 'seconds')
    central.authentication.database.database_updatetokens_frontend(customer_id, csrf_token, csrf_session_token,
                                                                   csrf_admin_token, csrf_admin_global_session_token, timestamp)

    return csrf_token, csrf_session_token
