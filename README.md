# Vulnerable Code Dataset

The toolkits subdirectory contains scripts.

## parse_nvd.py
- This script needs an nvd/ directory in the same subdirectory as the script containing all of the .json files from the NVD Database. The version of the schema it parses is 1.1

The parse_nvd.py file parses the nvd database and creates a semi-colon seperated csv file containing the CWE of the commit and the commit link.


