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
import central.configuration.configuration_push
import central.configuration.groups
import central.configuration.labels
import central.configuration.headers as headers
import central.configuration.sites
import central.configuration.vgw
import pandas as pd
import requests
from requests_toolbelt import MultipartEncoder

central_group_hubmesh = "SDB-HUB_MESH"
central_group_branchmesh = "SDB-BRANCH_MESH"
central_group_bgw = "SDB-Branch"
central_group_vpnc = "SDB-DC"
central_group_vpnc1 = "SDB-DC1"
central_group_vpnc2 = "SDB-DC2"
central_group_name = [central_group_bgw,
                      central_group_vpnc1, central_group_vpnc2]


def Assignment_VGW(array_central_group_bgw, array_central_group_vpnc1, array_central_group_vpnc2):
    VGW_Inventory = central.configuration.vgw.get_vgw()
    print("Assigning the following devices:\n")
    print(array_central_group_bgw)
    print(array_central_group_vpnc1)
    print(array_central_group_vpnc2)
    central_group_id = [array_central_group_vpnc1[0][1], array_central_group_vpnc2[0][1],
                        array_central_group_bgw[0][1], array_central_group_bgw[0][1]]  # Retrieve 2nd Array object the group_id
    central_group_name = [array_central_group_vpnc1[0][0], array_central_group_vpnc2[0][0],
                          array_central_group_bgw[0][0], array_central_group_bgw[0][0]]  # Retrieve 1st Array object the group_name
    print(central_group_id)
    print(central_group_name)
    central_device_name = ['VPNC3', 'VPNC4', 'BGW1', 'BGW2']
    central_site_name = ['SDB-DC1', 'SDB-DC2', 'SDB-Branch1', 'SDB-Branch2']

    VGW_Inventory['group_name'] = central_group_name
    VGW_Inventory['group_id'] = central_group_id
    VGW_Inventory['device_name'] = central_device_name
    VGW_Inventory['site_name'] = central_site_name

    print("VPNC's")
    print(VGW_Inventory[['device_name', 'serial_number',
                         'mac_address', 'group_name', 'group_id']].head(2))
    print("\nBGW's")
    print(VGW_Inventory[['device_name', 'serial_number',
                         'mac_address', 'group_name', 'group_id']].tail(2))

    sites_locations = central.configuration.sites.sites_get()
    # Merging two Pandas dataframes to match the site_names to include the site_ID of the sites_get Function
    VGW = VGW_Inventory.merge(sites_locations, how='inner', left_on=[
                              "site_name"], right_on=["site_name"])

    for (idx, row) in VGW.iterrows():
        vgw_id = row.loc['vgw_id']
        serial_number = row.loc['serial_number']
        mac_address = row.loc['mac_address']
        group_name = row.loc['group_name']
        group_id = row.loc['group_id']
        device_name = row.loc['device_name']
        site_id = row.loc['site_id']
        print(device_name, serial_number, mac_address, group_name)

        # Config file locations
        filename_directory = "./central/config/{}.txt".format(device_name)
        filename_open = open(filename_directory, "r")
        filename = filename_open.read()
        # print(bgw_csv2)
        # Download the VGW ISO User-Data.txt files.
        central.configuration.vgw.download_vgw_userdata(
            vgw_id, serial_number, device_name)
        print("\n\n\n")
        print("Sleeping 30 seconds to make sure that the device is added to Central Monitoring Instance - this varies per cid...")
        # Assign function VPNC and BGW's to the right group.
        # central.configuration.groups.group_preassignment(
            # serial_number, group_id) # This function should be deprecated once Central 2.5.3 is being used.
        central.configuration.groups.group_move(serial_number, group_name) # Central 2.5.3 automatically assigns VGW to Default group. Hence the Frontend Admin pre-assignment cannot be used and the backend Group Move function should be used. 
        # Response HTTP Status Code: 500 can be normal... with a group move....
        
        time.sleep(30)
        # Assign device to monitoring location. This also needs some timing of 10 seconds.
        central.configuration.sites.sites_assigndevice(site_id, serial_number)

        # Push the per-device configuration.
        push_config = central.configuration.configuration_push.config_device(
            filename, device_name, serial_number, mac_address)
        if push_config==200:
            None
        elif push_config==500:
            central.configuration.configuration_push.config_device(
            filename, device_name, serial_number, mac_address)
            
        # Initiating the removal of the first setup wizard screen
        central.configuration.configuration_push.skip_wizard(mac_address)



def sdwan_config():
    print("Creating the SDWAN Service configs (Hub-Mesh, Branch Mesh, Network Segments).")
    VGW_Inventory = central.configuration.vgw.get_vgw()
    # Selecting the two VPNC's and extracting their Serial numbers.
    serial_number_vpnc1 = VGW_Inventory['serial_number'].head(2).iloc[0]
    serial_number_vpnc2 = VGW_Inventory['serial_number'].head(2).iloc[1]
    
    # Selecting the two BGW's and extracting their Serial numbers.
    serial_number_bgw1 = VGW_Inventory['serial_number'].tail(2).iloc[0]
    serial_number_bgw2 = VGW_Inventory['serial_number'].tail(2).iloc[1]
    
    # Pushing the SDWAN HUB config to the Spokes group "SDB-Branch"
    central.configuration.groups.groupconfig_sdwanhub(
        central_group_bgw, serial_number_vpnc1, serial_number_vpnc2)

    central.configuration.groups.groupconfig_sdwanbranchmesh(
        central_group_branchmesh, serial_number_bgw1, serial_number_bgw2)
    
    central.configuration.groups.groupconfig_sdwanmesh(central_group_hubmesh)
    central.configuration.groups.groupconfig_sdwanmesh_link(
        central_group_hubmesh, central_group_vpnc1, central_group_vpnc2)
    

    # Assigning Labels to devices
    label_name_VPNC = "SDB - VPNC's"
    label_name_BGW = "SDB - Branch Gateways"
    VPNCs = [serial_number_vpnc1, serial_number_vpnc2]
    BGWs = [serial_number_bgw1, serial_number_bgw2]
    label_id_vpnc = central.configuration.labels.label_create(label_name_VPNC)
    label_id_bgw = central.configuration.labels.label_create(label_name_BGW)
    central.configuration.labels.label_assigndevice(label_id_vpnc, VPNCs)
    central.configuration.labels.label_assigndevice(label_id_bgw, BGWs)
    
    
    
        
        

def start_script():
    # Create 4 VGW's
    for _ in itertools.repeat(None, 4):
        central.configuration.vgw.create_vgw()
        print("Sleeping 12 seconds to make sure the job is started.")
        time.sleep(12)
    # List the VGW's
    print("These VGW's are created: \n{}".format(
        central.configuration.vgw.get_vgw()))
    print("Sleeping 10 seconds to make sure all devices are really added")
    time.sleep(10)

    # Create Group
    central.configuration.groups.group_create(central_group_name)
    # Retrieve Group_ID
    group_list = central.configuration.groups.get_group_id()
    print(group_list)
    # Push the group DC and Branch config to Central
    central.configuration.configuration_push.groupconfig_create(
        central_group_name)

    # #Set persona's of the groups:
    central.configuration.groups.groupconfig_persona_bgw(central_group_bgw)
    central.configuration.groups.groupconfig_persona_vpnc(central_group_vpnc1)
    central.configuration.groups.groupconfig_persona_vpnc(central_group_vpnc2)

    # #Numpy matching to Variable
    match_central_group_bgw = group_list[group_list['group_name'].str.match(
        central_group_bgw)]
    match_central_group_vpnc1 = group_list[group_list['group_name'].str.match(
        central_group_vpnc1)]
    match_central_group_vpnc2 = group_list[group_list['group_name'].str.match(
        central_group_vpnc2)]

    # #Numpy Array of Variable: [SDB-DC4, 50]
    array_central_group_bgw = match_central_group_bgw[[
        "group_name", "groupid"]].values
    array_central_group_vpnc1 = match_central_group_vpnc1[[
        "group_name", "groupid"]].values
    array_central_group_vpnc2 = match_central_group_vpnc2[[
        "group_name", "groupid"]].values
    print(array_central_group_bgw)
    print(array_central_group_vpnc1)
    print(array_central_group_vpnc2)

    # #Create Site monitoring Locations
    central.configuration.sites.sites_bulkupload()
    Assignment_VGW(array_central_group_bgw,
                   array_central_group_vpnc1, array_central_group_vpnc2)
    sdwan_config()
    
    #Enforce Firmware Compliance
    print("Setting Firmware compliance")
    central.configuration.groups.group_firmwarelevel()


def delete_script():
    print("Inititiating Deletion of the created config by this script (VGW's, Group and Sites)")
    get_vgws = central.configuration.vgw.get_vgw()
    print(get_vgws)
    central.configuration.vgw.delete_vgw_services()
    central.configuration.vgw.delete_vgw_monitoring()
    central.configuration.groups.group_delete(central_group_name)
    central.configuration.sites.sites_delete()
    central.configuration.labels.labels_delete()
    central.configuration.groups.groupconfig_sdwanmesh_delete(
        central_group_hubmesh)
    central.configuration.groups.groupconfig_sdwanbranchmesh_delete(
        central_group_hubmesh)
    central.configuration.vgw.delete_vgw_services()

