from configparser import ConfigParser
import os.path as path
import os

# params = Path(__file__).parents[1]

# print(params,"/config/config.cfg")
# print("komtiedan")
# two_up =  path.abspath(path.join(__file__ ,"../..","config/config.cfg"))
# print(two_up)
# print("komtiedan")
# import sys
# print(sys.path)
# print(os.path.dirname(__file__))
# print(os.path.dirname(__file__),os.path.pardir)

# configuration file parameters
params = path.abspath(path.join(__file__ ,"../..","config/config.cfg"))
# print(params)
# print(os.path.pardir)
# print(os.path.basename())

config = ConfigParser(strict=True)
config.read(params)


central_portal = config.get('Central', 'central_portal')
central_portal_fqdn = config.get('Central', 'central_portal_fqdn')
central_instance = config.get('Central', 'central_instance')
central_ui_url = config.get('Central', 'central_ui_url')
central_ui_fqdn = config.get('Central', 'central_ui_fqdn')
app_customerid = config.get('Central', 'app_customerid')
app_username = config.get('Credentials', 'app_username')
app_password = config.get('Credentials', 'app_password')
app_clientid = config.get('Tokens', 'app_clientid')
app_clientsecret = config.get('Tokens', 'app_clientsecret')


def check_config():
    """Validate the configuration from the params.cfg file."""
    if not central_instance:
        print(
            'Error: The Central Instance must be defined in config file for Central communication (config/params.cfg)')
        exit(1)
    if not app_customerid:
        print('Error: The customer ID must be defined in config file for Central communication (config/params.cfg)')
        exit(1)
    if not app_username or not app_password:
        print(
            'Error: username and password must be defined in config file for Central communication (config/params.cfg)')
        exit(1)
    if not app_clientid or not app_clientsecret:
        print(
            'Error: Client_ID and Client_secret must be defined in config file for Central communication (config/params.cfg)')
        exit(1)
    print("Configuration is valid - proceeding.")
    return True