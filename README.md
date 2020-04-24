# Backup
A simple Python-based backup utility for Linux.
## Getting Started
These instructions will get you started by demonstrating how the utility works.
### Prerequisites
A functional Python 3 installation with the standard library. That's it.
### Installation
Download this repository and extract the zip file to a directory somewhere under your user folder.
### Walkthrough
Open a terminal (`Ctrl+Alt+T`) and navigate to the directory where Backup is located.

##### Example Data
Have a look at the 'test_data' subdirectory. You should see the following structure:
```
test_data/
├── source1/
│   ├── dir1/
│   │   ├── dir3/
│   │   │   └── file4
│   │   ├── file2
│   │   └── file3
│   ├── dir2/
│   │   └── file5
│   └── file1.sdf
└── source2/
    └── file6
```
This is the directory tree we will be backup up as an example.
##### The Config File
Now inspect 'backup_config.py', which is in the root directory. There are several entries, each described here.
* `source_dirs` : These are the source directories that you want backing up. Each entry is a Python tuple (defined by the surrounding brackets) with two elements. The first element is the path to a directory that's to be backed up, and the second is its alias (described later). Both elements of each entry should be strings (encased in `'` or `"`). In this example config file, two directories will be backed up -- './test_data/source1/' and './test_data/source2'. Their aliases are 'f1' and 'f2' respectively. Relative paths have been used here for demonstration, but you can (and probably should) use absolute paths to your backup locations when creating a config file.
* `backup_locs` : These are the locations that the source directories will be backed up to. A new, timestamped, backup directory will be created under each of the backup locations. For the example, two backups will be created -- one under './test_data/test1' and another under './test_data/test2'.
* `exclude_file_types` : This is a list of excluded file types. Make sure each entry is a string.  Here, files ending in '.sdf' will be ignored. I use this to ignore large datasets, but maintain the necessary files to reproduce them.
* `log_setup` : This sets the nature of the log that's generated and should consist of two entries. The first is the location of the log file that will be created and written to (here set to './backup.log'). The second is the logging level and can be one of 'ERROR', 'INFO' or 'DEBUG'. 'ERROR' only logs failed file transfers and is the recommended setting. 'INFO' logs every action and can result in huge log files so is not recommended. 'DEBUG' is for debugging and again isn't recommended except for support cases.
* `notes` : Any notes you want attached to the backup go here as a Python string.
##### Making the Backups
Now that the config file is all set, simply run `python backup.py` from the root directory to initiate the backup. Because the example source directories contain very little data, this should be near-instantaneous.
Take a look in the 'test_data' directory again. You should see two new folders, 'dest1' and 'dest2'. The contents of these directories is identical. In each, there is a timestamped directory indicating the date and time of the backup. In there are two subdirectories -- 'f1' and 'f2'. 'f1' contains a copy of everything in 'source1' and 'f2' a copy of everything in 'source2', both excluding any '.sdf' files. The timestamp directory also contains a file, 'backup_notes.txt', with some notes of the backup.
# Usage
You should now be able to generate a config file to make your own backups, although I recommend you keep a copy of the example config for reference.
# Authors
* George K Holt -- inital work -- [georgeholt1](https://github.com/georgeholt1)
# License
Licensed under the MIT License. See the [LICENSE](https://github.com/georgeholt1/backup/blob/master/LICENSE) file for details.
