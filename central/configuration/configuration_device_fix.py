
from datetime import datetime
from os import path
import central.authentication.central_auth
import central.authentication.database
import central.configuration.configuration_push
import central.configuration.groups
import central.configuration.headers as headers
import central.configuration.sites
import central.configuration.vgw
import pandas as pd
from requests_toolbelt import MultipartEncoder

central_group_hubmesh = "SDB-MESH"
central_group_bgw = "SDB-Branch"
central_group_vpnc = "SDB-DC"
central_group_vpnc1 = "SDB-DC1"
central_group_vpnc2 = "SDB-DC2"
central_group_name = [central_group_bgw,
                      central_group_vpnc1, central_group_vpnc2]


def config_start_script():
    # Retrieve Group_ID
    group_list = central.configuration.groups.get_group_id()
    print(group_list)

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
    DeviceConfig_Push(array_central_group_bgw,
                   array_central_group_vpnc1, array_central_group_vpnc2)

def DeviceConfig_Push(array_central_group_bgw, array_central_group_vpnc1, array_central_group_vpnc2):
    VGW_Inventory = central.configuration.vgw.get_vgw()
    # print("Assigning the following devices:\n")
    # print(array_central_group_bgw)
    # print(array_central_group_vpnc1)
    # print(array_central_group_vpnc2)
    central_group_id = [array_central_group_vpnc1[0][1], array_central_group_vpnc2[0][1],
                        array_central_group_bgw[0][1], array_central_group_bgw[0][1]]  # Retrieve 2nd Array object the group_id
    central_group_name = [array_central_group_vpnc1[0][0], array_central_group_vpnc2[0][0],
                          array_central_group_bgw[0][0], array_central_group_bgw[0][0]]  # Retrieve 1st Array object the group_name
    # print(central_group_id)
    # print(central_group_name)
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
        serial_number = row.loc['serial_number']
        mac_address = row.loc['mac_address']
        group_name = row.loc['group_name']
        device_name = row.loc['device_name']
        print(device_name, serial_number, mac_address, group_name)

        # Config file locations
        filename_directory = "./central/config/{}.txt".format(device_name)
        filename_open = open(filename_directory, "r")
        filename = filename_open.read()
        # print(bgw_csv2)
        # Push the per-device configuration.
        push_config = central.configuration.configuration_push.config_device(
            filename, device_name, serial_number, mac_address)
        if push_config==200:
            None
        elif push_config==500:
            central.configuration.configuration_push.config_device(
            filename, device_name, serial_number, mac_address)
