import csv
import itertools
import json
import os
import random
from sqlite3.dbapi2 import version
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


def group_create(central_group_name):
    for group_name in central_group_name:
        print("Creating Group: {}".format(group_name))
        try:
            response = requests.post(
                url=headers.central_instance + "/configuration/v2/groups",
                headers=headers.set_header_backend(),
                data=json.dumps({
                    "group": str(group_name),
                    "group_attributes": {
                        "group_password": "Aruba123!",
                        "template_info": {
                            "Wired": False,
                            "Wireless": False
                        }
                    }
                })
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            # print('Response HTTP Response Body: {content}'.format(
            #     content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')


def group_delete(central_group_name):
    for group_name in central_group_name:
        print("Deleting Group: {}".format(group_name))
        try:
            response = requests.delete(
                url=headers.central_instance +
                "/configuration/v1/groups/{}".format(group_name),
                headers=headers.set_header_backend()
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            # print('Response HTTP Response Body: {content}'.format(
            #     content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')

def group_move(serial_number, group_name):
    try:
        print("Moving the VGW from the 'default' group to the intended group. Device SN: {}".format(serial_number))
        response = requests.post(
            url=headers.central_instance +
            "/configuration/v1/devices/move",
            headers=headers.set_header_backend(),
            data=json.dumps({
            "group": group_name,
            "serials": [
                serial_number
            ]
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
def get_group_id():
    try:
        response = requests.get(
            url=headers.central_ui_url + "/groups/v2/limit/50/offset/0",
            headers=headers.set_header_frontend(),
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        vvgw_inventory_json = response.json()
        df2 = pd.json_normalize(vvgw_inventory_json['groups'])
        # print(df2)
        return(df2)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def groupconfig_persona_bgw(central_group_bgw):
    try:
        print("Setting group configuration {} to SDWAN_Persona BGW.".format(
            central_group_bgw))
        response = requests.post(
            url=headers.central_ui_url + "/caas/v1/configuration/object/persona",
            params={
                "commit": "True",
                "node_name": central_group_bgw,
            },
            headers=headers.set_header_frontend(),
            data=json.dumps({
                "persona": "BG"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def groupconfig_persona_vpnc(central_group_vpnc):
    try:
        print("Setting group configuration {} to SDWAN_Persona VPNC.".format(
            central_group_vpnc))
        response = requests.post(
            url=headers.central_ui_url + "/caas/v1/configuration/object/persona",
            params={
                "commit": "True",
                "node_name": central_group_vpnc,
            },
            headers=headers.set_header_frontend(),
            data=json.dumps({
                "persona": "VPNC"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def groupconfig_sdwanhub(central_group_bgw, serial_number_vpnc1, serial_number_vpnc2):
    try:
        print("Associating SDB-Branch group to Hubs: {} and {} .".format(
            serial_number_vpnc1, serial_number_vpnc2))
        response = requests.post(
            url=headers.central_instance +
            "/sdwan-config/v1/node_list/GROUP/{}/config/branch-config/".format(
                central_group_bgw),
            headers=headers.set_header_backend(),
            data=json.dumps({
                "hubs": [
                    {
                        "identifier": serial_number_vpnc1
                    },
                    {
                        "identifier": serial_number_vpnc2
                    }
                ]
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def groupconfig_sdwanbranchmesh(central_group_branchmesh, serial_number_bgw1, serial_number_bgw2):
    try:
        print("Creating Branch-Mesh Label with the following BGW's: {} and {} .".format(
            serial_number_bgw1, serial_number_bgw2))
        response = requests.post(
            url=headers.central_instance +
            "/sdwan-config/v1/branch-mesh/{}/config/".format(
                central_group_branchmesh),
            headers=headers.set_header_backend(),
            data=json.dumps({
                "branch-devices": [
                    {
                        "identifier": serial_number_bgw1
                    },
                    {
                        "identifier": serial_number_bgw2
                    }
                ]
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def groupconfig_sdwanmesh(central_group_hubmesh):
    try:
        print("Creating the Hub-Mesh label.")
        response = requests.post(
            url=headers.central_instance +
            "/sdwan-config/v1/node_list/GLOBAL/GLOBAL/config/mesh-policy/hub-mesh/{}".format(
                central_group_hubmesh),
            headers=headers.set_header_backend(),
            data=json.dumps({
                "label": central_group_hubmesh
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def groupconfig_sdwanmesh_delete(central_group_hubmesh):
    try:
        print("Deleting the Hub-Mesh label.")
        response = requests.delete(
            url=headers.central_instance +
            "/sdwan-config/v1/node_list/GLOBAL/GLOBAL/config/mesh-policy/hub-mesh/{}/".format(
                central_group_hubmesh),
            headers=headers.set_header_backend(),
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def groupconfig_sdwanbranchmesh_delete(central_group_branchmesh):
    try:
        print("Deleting the Branch-Mesh Config.")
        response = requests.delete(
            url=headers.central_instance +
            "/sdwan-config/v1/branch-mesh/{}/config/".format(
                central_group_branchmesh),
            headers=headers.set_header_backend(),
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
def groupconfig_sdwanmesh_link(central_group_hubmesh, central_group_vpnc1, central_group_vpnc2):
    try:
        print("Linking the Hub-Mesh label between VPNC-Group {} and {}.".format(
            central_group_vpnc1, central_group_vpnc2))
        response = requests.post(
            url=headers.central_instance +
            "/sdwan-config/v1/node_list/GLOBAL/GLOBAL/config/mesh-policy/hub-mesh/{}".format(
                central_group_hubmesh),
            headers=headers.set_header_backend(),
            data=json.dumps({
                "hub-groups": [
                    {
                        "name": central_group_vpnc1
                    },
                    {
                        "name": central_group_vpnc2
                    }
                ],
                "label": central_group_hubmesh
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def group_preassignment(serial_number, group_id):
    print("Pre-Assigning Device Inventory to a group, so the VGW will become visible in Central Monitoring. Device SN: {}".format(serial_number))
    try:
        response = requests.post(
            url=headers.central_portal + "/platform/devicemanage/preassign",
            headers=central.configuration.headers.set_header_frontend_admin(),
            data=json.dumps({
                "devices": [
                    serial_number
                ],
                "group_id": group_id
            })
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def group_firmwarelevel():
    firmware_level_IAP = central.authentication.check_config.firmware_level_IAP
    firmware_level_HPPC = central.authentication.check_config.firmware_level_HPPC
    firmware_level_CX = central.authentication.check_config.firmware_level_CX
    firmware_level_GW = central.authentication.check_config.firmware_level_GW
    
    firmware_list = {"IAP" : firmware_level_IAP, "HPPC" : firmware_level_HPPC, "CX" : firmware_level_CX,  "MC" : firmware_level_GW}

    for key, value in firmware_list.items():
        try:
            # Skip empty versions!
            if not value:
                continue
            response = requests.post(
                url=headers.central_ui_url + "/firmware/customer/compliance_version",
                headers=headers.set_header_frontend(),
                data=json.dumps({
                    "delete_firmware_compliance": {},
                    "set_firmware_compliance": {
                        key:value
                    },
                    "reboot": {
                        key: "true"
                    },
                    "groups": [
                        "allGroups"
                    ],
                    "compliance_scheduled_at": 0
                    })
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
