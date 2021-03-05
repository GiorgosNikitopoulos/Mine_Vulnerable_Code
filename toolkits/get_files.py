import requests
import argparse
import logging
from parse import *
import pandas as pd


def construct_parent_link(file_links, old_hash, new_hash):
    old_sites = list()

    for i, file_link in enumerate(file_links):
        #print(i)
        #print(file_link)
        old_sites.append(file_link.replace(old_hash[i], new_hash))

    return(old_sites)

def get_parent_hash(text):
    try:
        temp = text.split('parent', 1)[1]
    except(IndexError):
        return(None)

    temp = temp.split("href=\"", 1)[1]
    temp = temp.split("\"", 1)[0]
    temp = temp.rsplit("/")[-1]

    return_string = temp

    return(return_string)

def get_file_link(text):
    split_all = text.split("\"View file")
    old_hashes = list()
    new_hashes = list()
    size_of_list = len(split_all) - 1

    for i in range(size_of_list):
        temp = split_all[i]
        temp = temp.rsplit("href=\"", 1)
        temp = temp[1]
        temp = temp.split("\"", 1)[0]
        old_hash = temp.split("blob/", 1)[1]
        old_hash = old_hash.split("/", 1)[0]
        temp = temp.replace("/blob", "")
        new_hashes.append("https://raw.githubusercontent.com" + temp)
        old_hashes.append(old_hash)
        #print(new_hashes)
        #print(old_hashes)

    return (new_hashes, old_hashes)

def get_old_new_links(url):
    response = requests.get(url)
    if(response.status_code != 200):
        return [], []
    text = response.text
    file_link, old_hash = get_file_link(text)
    parent_hash = get_parent_hash(text)
    if(parent_hash == None):
        return [], []
    old_file = construct_parent_link(file_link, old_hash, parent_hash)

    return old_file, file_link

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exclude')
    args = parser.parse_args()
    

    test_strings = ['test']
    df = pd.read_csv('commits.list', sep = ';', header = None)
    with open("commits.list", 'r') as f:
        urls = f.readlines()
    file_names_file = open("file_names.list", 'w')

    lines = [x.strip() for x in urls]
    urls = [x.rsplit(';', 1)[1] for x in lines]
    i_true = 0
    print(len(urls))
    for i, url in enumerate(urls):
        print(url)
        exception_happened = 0
        if(url.count("patch") > 0):
            logging.warning("Requests error: " + str(i))
            logging.warning("Requests error: " + bad_link)
            df.drop(index=i, inplace = True)
            continue
        if url.count('github') == 0:
            url = 'https://www.github.com/' + url
        old_links, new_links = get_old_new_links(url)
        for j in range(len(old_links)):
            bad_link = old_links[j]
            new_link = new_links[j]
            if bad_link.count('github') == 0:
                bad_link = 'https://www.github.com/' + bad_link

            if new_link.count('github') == 0:
                new_link = 'https://www.github.com/' + new_link

            try:
                name = bad_link.rsplit('/', 1)[1]
                if any(x in name for x in test_strings) != True:
                    bad_r = requests.get(bad_link)
                    bad_file = open("files/bad_" + str(i_true) + "_" + str(j), 'w')
                    bad_file.write(bad_r.text)
                    print("bad_" + str(i_true) + '_' + str(j) + ';' + name, file = file_names_file)
                    bad_file.close()
            except Exception as e:
                logging.warning("============")
                logging.warning("Requests error: " + str(i))
                logging.warning("Requests error: " + bad_link)
                df.drop(index=i, inplace = True)
                logging.warning("============")
                exception_happened = 1
                break
            try:
                name = new_link.rsplit('/', 1)[1]
                if any(x in name for x in test_strings) != True:
                    good_r = requests.get(new_link)
                    good_file = open("files/good_" + str(i_true) + "_" + str(j), 'w')
                    good_file.write(good_r.text)
                    print("good_" + str(i_true) + '_' + str(j) + ';' + name, file = file_names_file)
                    good_file.close()
            except Exception as e:
                logging.warning("============")
                logging.warning("Requests error: " + str(i))
                df.drop(index=i, inplace = True)
                logging.warning("============")
                exception_happened = 1
        if (exception_happened == 0 and len(old_links) > 0):
            i_true = i_true + 1
        elif(exception_happened == 0 and len(old_links) == 0):
            logging.warning("============")
            logging.warning("Requests error: " + str(i))
            df.drop(index=i, inplace = True)


    df.to_csv('commits_final.list', sep=';', header=None, index = None)

