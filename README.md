# Vulnerable Code Dataset

The toolkits subdirectory contains scripts.

## parse_nvd.py
- This script needs an nvd/ directory in the same subdirectory as the script containing all of the .json files from the NVD Database. The version of the schema it parses is 1.1

The parse_nvd.py file parses the nvd database and creates a semi-colon seperated csv file containing the CWE of the commit, the CVE ID and the commit link.

## clean_pulls.py
- This script requires the csv of github links parse_nvd.py created. 

The github links mined by parse_nvd.py contain pulls which contain many commits. This script flattens the pulls into commits. 
