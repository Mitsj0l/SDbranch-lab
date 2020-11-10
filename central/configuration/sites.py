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
import central.configuration.headers as headers
import pandas as pd
import requests
from requests_toolbelt import MultipartEncoder


def sites_get():
    try:
        print("Retrieving Site locations")
        response = requests.get(
            url=headers.central_instance + "/central/v2/sites",
            headers=headers.set_header_backend(),
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        sites_list_json = response.json()
        sites = pd.json_normalize(sites_list_json['sites'])
        # print(sites)
        return(sites)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def sites_assigndevice(site_id, serial_number):
    try:
        print("Associating device: {} to location_ID: {} .".format(
            serial_number, site_id))
        response = requests.post(
            url=headers.central_instance + "/central/v2/sites/associate",
            headers=headers.set_header_backend(),
            data=json.dumps({
                "site_id": site_id,
                "device_type": "CONTROLLER",
                "device_id": serial_number
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def sites_bulkupload():
    filename = "sample_Sites"
    csv_temp_upload = "./central/config/{}.csv".format(filename)
    print("Receiving Locations from : {}".format(csv_temp_upload))
    df = pd.read_csv(csv_temp_upload)
    print(df)
    for (idx, row) in df.iterrows():
        site_name = row.loc['name']
        site_address = row.loc['address']
        site_city = row.loc['city']
        site_state = row.loc['state']
        site_country = row.loc['country']
        site_zipcode = row.loc['zipcode']
        try:
            print("Creating site location: {} - {} - {}.".format(site_name,
                                                                 site_address, site_country))
            response = requests.post(
                url=headers.central_instance + "/central/v2/sites",
                headers=headers.set_header_backend(),
                data=json.dumps({
                    "site_address": {
                        "state": site_state,
                        "country": site_country,
                        "city": site_city,
                        "zipcode": site_zipcode,
                        "address": site_address
                    },
                    "site_name": site_name,
                    # "geolocation": {
                    #     "longitude": "-77.0364",
                    #     "latitude": "38.8951"
                    # }
                })

            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            # print('Response HTTP Response Body: {content}'.format(
            #     content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')


def sites_delete():
    print("Removing Site locations of SDBranch Script")
    sites = central.configuration.sites.sites_get()
    print(sites)
    # Filtering "SDB-" Keyword in the Site names and then receive the site_id's of those entries.
    site_location_ids = sites['site_id'][sites['site_name'].str.contains(
        "SDB-")].tolist()
    # print(site_location_ids)

    for site in site_location_ids:
        try:
            print("Deleting Site location ID: {}".format(site))
            response = requests.delete(
                url=headers.central_instance +
                "/central/v2/sites/{}".format(site),
                headers=headers.set_header_backend(),
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
