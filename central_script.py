from central import *
from twisted.internet import task, reactor
import time
import sys
import argparse

def create_vgw():
    print("Starting the creation of Aruba Virtual Gateways, group configuration and Sites.")
    central.authentication.check_config.check_config()
    central.authentication.database.database_init()
    central.configuration.VGW_Deployment.start_script()
    print("Finished!")

def delete_vgw():
    central.authentication.check_config.check_config()
    central.authentication.database.database_init()
    central.configuration.VGW_Deployment.delete_script()

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Create a showtop20 subcommand    
parser_showtop20 = subparsers.add_parser("create_vgw", help='Creates VGWs in Aruba Central')
parser_showtop20.set_defaults(func=create_vgw)

# Create a listapps subcommand       
parser_listapps = subparsers.add_parser("delete_vgw", help='Removes the VGWs in Aruba Central')
parser_listapps.set_defaults(func=delete_vgw)

if len(sys.argv) <= 1:
    sys.argv.append('--help')

options = parser.parse_args()
options.func()

