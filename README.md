#SDBranch Virtual Lab deployment script

This script configures Aruba Virtual gateways in Aruba Central for a canned SDBranch Virtual Lab environment.

1. Create a virtualenv in Python 3.7+ and call it venv: `python3 -m venv venv`
2. Activate the venv and install the required Python Modules: `pip install -r requirements.txt`
3. Rename `central/config/rename_to_config.cfg` to `central/config/config.cfg` and fill in the missing blanks. #Warning, this app will NOT work if you don't fill in EVERY detail.
4. Run this application in either VScode, or after activating the venv in the main directory:

`usage: central_script.py [-h] {create_vgw,delete_vgw} ...`
`positional arguments:`
`  {create_vgw,delete_vgw}`
`    create_vgw          Creates VGWs in Aruba Central`
`    delete_vgw          Removes the VGWs in Aruba Central`

`optional arguments:`
`  -h, --help            show this help message and exit`
