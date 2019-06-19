import os
import time
import hashlib
import argparse
import pandas as pd
import subprocess


def unmount_SDs(sd_prefix):
	cwd = os.getcwd()
	filename = "SDlist.txt"

	for i in range(len(sd_prefix)):
		cmd = "diskutil list | grep " + sd_prefix[i] + " > " + cwd + "/" + filename #f"diskutil list | grep {sd_prefix[i]} > {cwd}/{filename}"
		subprocess.call(cmd,shell=True) # get disk info for mounted SDs with specified prefix using diskutil

		if os.stat(filename).st_size != 0: # trying to read an empty file will throw an error
			lst = pd.read_csv(filename, header=None, delim_whitespace=True) # strip out disk name(s) (ie /dev/disk2) and associated SD name(s)

			lst.columns = ["0", "format", "name", "size", "size-units", "disk"]
			disks = lst["disk"].values
			names = lst["name"].values

			for i in range(len(disks)): # reformat cards to clean FAT32 with original names
				cmd = "diskutil unmountDisk /dev/" + disks[i][0:-2] #f"diskutil unmountDisk /dev/{disks[i][0:-2]}" # 'diskutil list' actually saves name like "disk2s2", so strip off last two characters
				subprocess.call(cmd, shell=True)
				
	cmd = "rm " + cwd + "/" + filename #f"rm {cwd}/{filename}"
	subprocess.call(cmd,shell=True) # delete SD reference file when done

# calculate the md5 hash
def getlocalfile_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# make a copy of files from sd to desired local destination, confirm data transfer with MD5 hash, then delete original from sd if desired
def copyfile_local(fname, srcpath, dstpath, delete_choice):
	if not fname.startswith("."):

		fname_safe = fname.replace(" ", "_") # replace whitespace in filename with underscores, if there. 
		if fname_safe != fname:
			cmd = "mv " + srcpath + "/'" + fname + "' " + srcpath + "/" + fname_safe   #f"mv {srcpath}/\"{fname}\" {srcpath}/{fname_safe}"
			os.system(cmd)

		fname = fname_safe

		copied = dstpath + "/" + fname  #f"{dstpath}/{fname}"
		cmd = "cp -p " + srcpath + "/" + fname + " " + dstpath   #f"cp -p {srcpath}/{fname} {dstpath}"
		os.system(cmd)

		md5local = getlocalfile_md5(srcpath + '/' + fname) 	 				# get hash for original file
		md5sd = getlocalfile_md5(copied)									# get hash for new local copy

		if not (md5local == md5sd):
			print("Oh no! Hash test failed for " + dstpath + "/" + fname + ". Trying again.")  #f"Oh no! Hash test failed for {dstpath}/{fname}. Trying again.") # if data copy doesn't match original, try again
			copyfile_local(fname, srcpath, dstpath, delete_choice)
		else:
			if delete_choice: # delete file from sd if user specified to
				os.remove(srcpath + "/" + fname)  #f"{srcpath}/{fname}")


def transfer_folder_contents(dst_path, sd_src_path, delete_choice):
	if not os.path.isdir(dst_path):
		os.makedirs(dst_path, mode=0o777) # make directory with folders inside for each disk (or subdirectory)

		files = os.listdir(path=sd_src_path)
		for file in files:
			if not file.startswith("."): #ignore hidden files
				if os.path.isdir(sd_src_path + "/" + file):
				# if os.path.isdir(f"{sd_src_path}/{file}"): #recursively copy nested folders
					# print(str(file) + ' is a directory.')
					local_subpath = dst_path + "/" + file  #f"{dst_path}/{str(file)}"
					sd_subpath = sd_src_path + "/" + file #f"{sd_src_path}/{str(file)}"
					transfer_folder_contents(local_subpath, sd_subpath, delete_choice)#, local)
				else: # bottom of the line. Copy file
					copyfile_local(file, sd_src_path, dst_path, delete_choice)

def get_disks(sd_prefix, sd_mount):
	'''
	Get list of disks matching prefix
	
	Inputs: 
		sd_prefix: user-specified list of sd card prefixes to use
		sd_mount: mount point for SD cards
	
	Returns a list of disks matching prefix
	'''

	# Account for naming errors (Kitzes Lab convention)
	if sd_prefix[0] == "MSD":
                sd_prefix.extend(["MS", "MD", "DMS", "DSM", "SDM", "SMD"])

	# Get list of disks matching prefix
	disks = os.listdir(path=sd_mount) # SD cards mount to /Volumes on Mac
	matching_disks = [disk for disk in disks if disk.startswith(tuple(sd_prefix))]
	if args.local or args.globus:
		print("     Transferring files from " + str(len(matching_disks)) + " disks:\n")#f"     Transferring files from {len(matching_disks)} disks:\n")
	return matching_disks 	


def local_transfer(sd_prefix, sd_mount, local_path, delete_choice, reformat_choice, unmount_choice):
	# Get list of disks matching prefixes
	matching_disks = get_disks(sd_prefix, sd_mount)

	# Transfer contents of all matching disks
	for disk in matching_disks:
		folder_name = str(disk)# + current_date)
		sd_fullpath = sd_mount + "/" + disk #f"{sd_mount}/{disk}"
		local_fullpath = os.path.join(local_path, folder_name)

		transfer_folder_contents(local_fullpath, sd_fullpath, delete_choice)
		print("          Files from " + disk + " copied to " + local_fullpath + ".") #f"          Files from {disk} copied to {local_fullpath}.")
	
	if reformat_choice:
		reformat_SDs_FAT32(matching_disks, sd_mount)
	
	if not reformat_choice and unmount_choice:
		unmount_SDs(matching_disks)


def globus_upload(sd_p, sd_mount, upload_dir, delete_choice, reformat_choice):
	import globus_sdk
	#only import if user needs - this will slow things down very slightly for Globus users, but save time for local users

	CLIENT_ID = "" # app
	MYENDPOINT_ID = "" # UUID
	DTN_ID = "" # dtn

	client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
	client.oauth2_start_flow(refresh_tokens=True)

	authorize_url = client.oauth2_get_authorize_url()
	print('Please go to this URL and login: {0}'.format(authorize_url))

	get_input = getattr(__builtins__, 'raw_input', input) # get correct input() fn to be compatible with Python2 or 3
	auth_code = get_input("Please enter the code you get after login here: ").strip()
	token_response = client.oauth2_exchange_code_for_tokens(auth_code)

	globus_auth_data = token_response.by_resource_server["auth.globus.org"]
	globus_transfer_data = token_response.by_resource_server["transfer.api.globus.org"]

	# most specifically, you want these tokens as strings
	AUTH_TOKEN = globus_auth_data["access_token"]
	TRANSFER_TOKEN = globus_transfer_data["access_token"]

	# a GlobusAuthorizer is an auxiliary object we use to wrap the token. In more
	# advanced scenarios, other types of GlobusAuthorizers give us expressive power
	authorizer = globus_sdk.AccessTokenAuthorizer(TRANSFER_TOKEN)
	tc = globus_sdk.TransferClient(authorizer=authorizer)
	tdata = globus_sdk.TransferData(tc, MYENDPOINT_ID, DTN_ID, label="", sync_level="checksum",preserve_timestamp=True,verify_checksum=True)

	upload_dir = "~/" + upload_dir  #f"~/{upload_dir}"

	tc.operation_mkdir(DTN_ID, path=upload_dir) # new directory in ~/ibwo for each SD
	# you will error out if you specified a directory that already exists

	# Get list of disks matching prefixes
	matching_disks = get_disks(sd_prefix, sd_mount)

        # Upload contents of all matching disks
	for d in matching_disks:
		new_folder = upload_dir + "/" + str(disk)  #f"{upload_dir}/{str(disk)}"
		sd_fullpath = sd_mount + "/" + disk    #f"{sd_mount}/{disk}"
		tc.operation_mkdir(DTN_ID, path=new_folder) # new directory in indicated directory for each SD

		files = os.listdir(path=sd_fullpath)
		for file in files:
			if not file.startswith("."): #ignore hidden files
				if os.path.isdir(sd_fullpath + "/" + file):  #f"{sd_fullpath}/{file}"): #recursively copy nested folders
					tdata.add_item( sd_fullpath + "/" + file, new_folder + "/" + file, recursive=True)  #f"{sd_fullpath}/{file}", f"{new_folder}/{file}", recursive=True)
				else:
					tdata.add_item(sd_fullpath + "/" + file, new_folder + "/" + file)   #f"{sd_fullpath}/{file}", f"{new_folder}/{file}") # copy from SD to new Globus dir

	transfer_result = tc.submit_transfer(tdata)
	print("Globus task_id =", transfer_result["task_id"])

    # not sure if it is safe to reformat right now, when globus transfer has been initiated but not necessarily completed.
	# if(reformat_choice):
	# 	reformat_SDs_FAT32(sd_prefix)
	
    
def reformat_SDs_FAT32(sd_prefix, sd_mount):
	print("\n     Reformatting SD cards.\n---")

	cwd = os.getcwd()
	filename = "SDlist.txt"

	for i in range(len(sd_prefix)):
		cmd = "diskutil list | grep " + sd_prefix[i] + " > " + cwd + "/" + filename #f"diskutil list | grep {sd_prefix[i]} > {cwd}/{filename}"
		subprocess.call(cmd,shell=True) # get disk info for mounted SDs with specified prefix using diskutil

		if os.stat(filename).st_size != 0: # trying to read an empty file will throw an error
			lst = pd.read_csv(filename, header=None, delim_whitespace=True) # strip out disk name(s) (ie /dev/disk2) and associated SD name(s)

			lst.columns = ["0", "format", "name", "size", "size-units", "disk"]
			disks = lst["disk"].values
			names = lst["name"].values

			for i in range(len(disks)): # reformat cards to clean FAT32 with original names
				cmd =  "diskutil eraseDisk FAT32 " + names[i] + " MBRFormat /dev/" + disks[i][0:-2]  #f"diskutil eraseDisk FAT32 {names[i]} MBRFormat /dev/{disks[i][0:-2]}" # 'diskutil list' actually saves name like "disk2s2", so strip off last two characters
				subprocess.call(cmd, shell=True)
				if not args.unmount:
					cmd = "diskutil mountDisk /dev/" + disks[i][0:-2]   #f"diskutil mountDisk /dev/{disks[i][0:-2]}"
					subprocess.call(cmd,shell=True)
				print("---")
	cmd = "rm " + cwd + "/" + filename  #f"rm {cwd}/{filename}"
	subprocess.call(cmd,shell=True) # delete SD reference file when done
	if args.unmount:
		matching_disks = get_disks(sd_prefix, sd_mount)
		unmount_SDs(matching_disks)


###################################################################################### MAIN

start = time.time()
donemsg = 1
local = 1

parser = argparse.ArgumentParser(description="Transfer files from SD card(s) to local storage or Globus cloud storage, and/or delete data or reformat SD card(s).")

parser.add_argument("-p", "--prefix", nargs='+', required=True, help="Prefix(es) of all your SD cards' names. Enter multiple prefixes separated by spaces to indicate a range of prefixed names. [Required]")
parser.add_argument("-m", "--mountPath", default='/Volumes', help ="The path to where SD cards mount on this computer (defaults to Mac's mountpoint: /Volumes). [Optional]")
parser.add_argument("-l", "--local", help="New local directory name (with path) to save data to. [Required for local transfer]")
parser.add_argument("-g", "--globus", help="New directory name (with absolute path) in your Globus filesystem to upload data to.[Required for local Globus transfer]")
parser.add_argument("-d", "--delete", action='store_true', help="Delete files from SD cards after transfer and confirmation are complete. Files are only deleted if this flag is included. [Optional]")
parser.add_argument("-r", "--reformat", action='store_true', help="Reformat SD card to FAT32, maintaining its name. WARNING: all data will be deleted during reformat, even if you didn't specify the -d flag (defaults to not reformat). To reformat but not transfer any data, use -l 0 -g 0 -r. [Optional]")
parser.add_argument("-u", "--unmount", action='store_true', help="Unmount SD cards from your computer after done with local copy or reformat. Don't use this for Globus upload! [Optional]")
parser.add_argument("-y", "--yes", action='store_true', help="Include this flag if you want to force deletion or reformatting without typing Y in the menu [Optional]")

args = parser.parse_args()

print("     SD prefix(es): ")
for i in args.prefix:
	print("        " + i)#f"        {i}")
print("     SD mount path: " + args.mountPath)

# Print delete & reformatting message - make sure they're serious about deleting data off cards
if args.delete:
	if not args.yes:
		tmp = input("\n     Please confirm (Y/N) that you want to delete all files from the SD cards after transfer is done:\n     >>> ")
		if tmp == "Y" or tmp == "y":
			print("     Great! Just making sure.\n")
			time.sleep(2)
		else:
			print("     Ok! Continuing with copy, but files will NOT be deleted.\n")
			args.delete = False
			time.sleep(2)
	else:
		print("     Deleting data after transfer complete.\n")
		time.sleep(2)

if args.reformat:
	sd_prefix = args.prefix
	if sd_prefix[0] == "MSD":
		sd_prefix.extend(["MDS", "DMS", "DSM", "SDM", "SMD"]) # account for naming errors
	if not args.yes:
		tmp = input("\n     Please confirm (Y/N) that you want to reformat and delete all files from the SD cards after transfer is done (if any):\n     >>> ")
		if tmp == 'Y' or tmp == 'y':
			print("     Great! Just making sure.\n")
			time.sleep(2)
		else:
			print("Ok! Continuing with copy, but SD cards will NOT be reformatted.\n")
			time.sleep(2)
			args.reformat = False
	else:
		print("     Reformatting SD cards after transfer complete (if any).")
		time.sleep(2)

	if args.globus:
		print("     Ignoring -r (reformat) flag - run again after Globus Upload is complete to ensure data isn't deleted before it istransferred.\n.")

	if (not args.globus) and (not args.local): #initiate reformat if no transfer happening
		reformat_SDs_FAT32(sd_prefix, sd_mount)


# Initiate local transfer
if args.local:
	print("     Saving to local directory: " + args.local)#f"     Saving to local directory: {args.local}")
	local_transfer(args.prefix, args.mountPath, args.local, args.delete, args.reformat, args.unmount)

# Initiate Globus transfer
if args.globus:
	local = 0
	print("     Uploading to directory " + args.globus + " on Globus.")#f"     Uploading to directory {args.globus} on Globus.")
	tmp = input('\n     Please confirm (Y/N) that you want to begin a Globus transfer, and have already updated the python script to include your Globus IDs (see README)\n     >>> ')
	if tmp == "Y" or tmp == "y":
		globus_upload(args.prefix, args.mountPath, args.globus, args.delete, args.reformat)
	else:
		donemsg = 0
		print("     Exiting.")



# Print 'peace out'
if donemsg:
	if not local:
		print("\n     Globus transfer initiated.\n")
	if args.local:
		print("\n     Done with local transfer! Executed in " +  str(time.time()-start) + " seconds\n") #f"\n     Done with local transfer! Executed in {str(time.time()-start)} seconds\n")
	if args.reformat:
		print("\n     Done with reformatting!\n")



#TODO: unmount all - use -u uption accordingly. Not for globus transfer.
