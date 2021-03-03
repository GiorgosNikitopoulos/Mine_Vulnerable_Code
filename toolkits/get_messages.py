import pandas as pd
import requests
import csv
import json
import time

ACCESS_TOKEN = '<INSERT ACCESS TOKEN HERE>'
header = {'Accept': 'application/vnd.github.cloak-preview'}
all_messages = list()
all_cwes = list()
all_cves = list()
all_commits = pd.read_csv('commits_final.list', sep = ';', quoting = csv.QUOTE_ALL, header = None)
all_commits[2][0]
all_found_commits = list()
i = 0
for j, commit_link in enumerate(all_commits[2]):
    i += 1
    if (i % 1000 == 0):
        print(i)
        time.sleep(1200)
    api_link = commit_link.replace('github.com/', 'api.github.com/repos/')
    api_link = api_link.replace('commit', 'commits')
    api_link = api_link.replace('commitss', 'commits')
    api_link = api_link.replace('www.', '')
    try:
        response = requests.get(api_link, headers = header, auth = ('GiorgosNikitopoulos', ACCESS_TOKEN))
        if response.status_code == 403:
            print("THROTTLE")
        response = json.loads(response.text)
    except Exception as e:
        print(api_link)
        print(e)
        #all_messages.append(None)
        continue
    try:
        all_messages.append(response['commit']['message'])
        all_cwes.append(all_commits[0][j])
        all_cves.append(all_commits[1][j])
        all_found_commits.append(commit_link)
    except Exception as e:
        print(api_link)
        print(e)
        #all_messages.append(None)

dataframe = pd.DataFrame()
dataframe['cwe'] = all_cwes
dataframe['cve'] = all_cves
dataframe['commits'] = all_found_commits
dataframe['messages'] = all_messages
dataframe.to_csv('secpatch_commit_msgs.list', sep = ';', header = False, index = False, quoting = csv.QUOTE_ALL)

