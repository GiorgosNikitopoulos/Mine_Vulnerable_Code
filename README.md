# Vulnerable Code Dataset

The toolkits subdirectory contains scripts.

## parse_nvd.py
- This script needs an nvd/ directory in the same subdirectory as the script containing all of the .json files from the NVD Database. The version of the schema it parses is 1.1

The parse_nvd.py file parses the nvd database and creates a semi-colon seperated csv file containing the CWE of the commit, the CVE ID and the commit link.

## clean_pulls.py
- This script requires the csv of github links parse_nvd.py created. 

The github links mined by parse_nvd.py contain pulls which contain many commits. This script flattens the pulls into commits. 
## get_files.py
- This script requires a files/ directory. Create the files/ directory with the command
    ```
    mkdir files
    ```
- This script requires the csv of github links clean_pulls.py created. (named commits.list) 

The get_files.py script creates a file_names.list file containing the file names of each file downloaded. 
The files downloaded end up on the files/ directory. They have the format of <good_or_bad>_<Vulnerability_ID>_<File_ID> 

## make_directories.py
- This script requires the file_names.list file made by get_files.py and the commits.list file created by clean_pulls.py
- This script requires the dataset/ directory in the same directory as the script. Create the dataset/ subdirectory with the command 
    ```
    mkdir dataset
    ```
This script creates the subdirectory tree required for the dataset 
The file_exts list contains the list of all ALLOWED file extensions. File extensions are filtered by this list 
j
## populate_files.py
- This script requires the file_names.list file made by get_files.py and the commits.list file created by clean_pulls.py
- This script requires the dataset/ directory formatted by the make_directories.py script. 
This script populates the subdirectory tree required for the dataset 
The file_exts list contains the list of all ALLOWED file extensions. File extensions are filtered by this list 

