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


def label_create(label):
    try:
        # print("Creating Labels")
        response = requests.post(
            url=headers.central_instance + "/central/v1/labels",
            headers=headers.set_header_backend(),
            data=json.dumps({
            "category_id": 1,
            "label_name": label
            })
        )
        label_list_json = response.json()
        print(label, label_list_json['label_id'])
        label_id = label_list_json['label_id']
        return(label_id)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def label_get():
    try:
        print("Retrieving Site locations")
        response = requests.get(
            url=headers.central_instance + "/central/v2/labels",
            headers=headers.set_header_backend(),
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        label_list_json = response.json()
        # sites = pd.json_normalize(sites_list_json['sites'])
        # print(label_list_json)
        return(label_list_json['labels'])
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def label_assigndevice(label_id, serial_number):
    try:
        print("Associating device(s): {} to label: {} .".format(
            serial_number, label_id))
        response = requests.post(
            url=headers.central_instance + "/central/v2/labels/associations",
            headers=headers.set_header_backend(),
            data=json.dumps({
            "label_id": label_id,
            "device_type": "CONTROLLER",
            "device_ids": serial_number
            })
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def labels_delete():
    print("Removing Labels of SDBranch Script")
    labels = label_get()
    if not labels:
        print("No labels defined.")
        return(None)
    for i in range(0, len(labels)):
        label_name = labels[i]['label_name']
        label_id = labels[i]['label_id']        
        if label_name.find("SDB") != -1:
            try:
                print("Deleting Label {} with ID: {}".format(label_name, label_id))
                response = requests.delete(
                    url=headers.central_instance +
                    "/central/v1/labels/{}".format(label_id),
                    headers=headers.set_header_backend(),
                )
                print('Response HTTP Status Code: {status_code}'.format(
                    status_code=response.status_code))
                print('Response HTTP Response Body: {content}'.format(
                    content=response.content))
            except requests.exceptions.RequestException:
                print('HTTP Request failed')
