import csv
import itertools
import json
import os
import random
import string
import time
from datetime import datetime
from os import path

import central.authentication.central_auth
import central.authentication.database
import pandas as pd
import requests
from requests_toolbelt import MultipartEncoder

#### Global Parameters START ##
central_instance = str(central.authentication.check_config.central_instance)
central_portal = str(central.authentication.check_config.central_portal)
central_ui_url = str(central.authentication.check_config.central_ui_url)
app_customerid = str(central.authentication.check_config.app_customerid)
app_username = str(central.authentication.check_config.app_username)
app_password = str(central.authentication.check_config.app_password)
app_clientid = str(central.authentication.check_config.app_clientid)
app_clientsecret = str(central.authentication.check_config.app_clientsecret)


def set_header_frontend():
    central_xcsrf, central_xcsrf_session, central_xcsrf_admin, central_xcsrf_admin_session = central.authentication.database.database_lookup_frontend()
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:81.0) Gecko/20100101 Firefox/81.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip",
        "X-Csrf-Token": central_xcsrf,
        "Cookie": "csrftoken=" + central_xcsrf + "; session=" + central_xcsrf_session,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
        "Origin": central_portal,
        "Dnt": "1",
        "Connection": "keep-alive",
        "Referer": central_ui_url + "/frontend/",
        "Sec-Gpc": "1",
    }


def set_header_backend():
    central_xcsrf, central_xcsrf_session, central_token_access = central.authentication.database.database_lookup()
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Authorization": "Bearer "+central_token_access,
        "Content-Type": "application/json; charset=utf-8",
    }


def set_header_frontend_admin():
    central_xcsrf, central_xcsrf_session, central_xcsrf_admin, central_xcsrf_admin_session = central.authentication.database.database_lookup_frontend()
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:81.0) Gecko/20100101 Firefox/81.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json;charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": central_portal,
        "Dnt": "1",
        "Connection": "keep-alive",
        "Referer": central_portal + "/platform/frontend/",
        "X-Csrf-Token": central_xcsrf_admin,
        "Cookie": "global-session=" + central_xcsrf_admin_session + "; " + "csrftoken=" + central_xcsrf_admin,
        "Sec-Gpc": "1",
        "Te": "Trailers",
    }
