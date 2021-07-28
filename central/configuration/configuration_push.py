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


def config_device(filename, device_name, serial_number, mac_address):
    try:
        print("Push the per-device configuration to device {} - {} - {} .".format(
            device_name, serial_number, mac_address))
        response = requests.post(
            url=headers.central_instance + "/caasapi/v1/exec/cmd",
            params={
                "cid": headers.app_customerid,
                "node_name": mac_address,
            },
            headers=headers.set_header_backend(),
            data=filename
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        return(response.status_code)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def skip_wizard(mac_address):
    try:
        response = requests.post(
            url=headers.central_ui_url + "/caas/v1/configuration/object",
            headers=headers.set_header_frontend(),
            params={
                "commit": "True",
                "node_name": mac_address,
                "action": "cancel",
                "wizard": "true",
            },
            data=json.dumps({
                "state_data": {
                    "simplified_sdwan": {
                        "wizard_state": 0,
                        "section": "",
                        "module_data": {
                            "peer_node_id": "",
                            "gateway_model": ""
                        },
                        "step": "",
                        "version": "V1"
                    }
                },
                "config_data": {

                }
            })
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def groupconfig_create(central_group_name):
    for groupname in central_group_name:

        # Config file locations
        filename_directory = "./central/config/{}.txt".format(groupname)
        filename_open = open(filename_directory, "r")
        filename = filename_open.read()
        # print(bgw_csv2)
        try:
            print("Pushing group configuration of filename {} to Central group {}.".format(
                filename_directory, groupname))
            response = requests.post(
                url=headers.central_instance + "/caasapi/v1/exec/cmd",
                params={
                    "cid": headers.app_customerid,
                    "group_name": groupname,
                },
                headers=headers.set_header_backend(),
                data=filename
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            # print('Response HTTP Response Body: {content}'.format(
            #     content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
