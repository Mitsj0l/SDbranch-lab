import central.authentication.database
import central.authentication.check_config
import requests, pickle
import json
from datetime import datetime
import httplib2
import urllib
import hyper
from hyper.contrib import HTTP20Adapter
import ast
import urllib.parse as urlparse
from urllib.parse import parse_qs
from requests.models import PreparedRequest
from bs4 import BeautifulSoup


session = requests.session()
username = central.authentication.check_config.app_username
password = central.authentication.check_config.app_password
customer_id = central.authentication.check_config.app_customerid

central_portal = str(central.authentication.check_config.central_portal)
central_portal_fqdn = str(central.authentication.check_config.central_portal_fqdn)
central_instance = str(central.authentication.check_config.central_instance)
central_ui_url = str(central.authentication.check_config.central_ui_url)
central_ui_fqdn = str(central.authentication.check_config.central_ui_fqdn)


def frontend_auth():
    print("Starting the frontend token retrieval")
####################################################################################
##  1st API call - check if username exists
####################################################################################
    try:
        print("1 - Check if username exists")
        response = requests.post(
            url=central_portal + "/platform/login/validate/userid",
            headers={
                "Host": central_portal_fqdn,
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": central_portal,
                "X-Requested-With": "XMLHttpRequest",
                "Accept-Language": "en-us",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Accept-Encoding": "gzip",
            },
            data={
                "userid": username ,
                "language": "en_US",
            },
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')



    # r = session.post(url, data=payload, headers=header)
####################################################################################
##  2nd API call - Post SSO and Receive SSO URL Params
####################################################################################
    try:
        print("2 - Post SSO and Receive SSO URL Params")
        url=central_portal + "/platform/login/aruba/sso"
        session.mount(url, HTTP20Adapter())
        response1 = session.post(
            url=url,
            params={
                "username": username,
            },
            headers={
                "Host": central_portal_fqdn,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                # "Origin": "https://internal-portal.central.arubanetworks.com",
                "Accept-Language": "en-us",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                # "Referer": "https://internal-portal.central.arubanetworks.com/platform/login/user",
            },
            data={
                "pf.username": username,
            },
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response1.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response1.content))
        # print(response1.cookies)
        # print(response1.cookies.get_dict)
        # print(response1.headers)

        response1_header = dict(response1.headers)

        location_url = response1_header[b'location'].decode('utf-8')
        global_session = response1_header[b'set-cookie'].decode('utf-8')
        # print(location_url)
        # print(global_session)

        base_hostname = urlparse.urlparse(location_url).hostname
        base_path = urlparse.urlparse(location_url).path
        base_server = "https://"+base_hostname+base_path
        base_query = urlparse.urlparse(location_url)

        # print(base_hostname)
        # print(base_path)

        # print("Hello")
        # print(parse_qs(base_query.query))
        params_new = parse_qs(base_query.query)

        url_new = "https://nu.nl/"

        req = PreparedRequest()
        req.prepare_url(url_new, params_new)
        # print(req.url)


    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
##  3rd API call - Get SSO URL + Tokens
####################################################################################

    try:
        print("3 - Get SSO URL + Tokens")
        session.mount(base_server, HTTP20Adapter())

        response3 = session.get(
            url=base_server ,
            params=params_new,
            headers={
                "Host": "sso.arubanetworks.com",
                # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                # "Accept-Language": "en-us",
                "Referer": central_portal +"/platform/login/user",
                # "Accept-Encoding": "gzip",
                "Cookie": global_session,
            },
        )
        # print(response2.headers)
        # print(response2.cookies)
        # print(response2.headers.values)
        # print(response2.raw.headers)

        # raw_response = response3.raw.headers
        # test = response2.raw.headers['set-cookie'][0].decode('utf-8')
        cookie0 = response3.raw.headers['set-cookie'][0].decode('utf-8')
        cookie1 = response3.raw.headers['set-cookie'][1].decode('utf-8')
        cookie2 = response3.raw.headers['set-cookie'][2].decode('utf-8')
        cookie3 = response3.raw.headers['set-cookie'][3].decode('utf-8')
        cookiejar = cookie0+"; "+cookie1+"; "+cookie2+"; "+cookie3

        # cookie_jar_3rd_API = []
        location_3rd_API = response3.headers[b'location'].decode('utf-8')
        # cj = http.cookiejar.CookieJar()
        # for x in range(0, len(raw_response['set-cookie'])):
        #     tester = raw_response['set-cookie'][x].decode('utf-8')
        #     cookie_jar_3rd_API.append(tester)
        #     cookie = http.cookiejar.Cookie(tester)

        # cj.set_cookie(cookie)
        # print("\n\n\nThis is the Cookie Jar:\n\n\n")
        # print(cookie_jar_3rd_API)
        # print(cj)

        # print("\n\n\nAPI-call3")
        # print(response4.headers)
        # print(response4.cookies)
        # print(response4.headers.values)
        # print(response4.raw.headers)


        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response3.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response3.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')



####################################################################################
##  4th API call - GET SSO
####################################################################################


    try:
        print("4 - Get SSO to user-mapping")
        session.mount(location_3rd_API, HTTP20Adapter())
        response4 = session.get(
            url=location_3rd_API,
            headers={
                "Host": "sso.arubanetworks.com",
                "Cookie": cookiejar,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Accept-Language": "en-us",
                "Referer": central_portal,
                "Accept-Encoding": "gzip",
            },
        )

        # print(response4.url)
        # print(response4.headers)
        # # print(response4.cookies)
        # print(response4.headers.values)
        # print(response4.raw.headers)

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response4.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response4.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    # print(location_3rd_API)
    # print(cookiejar)


###################################################################################
#  5th API call - POST Credentials to IDP
###################################################################################

    try:
        print("5 - POST Credentials to IDP")
        session.mount(location_3rd_API, HTTP20Adapter())
        response5 = session.post(
            url=location_3rd_API,
            headers={
                "Host": "sso.arubanetworks.com",
                "Cookie": cookiejar,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://sso.arubanetworks.com",
                "Accept-Language": "en-us",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Referer": "https://sso.arubanetworks.com/",
                "Accept-Encoding": "gzip",
            },
            data={
                "pf.ok": "",
                "pf.cancel": "",
                "pf.username": username,
                "pf.pass": password,
            },
        )
        # print(response5.headers)
        # print(response5.cookies)
        # print(response5.headers.values)
        # print(response5.raw.headers)
        # print(cookiejar)
        # print(response5.url)
        # print(response5.cookies)

        # raw_response = response5.raw.headers
        cookie0 = response5.raw.headers['set-cookie'][0].decode('utf-8')
        cookie1 = response5.raw.headers['set-cookie'][1].decode('utf-8')
        cookie2 = response5.raw.headers['set-cookie'][2].decode('utf-8')
        cookiejar = cookie0+"; "+cookie1+"; "+cookie2
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
##  6th API call - POST SSO ACS
####################################################################################
    try:
        print("6 - Post to SSO ACS")
        api_6th_url = "https://sso.arubanetworks.com/sp/ACS.saml2"
        session.mount(api_6th_url, HTTP20Adapter())
        response6 = session.post(
            url=api_6th_url,
            headers={
                "Host": "sso.arubanetworks.com",
                "Cookie": cookiejar,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://sso.arubanetworks.com",
                "Accept-Language": "en-us",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Referer": "https://sso.arubanetworks.com/",
                "Accept-Encoding": "gzip",
            },
           data={
                "RelayState": central_portal +"/platform/login/user",
                "SAMLResponse":saml_code})


        # print(response6.headers)
        # print(response6.cookies)
        # print(response6.headers.values)
        # print(response6.raw.headers)

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
##  7th API call - POST to Aruba Central
####################################################################################

    try:
        print("7 - Logging into Central")
        # print("Old global session token: ",global_session)
        api_7th_url = central_portal + "/platform/login/user"
        session.mount(api_7th_url, HTTP20Adapter())
        response7 = session.post(
            url=api_7th_url,
            headers={
                "Host": central_portal_fqdn,
                "Cookie": global_session,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://sso.arubanetworks.com",
                "Accept-Language": "en-us",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Referer": "https://sso.arubanetworks.com/",
                "Accept-Encoding": "gzip",
            },
            data={
                "REF": ref_code,
                "TargetResource": api_7th_url,
            },
        )
        # print(response7.headers)
        # print(response7.cookies)
        # print(response7.headers.values)
        # print(response7.raw.headers)
        raw_response = response7.raw.headers
        cookie0 = response7.raw.headers['set-cookie'][0].decode('utf-8')
        cookie1 = response7.raw.headers['set-cookie'][1].decode('utf-8')
        cookiejar = cookie0+"; "+cookie1

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')



####################################################################################
##  8th API call - Redirect to Customer portal
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
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Origin": "https://sso.arubanetworks.com",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Accept-Language": "en-us",
                "Referer": "https://sso.arubanetworks.com/",
                "Accept-Encoding": "gzip",
            },
        )

        # print(response8.raw.headers)
        # raw_response = response8.raw.headers
        # cookie0 = response8.raw.headers['set-cookie'][0].decode('utf-8')
        # cookie1 = response8.raw.headers['set-cookie'][1].decode('utf-8')
        # cookiejar = cookie0+"; "+cookie1

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response8.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response8.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
##  9th API call - Getting Permissions from customer portal
####################################################################################

    try:
        print("9 - Getting Permissions from customer portal")
        # print(cookiejar)
        api_9th_url = central_portal + "/platform/login/customers"
        session.mount(api_9th_url, HTTP20Adapter())
        response9 = requests.get(
            url=api_9th_url,
            headers={
                "Host": central_portal_fqdn,
                "Cookie": cookiejar,
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Accept-Language": "en-us",
                "Referer": central_portal + "/platform/login/redirect/customer",
                "Accept-Encoding": "gzip",
            },
        )
        # print(response9.headers)
        # print(response9.cookies)
        # print(response9.headers.values)
        # print(response9.raw.headers)

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response9.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response9.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    customerlist = response9.json()
    # print(customerlist)
    print("Logged in user: ",customerlist['email_id'])
    print("The account has permission to the following accounts:")
    for i in range(0, len(customerlist['customers_list'])):
        email = customerlist['customers_list'][i]['email']
        cid = customerlist['customers_list'][i]['id']
        name = customerlist['customers_list'][i]['name']
        print("CID: ",cid," - Email: ",email," - Name: ",name)




####################################################################################
##  10th API call - Selecting the user Frontend account in Admin panel
####################################################################################

    try:
        print("10 - Selecting the user Frontend account in Admin panel")
        # print(cookiejar)
        api_10th_url = central_portal + "/platform/login/customers/selection"
        session.mount(api_10th_url, HTTP20Adapter())
        response10 = requests.post(
            url=api_10th_url,
            headers={
                "Host": central_portal_fqdn,
                "Cookie": cookiejar,
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json;charset=utf-8",
                # "Origin": "https://internal-portal.central.arubanetworks.com",
                "Accept-Language": "en-us",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                # "Referer": "https://internal-portal.central.arubanetworks.com/platform/login/redirect/customer",
                "Accept-Encoding": "gzip",
            },
            data=json.dumps({
                "cid": customer_id
            })
        )
        print("Selected Customer Account ID (CID): ",customer_id)
        # print(response10.headers)
        # print(response10.cookies)
        # print(response10.headers.values)
        # print(response10.raw.headers)
        csrf_admin_token = response10.cookies['csrftoken']
        csrf_admin_global_session_token = response10.cookies['global-session']
        # print(csrf_admin_token)
        # print(csrf_admin_global_session_token)

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response10.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response10.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
##  11th API call - Get Token for Admin UI Frontend
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
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Accept-Language": "en-us",
                "Referer": central_portal+"/platform/login/redirect/customer",
                "Accept-Encoding": "gzip",
            },
        )

        # print(response11.headers)
        # print(response11.cookies)
        # print(response11.headers.values)
        # print(response11.raw.headers)

        cookie0 = response11.headers['Set-Cookie']
        # cookie1 = response11.raw.headers['set-cookie'][1].decode('utf-8')
        # cookiejar = cookie0+"; "+cookie1
        cookiejar = cookie0
        # print("\n\n\n",cookiejar,"\n\n\n")

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response11.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response11.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
##  12th API call - Get Token for NMS
####################################################################################

    try:
        print("12 - Get Token for NMS App")
        # print(cookiejar)
        api_12th_url = central_portal + "/platform/login/apps/nms/launch"

        session.mount(api_12th_url, HTTP20Adapter())
        response12 = session.get(
            url=api_12th_url,
            params={
                "_": "1588875095939",
            },
            headers={
                "Host": central_portal_fqdn,
                "Cookie": cookiejar,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Accept-Language": "en-us",
                "Referer": central_portal+"/platform/frontend/",
                "Accept-Encoding": "gzip",
            },
        )
        # print(response12.raw.headers)
        # print(response12.raw.headers['location'])
        # print(response12.raw.headers['set-cookie'])


        # print(response12.cookies)

        # print(response12.raw.headers['set-cookie'])
        cookie0 = response12.raw.headers['set-cookie'][0].decode('utf-8')

        # print(cookie0)
        # # cookie0 = response12.raw.headers['set-cookie'][0
        # # cookie1 = response12.raw.headers['set-cookie'][1].decode('utf-8')
        # # cookiejar = cookie0+"; "+cookie1
        # cookiejar = cookie0
        location_url = response12.raw.headers['location'][0].decode('utf-8')
        # print(location_url)


        # base_hostname = urlparse.urlparse(location_url).hostname
        # base_path_ott = urlparse.urlparse(location_url).path
        base_server = "https://"+base_hostname+base_path
        base_query = urlparse.urlparse(location_url)
        # print(parse_qs(base_query.query))
        params_new = parse_qs(base_query.query)
        # print(params_new)
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response12.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response12.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


####################################################################################
##  13th API call - Get Session Token for frontend new XCSRF Tokens
####################################################################################

    try:
        print("13 - Redirecting to Central NMS Frontend")
        # print(cookiejar)

        api_13th_url = central_ui_url+"/login"

        session.mount(api_13th_url, HTTP20Adapter())
        response13 = session.get(
            url=api_13th_url,
            params=params_new
            ,
            headers={
                # "Host": central_ui_fqdn,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Accept-Language": "en-us",
                "Referer": central_portal+"/platform/frontend/",
                "Accept-Encoding": "gzip",
                # "Cookie": cookiejar,
            },
        )

        # print(response13.headers)
        # print(response13.cookies)
        # print(response13.headers.values)
        # print(response13.raw.headers)

        cookie0 = response13.raw.headers['set-cookie'][0].decode('utf-8')
        cookiejar = cookie0
        location_url = response13.raw.headers['location'][0].decode('utf-8')
        # print("\n\n\n",cookiejar,"\n\n\n")
        # print("\n\n\n",cookiejar,"\n\n\n")
        # print(location_url)

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response13.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response13.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

####################################################################################
##  14th API call - Get XCSRF Token for frontend
####################################################################################
    try:
        print("14 - Get XCSRF Token for frontend")
        # print(cookiejar)
        api_14th_url = location_url

        session.mount(api_14th_url, HTTP20Adapter())
        response14 = requests.get(
            url=api_14th_url,
            headers={
                "Host": central_ui_fqdn,
                "Cookie": cookiejar,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1",
                "Accept-Language": "en-us",
                "Referer": central_portal+"/platform/frontend/",
                "Accept-Encoding": "gzip",
            },
        )
        # print(response14.headers)
        # print(response14.cookies)
        # print(response14.cookies['csrftoken'])
        # print(response14.headers.values)
        # print(response14.raw.headers)
        csrf_token = response14.cookies['csrftoken']
        csrf_session_token = response14.cookies['session']
        print("This is my final Frontend NMS CSRF token: ", csrf_token)
        print("This is my final Frontend NMS CSRF Session token: ", csrf_session_token)
        cookiejar = "csrftoken=" + csrf_token + "; session=" + csrf_session_token

        # cookie0 = response7.raw.headers['set-cookie'][0].decode('utf-8')
        # cookie1 = response7.raw.headers['set-cookie'][1].decode('utf-8')
        # cookiejar = cookie0+"; "+cookie1
        # # cookiejar = cookie0
        # print(cookiejar)
        # print(cookie0)
        # print(cookie1)
        # print(type(cookie0))

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response14.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response14.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


    print("15 - Request Central Keep-alive")
    # print(cookiejar)
    # api_15th_url = "https://internal-ui.central.arubanetworks.com/admin/user/keepalive"

    # session.mount(api_15th_url, HTTP20Adapter())
    try:
        api_15th_url = central_ui_url+"/admin/user/keepalive"
        # print(cookiejar)
        # print(csrf_token)

        response = requests.post(
            url=api_15th_url,
            headers={
                "Host": central_ui_fqdn,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:75.0) Gecko/20100101 Firefox/75.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
                "X-Newrelic-Id": "VgQAVlFQCRADVVVQBwkFV1Q=",
                "X-Requested-With": "XMLHttpRequest",
                "X-Csrf-Token": csrf_token,
                "Origin": central_ui_url,
                "Dnt": "1",
                "Referer": central_ui_url+"/frontend/",
                "Cookie": cookiejar,
                "Te": "Trailers",
                "Accept-Encoding": "gzip",
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
