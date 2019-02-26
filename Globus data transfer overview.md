
Notes by Trieste, 02-2019, to document how we’ll be transferring data, using the script globus_sd_transfer.py

SETUP:
* Physical setup: any number of SD cards mounted via USB to a laptop on Ethernet for a fast internet connection. I have been using 1 or 2 Lexar 12-MSD hubs, connected via USB to my MacBook Pro
* Globus & script setup:
    * Follow [tutorial](https://docs.globus.org/how-to/globus-connect-personal-mac/ "Title") to download, install, & open Globus Connect Personal; get and enter key
    * Update globus-sd-transfer.py with your Globus ID numbers (You shouldn’t have to change the pitt#dtn ID, but it’s in there too):
        1. Client ID (your ‘app’) - Follow Steps 1 and 2 in this [tutorial](https://globus-sdk-python.readthedocs.io/en/stable/tutorial/ "blah") to make an ‘app’ (log in with your regular Pitt username and password, app name doesn’t matter) and copy the CLIENT_ID into _line 14_
        2. Endpoint ID (your account) - log into Globus.org with your Pitt info, go to Endpoints/[you], and copy the UUID into _line 15_
        3. pitt#dtn ID (where the data is going). Barry set up a symlink in the home directory of pitt#dtn (~/ibwo_data) for us to send this data to the Cluster.
* Check that _line 10_ has the correct path to where the SDs mount (on Mac it’s /Volumes)
* Give Globus access to SD cards - Create a symlink to /Volumes (ie symlink /Volumes ~/Desktop/volsym), then open Globus Connect Personal preferences (click the ‘g’ bubble in the top bar by wifi, for Mac), and make the symlink Sharable in the Access tab

USAGE:
* Make sure you are logged into Globus and have access to pitt#dtn - go to the Endpoint in the online GUI and Activate Credentials with your Pitt user info if you’re not currently activated
* Run script: python globus_sd_transfer.py
* Follow link to Consent Request using Globus page (cmd-click), enter any name in “Provide a label for future reference” box, click Allow
* Copy Native App Authorization Code, paste into CL
    * Note: script is set up to auto-reauth

WEIRD CODE THINGS, for future work on this/other Globus scripts:
* Instead of recursively copying from all of the MSD folders, I go into each MSD folder, and then add each file to the TransferData list. I did this so I could scan filenames and skip the invisible files (ie .Spotlight)
* When specifying the path of local files/directories to be copied, you’ll get a permission error unless you have the FULL path included in the Globus API add_item() function. Ie Users/kitzeslab/Desktop, not ~/Desktop. It doesn’t mind relative paths on the Globus side, though (~/ibwo_data is fine)
* “Recursively” copying directory /Foo/ will only recursively copy what’s inside /Foo/. I got around this by starting in /Volumes and recursively copying directories that begin with the prefix ‘MSD’. If SD files are ever named something else, changing the sd_prefix variable will handle the new names.
* Globus will transfer a single symlinked file, but if you ask it to recursively transfer a symlink directory, it’ll just make an empty folder of the root name and not continue transferring further down the line.

