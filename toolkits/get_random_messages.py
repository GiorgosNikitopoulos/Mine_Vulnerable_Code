import pandas as pd
import requests
import csv
import json
import time
import random

ACCESS_TOKEN = '<INSERT HERE>'
header = {'Accept': 'application/vnd.github.cloak-preview'}
all_random_commit_links = list()
all_messages = list()
all_cwes = list()
all_cves = list()
all_commits = pd.read_csv('commits_final.list', sep = ';', quoting = csv.QUOTE_ALL, header = None)
all_our_commits = pd.read_csv('generic_msgs.list', sep = ';', quoting = csv.QUOTE_ALL, header = None)

print(all_our_commits[2])
#if(all_our_commits[2].str.contains('https://github.com/OpenNMS/opennms/commit/8710463077c10034fcfa06556a98fb1a1a64fd0d').any()):
#    print('Bizd')
all_commits[2][0]
all_found_commits = list()
all_numbers = list()
all_random_commit_msgs = list()
i = 0
for j, commit_link in enumerate(all_commits[2]):
    i += 1
    if(all_our_commits[2].str.contains(commit_link).any()):
        continue
    else:
        pass
    api_link = commit_link.replace('github.com/', 'api.github.com/repos/')
    api_link = api_link.replace('commit', 'commits')
    api_link = api_link.replace('commitss', 'commits')
    api_link = api_link.replace('www.', '')

    try:
        api_link = api_link.rsplit('/', 1)[0]
        api_link = api_link + '?per_page=1'
        response = requests.get(api_link, headers = header, auth = ('GiorgosNikitopoulos', ACCESS_TOKEN))
        print(response.headers['X-RateLimit-Remaining'])
        if (int(response.headers['X-RateLimit-Remaining']) < 10 ):
            time.sleep(4000)
        if response.status_code == 403:
            #print(response.headers)
            print("THROTTLE")
        number = response.headers['Link'].rsplit('=', 2)[1]
        number = number.split('>')[0]
        number = int(number)
        response = json.loads(response.text)

        rand_number = random.randint(1, number)
        api_link = api_link + '&page=' + str(rand_number)
        response_ran_page = requests.get(api_link, headers = header, auth = ('GiorgosNikitopoulos', ACCESS_TOKEN))
        if (int(response_ran_page.headers['X-RateLimit-Remaining']) < 10 ):
            time.sleep(4000)

        if response_ran_page.status_code == 403:
            print("THROTTLE")
        response_ran_page = json.loads(response_ran_page.text)
        random_commit_link = response_ran_page[0]['url']


        response_ran_commit = requests.get(api_link, headers = header, auth = ('GiorgosNikitopoulos', ACCESS_TOKEN))
        if (int(response_ran_commit.headers['X-RateLimit-Remaining']) < 10 ):
            time.sleep(4000)
        if response_ran_commit.status_code == 403:
            print("THROTTLE")
        response_ran_commit = json.loads(response_ran_commit.text)
        random_commit_message = (response_ran_commit[0]['commit']['message'])
    except Exception as e:
        print(api_link)
        print(e)
        #all_messages.append(None)
        continue
    try:
        all_messages.append(response[0]['commit']['message'])
        all_cwes.append(all_commits[0][j])
        all_cves.append(all_commits[1][j])
        all_found_commits.append(commit_link)
        all_numbers.append(number)
        all_random_commit_links.append(random_commit_link)
        all_random_commit_msgs.append(random_commit_message)
        dataframe = pd.DataFrame()
        dataframe['cwe'] = all_cwes
        dataframe['cve'] = all_cves
        dataframe['commits'] = all_found_commits
        dataframe['messages'] = all_messages
        dataframe['numbers'] = all_numbers
        dataframe['rcommit_links'] = all_random_commit_links
        dataframe['rcommit_msgs'] = all_random_commit_msgs

        dataframe.to_csv('generic_msgs.list', sep = ';', header = False, index = False, quoting = csv.QUOTE_ALL)

    except Exception as e:
        print(api_link)
        print(e)
        #all_messages.append(None)

dataframe = pd.DataFrame()
dataframe['cwe'] = all_cwes
dataframe['cve'] = all_cves
dataframe['commits'] = all_found_commits
dataframe['messages'] = all_messages
dataframe['numbers'] = all_numbers
dataframe['rcommit_links'] = all_random_commit_links
dataframe['rcommit_msgs'] = all_random_commit_msgs

dataframe.to_csv('generic_msgs.list', sep = ';', header = False, index = False, quoting = csv.QUOTE_ALL)

