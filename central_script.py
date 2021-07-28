import argparse
import sys
import time

from central import *


def create_vgw():
    print("Starting the creation of Aruba Virtual Gateways, group configuration and Sites.")
    central.authentication.check_config.check_config()
    central.authentication.database.database_init()
    central.configuration.VGW_Deployment.start_script()
    while True:
        prompt=input('''Though the VGW's have been deployed, when the VGW's will come online in Central for the first time, 
        Aruba Central will change the VGW uplink ports (0/0/0 & 0/0/1) to vlan 4094.\n
        Type in  to push the configuration, once all VGW's are online.
        \n Type exit to exit this script.     config_push or exit    :   ''').lower()
        if prompt== 'config_push':
            print("re-executing configuration push function")
            central.configuration.configuration_device_fix.config_start_script()
        elif prompt== "exit":
            print("Exiting script. You can always execute the configuration push by typing 'python3 central_script.py config_push'")
            return
        else:
            print("Type either config_push or exit")
        print("Finished!")

def delete_vgw():
    central.authentication.check_config.check_config()
    central.authentication.database.database_init()
    central.configuration.VGW_Deployment.delete_script()


def config_push():
    central.authentication.check_config.check_config()
    central.authentication.database.database_init()
    central.configuration.configuration_device_fix.config_start_script()


# def test():
#     central.authentication.check_config.check_config()
#     central.authentication.database.database_init()
#     central.configuration.labels.labels_delete()


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_showtop20 = subparsers.add_parser(
    "create_vgw", help='Creates VGWs in Aruba Central')
parser_showtop20.set_defaults(func=create_vgw)

parser_listapps = subparsers.add_parser(
    "delete_vgw", help='Removes the VGWs in Aruba Central')
parser_listapps.set_defaults(func=delete_vgw)


parser_listapps = subparsers.add_parser(
    "config_push", help='Push the Device Configs again for consistency...')
parser_listapps.set_defaults(func=config_push)


# parser_listapps = subparsers.add_parser(
#     "test", help='Test ....')
# parser_listapps.set_defaults(func=test)


if len(sys.argv) <= 1:
    sys.argv.append('--help')

options = parser.parse_args()
options.func()
