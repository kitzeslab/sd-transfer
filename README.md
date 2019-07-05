# sd-transfer.py
Trieste Devlin, the Kitzes Lab, University of Pittsburgh
Last update: 06-24-2019

# About

This script finds all SD cards named with a specified list of 1+ prefixes (ours are all called `MSD-0001`, `MSD-0002`, etc), and copy all files contained to the local or Globus cloud destination of your choice. The contents of each drive is placed in its own folder with file structure and original write times maintained in the copies. A checksum is performed on each file to confirm successful transfer. A user may choose to do any combination of the available operations: copy data, delete data from cards, reformat cards, and unmount cards.

# Installation and Basic Info:

If you're not familiar with navigating your filesystem and running simple commands in the Terminal, [this tutorial](https://www.macworld.com/article/2042378/master-the-command-line-navigating-files-and-folders.html) gives a good, quick overview.

On the Github webpage for this script, copy the git URL using the green *Clone or Download* button. Then, in Terminal, navigate to the location in your filesystem where you'd like the script to be saved and run ```git clone \[paste URL\]```. If you get a git error along the lines of *"The command-line developer tools need to be installed"*, follow the instructions printed with that error to get the tools installed on your computer.

Once the download is complete, you can delete everything other than the ```dist``` directory, if you want - it is a self-contained executable copy of the code and all dependencies needed to make it run. To run the code, you need to navigate a few levels deep into the folder that was just created (```cd sd-transfer/dist/SD-tool```). Now you can run the script with the command ```./SD-tool ...``` with the flags and arguments indicating what exactly you want it to do and where you want the data to be saved. Flags to use to specify the different options are outlined in the **Usage** section below. Optional inputs are shown in brackets - but you need to at least specify a prefix so the program knows what cards to read from and either a local or Globus transfer flag with a destination folder name (```-l [name]``` or ```-g```) OR either the delete or reformat flag (```-d``` or ```-r```, indicating that you want to delete/reformat files without copying them anywhere). See the **Examples** section below for specific commands to run for various results. Run ```./SD-tool -h``` to get a printout of the **Usage** section to the terminal as a reminder.

Local usage is as simple as running as specified below with the ```-l [folder-name]``` flag. If the folder you include doesn't exist yet, it will be created. If you just include a folder name, it'll be created in the current directory. If you include a path in front of the name, you can specify the location of where to save the data on your computer (ie ```-l /Users/[you]/Desktop/[folder-name]```). Note: the command ```pwd``` will print the full path of your current directory in the Terminal. See below for Globus setup details, as there are a few changes you need to make in the Python code to get synced up with your account. Note that this code is designed for use on Mac - some changes are necessary to run on another OS. Hope this is useful!

Right now, the script isn't able to handle folder names containing spaces (filenames with spaces are ok though). This will be fixed very soon.


# Usage
```
./sd-transfer [-h] -p PREFIX [PREFIX ...] [-m MOUNTPATH] -l LOCAL
                      [-g GLOBUS] [-d] [-r] [-u] [-y]

Transfer files from SD card(s) to local storage or Globus cloud storage,
and/or delete data or reformat SD card(s).

Arguments:
  -h, --help            show this help message and exit
  -p PREFIX [PREFIX ...], --prefix PREFIX [PREFIX ...]
                        Prefix(es) of all your SD cards' names. Enter multiple
                        prefixes separated by spaces to indicate a range of
                        prefixed names. [Required]
  -m MOUNTPATH, --mountPath MOUNTPATH
                        The path to where SD cards mount on this computer
                        (defaults to Mac's mountpoint: /Volumes). [Optional]
  -l LOCAL, --local LOCAL
                        New local directory name (with path) to save data to.
                        [Required for local transfer]
  -g GLOBUS, --globus GLOBUS
                        New directory name (with absolute path) in your Globus
                        filesystem to upload data to. [Required for local
                        Globus transfer]
  -d, --delete          Delete files from SD cards after transfer and
                        confirmation are complete. Files are only deleted if
                        this flag is included. [Optional]
  -r, --reformat        Reformat SD card to FAT32, maintaining its name.
                        WARNING: all data will be deleted during reformat,
                        even if you didn't specify the -d flag. To reformat
                        but not transfer any data, use -l 0 -g 0 -r. [Optional]
  -u, --unmount         Unmount SD cards from your computer after done with
                        local copy or reformat. Don't use this for Globus
                        upload! [Optional]
  -y, --yes             Include this flag if you want to force deletion or
                        reformatting without typing Y in the menu [Optional]
```


# Examples
```
./sd-transfer.py -p MSD -l ~/Desktop/SD_folder -d 
     # Copy the contents of SD cards with names prefixed by "MSD" to "SD_folder" on your Desktop, then delete files from SDs after asking for delete confirmation.

./sd-transfer.py -p MSD -l ~/Desktop/SD_folder -r -y -u   
     # Same as above, but erase and reformat cards when finished (skip confirmation), then unmount.

./sd-transfer.py -p fieldData -r -u -y
     # Erase and reformat SD cards with names prefixed by "fieldData" (skip confirmation). Don't save any data, but keep the card names as they were. Unmount when finished.

./sd-transfer.py -p SD BobsData -g fieldData/sdTransfer
     # Copy the contents of SD cards with names prefixed by "SD" or "BobsData" to the folder "fieldData/sdTransfer" in your
     # Globus Personal Endpoint filesystem, leaving the contents of the SD cards alone.
```

# Globus Setup:

* Physical setup: any number of SD cards mounted via USB to a laptop on Ethernet for a fast internet connection. Testing was done using variable size 2-12 MSD hubs connected via USB to a MacBook Pro.
* Globus & script setup:
    * Follow [tutorial](https://docs.globus.org/how-to/globus-connect-personal-mac/ "Title") to download, install, & open Globus Connect Personal; get and enter key
    * Update globus-sd-transfer.py with your Globus ID numbers:
        1. Client ID (your ‘app’) - Follow Steps 1 and 2 in this [tutorial](https://globus-sdk-python.readthedocs.io/en/stable/tutorial/ "blah") to make an ‘app’ (Pitt users: log in with your regular Pitt username and password, app name doesn’t matter) and copy the CLIENT_ID into _line 14_
        2. Endpoint ID (your account) - log into Globus.org (Pitt users: with your Pitt login again), go to Endpoints/[you], and copy the UUID into _line 15_
        3. dtn_ID (where the data is going). (Pitt users: talk to Trieste for deets or someone at CRC to get added)
* Give Globus access to SD cards - Create a symlink to /Volumes (eg `ln -s /Volumes ~/Desktop/volsym`), then open Globus Connect Personal preferences (click the ‘g’ bubble in the top bar by wifi, for Mac), and make the symlink Sharable in the Access tab
* Install Globus python SDK: 'pip install globus-sdk'

# Globus Usage:

* Make sure you are logged into Globus and have access to the dtn_ID you'll be using (go to the Endpoint in the online GUI and Activate Credentials with your user info if it's not currently activated)
* Run script: python sd-transfer.py with args as specified above (use absolute path for -g; \~ is interpreted as a local path)
* Follow link to Consent Request using Globus page (cmd-click), enter any name in “Provide a label for future reference” box, click Allow
* Copy Native App Authorization Code, paste into commandline



# Globus Code Things, for future reference on this/other scripts:

* When specifying the path of local files/directories to be copied from the Globus side, you’ll get a permission error unless you have the FULL path included in the Globus API add_item() function. Ie ```Users/me/Desktop```, not ```\~ /Desktop```. It doesn’t mind relative paths on the Globus side, though (```\~/folder``` is fine). This is reversed for input on the local side - don't give it a relative Globus filepath.
* “Recursively” copying directory ```/Foo/``` will only recursively copy what’s *inside* ```/Foo/```. I got around this by starting in ```/Volumes``` and recursively copying directories that begin with the one of the specified prefixes.
* Globus will transfer a single symlinked file, but if you ask it to recursively transfer a symlink directory, it’ll just make an empty folder of the root name and not continue transferring further down the line. I thought this would be a brilliant way to recursively copy from every SD at once, but alas it had to be more complicated than that.
