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


def get_vgw():
    try:
        response = requests.get(
            url=headers.central_ui_url + "/cgw/vgw_instances/unmanaged",
            headers=headers.set_header_frontend(),
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        vvgw_inventory_json = response.json()
        df2 = pd.json_normalize(
            vvgw_inventory_json['deployments'][0]['vgw_devices'])
        # print(df2)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
    return(df2)


def get_vgw_monitoring():
    try:
        response = requests.get(
            url=headers.central_instance + "/monitoring/v1/mobility_controllers",
            headers=headers.set_header_backend(),
            params={
                "model": "ArubaVGW",
            }
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        vvgw_inventory_json = response.json()
        # When VGW's have never been online the model status is "MC-VA". If devices have ever been online, they have the model "ArubaVGW".
        if vvgw_inventory_json['count'] == 0:
            try:
                response = requests.get(
                    url=headers.central_instance + "/monitoring/v1/mobility_controllers",
                    headers=headers.set_header_backend(),
                    params={
                        "model": "MC-VA",
                    }
                )
                # print('Response HTTP Status Code: {status_code}'.format(
                #     status_code=response.status_code))
                # print('Response HTTP Response Body: {content}'.format(
                #     content=response.content))
                vvgw_inventory_json = response.json()
                print(vvgw_inventory_json['count'])
                if vvgw_inventory_json['count'] == 0:
                    print("No VGW's found!")
                    return(False)
                df2 = pd.json_normalize(vvgw_inventory_json['mcs'])
                return(df2)
            except requests.exceptions.RequestException:
                print('HTTP Request failed')
        df2 = pd.json_normalize(vvgw_inventory_json['mcs'])
        return(df2)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def create_vgw():
    print("Creating Virtual Gateways")
    try:
        response = requests.post(
            url=headers.central_ui_url + "/cgw/vgw_topology/deploy",
            headers=headers.set_header_frontend(),
            data=json.dumps({
                "topology": {

                },
                "config": {
                    "bw_sku": "VGW-500MB"
                },
                "metadata": {
                    "managed": False
                }
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        # admin_inventory_json = response.json()
        # df2 = pd.json_normalize(admin_inventory_json)
        # print(df2)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def delete_vgw_monitoring():
    vgws = get_vgw_monitoring()
    for serial_number in vgws['serial']:
        try:
            print("Deleting VGW with Serial Number: {}".format(serial_number))
            response = requests.delete(
                url=headers.central_instance +
                "/monitoring/v1/mobility_controllers/{}".format(serial_number),
                headers=headers.set_header_backend()
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        time.sleep(1)


def delete_vgw_services():
    print("Deleting Virtual Gateways:")
    get_vgws = get_vgw()
    for vgw_id in get_vgws['vgw_id']:
        try:
            response = requests.delete(
                url=headers.central_ui_url +
                "/cgw/vgw_instances/{}".format(vgw_id),
                headers=headers.set_header_frontend()
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        time.sleep(3)


def download_vgw_userdata(vgw_id, serial_number, device_name):
    try:
        response = requests.get(
            url=headers.central_ui_url +
            "/cgw/vgw_instances/{}/user_data/download_iso".format(vgw_id),
            headers=headers.set_header_frontend(),
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        # content=response.content))
        filename = device_name+"-"+serial_number+".iso"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print("Downloaded ISO VGW userdata-file: "+filename)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
