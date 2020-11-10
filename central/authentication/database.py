import os
import sqlite3
import sys
from datetime import datetime
from os import path

import central.authentication.central_auth
import central.authentication.central_frontend_auth
import pandas as pd

# def tester():
#     central.authentication.central_auth.hello_world()

# def database_function():
#     print("This is my database")


def database_init():
    if path.exists("central/authentication/token.sqlite3") == False:
        print("Creating the local database...")
        # You can create a new database by changing the name within the quotes
        conn = sqlite3.connect('central/authentication/token.sqlite3')
        c = conn.cursor()  # The database will be saved in the location where your 'py' file is saved
        # Create table - CLIENTS
        c.execute('''CREATE TABLE CLIENTS
                     ([generated_id] INTEGER PRIMARY KEY,[Client_Token_ID] text, [Customer_ID] integer,[Client_TokenSecret_ID] text,[XCSRF_Token] text,[XCSRF_Session] text,[Authcode_Token] text,[Acess_Token] text, [Date] date)''')
        c.execute('''CREATE TABLE FrontendAPI
                     ([generated_id] INTEGER PRIMARY KEY, [Customer_ID] integer,[XCSRF_Token] text,[XCSRF_Session] text, [CSRF_ADMIN_TOKEN] text, [CSRF_ADMIN_SESSION] text, [Date] date)''')
        conn.commit()
        # central_authentication()
        central.authentication.central_auth.central_authentication()
        central.authentication.central_frontend_auth.frontend_auth()

    else:
        print("Checking if an API key is still valid...")
        conn = sqlite3.connect('central/authentication/token.sqlite3')
        c = conn.cursor()
        df1 = pd.read_sql_query(
            "SELECT * FROM CLIENTS ORDER BY generated_id DESC LIMIT 1;", conn)
        token_timestamp = df1['Date'].values[0]
        current_timestamp = datetime.now().isoformat(' ', 'seconds')
        start = __datetime(token_timestamp)
        end = __datetime(current_timestamp)
        delta = end - start
        token_timedifference = delta.total_seconds()
        # print(token_timedifference)
        if token_timedifference > 7200:
            print("Need to generate new tokens for frontend and official API")
            central.authentication.central_auth.central_authentication()
            central.authentication.central_frontend_auth.frontend_auth()
        else:
            # Retrieve stored tokens for Offical API
            get_column_names = c.execute("select * from CLIENTS limit 1")
            col_name = [i[0] for i in get_column_names.description]
            c.execute('''
             SELECT * FROM CLIENTS ORDER BY generated_id DESC LIMIT 1
                       ''')
            print("Your Backend API token is still valid: ")
            print(col_name)
            print(c.fetchall())

            # Retrieve stored tokens for Frontend API
            get_column_names = c.execute("select * from FrontendAPI limit 1")
            col_name = [i[0] for i in get_column_names.description]
            c.execute('''
             SELECT * FROM FrontendAPI ORDER BY generated_id DESC LIMIT 1
                       ''')
            print("Your Frontend API token is still valid: ")
            print(col_name)
            print(c.fetchall())


def __datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def database_updatetokens(app_clientid, app_customerid, app_clientsecret, csrf_token, csrf_session_token, authcode,
                          token_access,
                          timestamp):
    conn = sqlite3.connect('central/authentication/token.sqlite3')
    c = conn.cursor()
    c.execute('''
           SELECT  *
           FROM CLIENTS
                     ''')

    print(c.fetchall())
    df = pd.read_sql_query("select * from CLIENTS;", conn)
    print(df["Client_Token_ID"])
    params = (
        app_clientid, app_customerid, app_clientsecret, csrf_token, csrf_session_token, authcode, token_access,
        timestamp)
    c.execute("insert into CLIENTS values (null,?,?,?,?,?,?,?,?)", params)
    conn.commit()
    c.close()


def database_updatetokens_frontend(customer_id, csrf_token, csrf_session_token,
                                   csrf_admin_token, csrf_admin_global_session_token, timestamp):
    conn = sqlite3.connect('central/authentication/token.sqlite3')
    c = conn.cursor()
    params = (
        customer_id, csrf_token, csrf_session_token,
        csrf_admin_token, csrf_admin_global_session_token, timestamp)
    c.execute("insert into FrontendAPI values (null,?,?,?,?,?,?)", params)
    conn.commit()
    c.execute('''
           SELECT  *
           FROM FrontendAPI
                     ''')
    print("Added the folowing Frontend tokens in central/authentication/token.sqlite3:")
    print(c.fetchall())
    c.close()


def database_lookup():
    conn = sqlite3.connect('central/authentication/token.sqlite3')
    df1 = pd.read_sql_query(
        "SELECT * FROM CLIENTS ORDER BY generated_id DESC LIMIT 1;", conn)
    central_xcsrf = df1['XCSRF_Token'].values[0]
    central_xcsrf_session = df1['XCSRF_Session'].values[0]
    central_token_access = df1['Acess_Token'].values[0]
    return central_xcsrf, central_xcsrf_session, central_token_access


def database_lookup_frontend():
    # print("Looking up Frontend tokens:")
    conn = sqlite3.connect('central/authentication/token.sqlite3')
    df1 = pd.read_sql_query(
        "SELECT * FROM FrontendAPI ORDER BY generated_id DESC LIMIT 1;", conn)
    # print(df1)
    central_xcsrf = df1['XCSRF_Token'].values[0]
    central_xcsrf_session = df1['XCSRF_Session'].values[0]
    central_xcsrf_admin = df1['CSRF_ADMIN_TOKEN'].values[0]
    central_xcsrf_admin_session = df1['CSRF_ADMIN_SESSION'].values[0]
    return central_xcsrf, central_xcsrf_session, central_xcsrf_admin, central_xcsrf_admin_session
