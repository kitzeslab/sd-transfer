import globus_sdk
import sys
import os
import re
import datetime

#usage: python globus_sd_transfer.py


sd_prefix = 'MSD'
sd_mount = '/Volumes'
now = datetime.datetime.now()
current_date = '_' + str(now.month) + '-' + str(now.day) + '-' + str(now.year)

CLIENT_ID = 'bcb2d378-7ab1-4392-9f4e-7eee8b7a5e34' # app
MYENDPOINT_ID = '7b24c79c-2fa0-11e9-9fa4-0a06afd4a22e' # UUID
PITTDTN_ID = 'ee174383-87f2-11e5-995d-22000b96db58' # pitt#dtn

client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
client.oauth2_start_flow(refresh_tokens=True)

authorize_url = client.oauth2_get_authorize_url()
print('Please go to this URL and login: {0}'.format(authorize_url))

get_input = getattr(__builtins__, 'raw_input', input) # get correct input() fn to be compatible with Python2 or 3
auth_code = get_input('Please enter the code you get after login here: ').strip()
token_response = client.oauth2_exchange_code_for_tokens(auth_code)

globus_auth_data = token_response.by_resource_server['auth.globus.org']
globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']

# most specifically, you want these tokens as strings
AUTH_TOKEN = globus_auth_data['access_token']
TRANSFER_TOKEN = globus_transfer_data['access_token']

# a GlobusAuthorizer is an auxiliary object we use to wrap the token. In more
# advanced scenarios, other types of GlobusAuthorizers give us expressive power
authorizer = globus_sdk.AccessTokenAuthorizer(TRANSFER_TOKEN)
tc = globus_sdk.TransferClient(authorizer=authorizer)
tdata = globus_sdk.TransferData(tc, MYENDPOINT_ID, PITTDTN_ID, label="", sync_level="checksum",preserve_timestamp=True,verify_checksum=True)
#TODO: verify_checksum might create a bottleneck, but seems like a good idea

disks = os.listdir(path=sd_mount)					# SD cards mount to /Volumes on Mac
for disk in disks:
	if bool(re.search(sd_prefix, disk)):			# iterate thru SD cards
		new_folder = '/~/ibwo_data/'+str(disk + current_date)
		sd_fullpath = sd_mount+'/' + disk
		tc.operation_mkdir(PITTDTN_ID, path=new_folder) # new directory in ~/ibwo for each SD
		files = os.listdir(path=sd_fullpath)
		for file in files:
			if not (bool(re.match("^\.",file))): # ignore hidden files
				tdata.add_item(sd_fullpath+'/'+file, new_folder+'/'+file) # copy from SD to new Globus dir

transfer_result = tc.submit_transfer(tdata)
print("task_id =", transfer_result["task_id"])

