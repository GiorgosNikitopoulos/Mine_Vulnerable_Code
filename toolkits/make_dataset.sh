#!/bin/sh
python3 parse_nvd > cve_cwe.list
python3 clean_pulls.py > commits.list
python3 clean_master.py
mkdir files
python3 get_files.py
mkdir dataset_final_sorted
python3 make_directories.py
python3 populate_files.py
