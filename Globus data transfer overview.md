README for use of sd-transfer.py
Trieste Devlin, the Kitzes Lab, University of Pittsburgh, 03-2019

This script can finds all SD cards named with a specified list of 1+ prefixes (ours are all called 'MSD-001', 'MSD-002, etc), and copy all of the files contained to the local or Globus cloud destination of your choice. The contents of each file is placed in its own folder with file structure and original write times maintained in the copies. A checksum is performed on each file to confirm successful transfer. There is the option to delete files from the SDs after successful transfer.

Local usage is as simple as running as specified below with the -l flag. See below for Globus setup details, as there are a few changes you need to make in the python code to get synced up with your account.

Note that this code is designed for use on Mac - some few changes to path structures are probably necessary to run on another OS. Hope this is useful!



USAGE: copyfiles.py [-h] -p PREFIX -m MOUNTPATH -l LOCAL [-g GLOBUS] [-d]

ARGUMENTS:

  -h, --help            show this help message and exit

  -p PREFIX, --prefix PREFIX
                        Prefix(es) of all your SD cards' names. Enter multiple
                        prefixes separated by spaces to indicate a range of
                        prefixed names. [Required]

  -m MOUNTPATH, --mountPath MOUNTPATH
                        The path to where SD cards mount on this computer
                        (defaults to Mac's mountpoint: /Volumes). [Optional]

  -l LOCAL, --local LOCAL
                        New local directory (with path) to save data to. [Required for local transfer]

  -g GLOBUS, --globus GLOBUS
                        New directory name (with absolute path) to upload data to in your
                        Globus personal endpoint filesystem. [Required for Globus transfer]

  -d, --delete          Delete files from SD cards after transfer and
                        confirmation are complete. Files are only deleted if
                        this flag is included. [Optional]

EXAMPLE USAGE:

   copyfiles.py -p MSD -l ~/Desktop/SD_folder -d 
     # copy the contents of SD cards with names prefixed by "MSD" to "SD_folder" on your Desktop, then delete files from SDs
   
   copyfiles.py -p SD BobsData -g fieldData/sdTransfer
     # copy the contents of SD cards with names prefixed by "SD" or "BobsData" to the folder "fieldData/sdTransfer" in your
     # Globus Personal Endpoint filesystem, leaving the contents of the SD cards alone




GLOBUS SETUP:

* Physical setup: any number of SD cards mounted via USB to a laptop on Ethernet for a fast internet connection. Testing was done using variable size 2-12 MSD hubs connected via USB to a MacBook Pro.
* Globus & script setup:
    * Follow [tutorial](https://docs.globus.org/how-to/globus-connect-personal-mac/ "Title") to download, install, & open Globus Connect Personal; get and enter key
    * Update globus-sd-transfer.py with your Globus ID numbers:
        1. Client ID (your ‘app’) - Follow Steps 1 and 2 in this [tutorial](https://globus-sdk-python.readthedocs.io/en/stable/tutorial/ "blah") to make an ‘app’ (Pitt users: log in with your regular Pitt username and password, app name doesn’t matter) and copy the CLIENT_ID into _line 14_
        2. Endpoint ID (your account) - log into Globus.org (Pitt users: with your Pitt login again), go to Endpoints/[you], and copy the UUID into _line 15_
        3. dtn_ID (where the data is going). (Pitt users: talk to Trieste for deets or someone at CRC to get added)
* Give Globus access to SD cards - Create a symlink to /Volumes (eg `ln -s /Volumes ~/Desktop/volsym`), then open Globus Connect Personal preferences (click the ‘g’ bubble in the top bar by wifi, for Mac), and make the symlink Sharable in the Access tab
* Install Globus python SDK: 'pip install globus-sdk'

GLOBUS USAGE:
* Make sure you are logged into Globus and have access to the dtn_ID you'll be using (go to the Endpoint in the online GUI and Activate Credentials with your user info if it's not currently activated)
* Run script: python sd-transfer.py with args as specified above (use absolute path for -g; \~ is interpreted as a local path)
* Follow link to Consent Request using Globus page (cmd-click), enter any name in “Provide a label for future reference” box, click Allow
* Copy Native App Authorization Code, paste into commandline


WEIRD CODE THINGS, for future reference on this/other Globus scripts:
* When specifying the path of local files/directories to be copied from the Globus side, you’ll get a permission error unless you have the FULL path included in the Globus API add_item() function. Ie Users/me/Desktop, not \~ /Desktop. It doesn’t mind relative paths on the Globus side, though (\~/ibwo_data is fine). This is reversed for input on the local side - don't give it a relative Globus filepath.
* “Recursively” copying directory /Foo/ will only recursively copy what’s inside /Foo/. I got around this by starting in /Volumes and recursively copying directories that begin with the one of the specified prefixes.
* Globus will transfer a single symlinked file, but if you ask it to recursively transfer a symlink directory, it’ll just make an empty folder of the root name and not continue transferring further down the line. I thought this would be a brilliant way to recursively copy from every SD at once, but alas it had to be more complicated than that.
