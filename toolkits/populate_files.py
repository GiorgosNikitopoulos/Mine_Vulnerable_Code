from collections import Counter
import os

#cancel_out_list = [None, 'rst', 'kwj', 'am', 'ac', 'gitignore', 'txt', 'md', 'test', 'png', 'uuid', 'pcap', 'out','sbt' ]
file_exts = ['c', 'php', 'js', 'py', 'h', 'rb', 'java', 'cpp', 'go', 'html', 'xml', 'tpl', 'json', 'cs', 'cc', 'pm', 'sh', 'phpt', 'm', 'inc', 'scala', 'cxx', 'jsp', 'ctp', 'jelly', 't', 'htm', 'scss', 'tt', 'as', 'rs', 'pl', 'S', 'spec', 'conf', 'vim', 'htaccess', 'hh', 'lua', 'coffee', 'ts', 'css', 'phtml', 'cgi', 'yml', 'sql', 'yaml']
with open("commits.list", 'r') as file_desc:
    all_lines = file_desc.readlines()
all_lines = [x.strip() for x in all_lines]
cwes = [x.split(';', 1)[0] for x in all_lines]
with open("file_names.list", 'r') as file_desc:
    all_lines = file_desc.readlines()
all_lines = [x.strip() for x in all_lines]
original_filenames = [x.split(';')[1] for x in all_lines]
dataset_filenames = [x.split(';')[0] for x in all_lines]
filename_extentions = [x.rsplit('.', 1)[1] if len(x.split('.')) == 2 else None for x in original_filenames]
unique_file_paths = list()
file_paths = list()

for i, d_filename in enumerate(dataset_filenames):
    cwe_id = int(d_filename.split('_')[1])
    cwe = cwes[cwe_id]
    if filename_extentions[i] in file_exts:
        #print(filename_extentions[i])
        #print(cwe)
        unique_file_paths.append(cwe + '/' + filename_extentions[i])
        file_paths.append(cwe + '/' + filename_extentions[i] + '/' + d_filename)
        os.system('cp files/' + d_filename + ' dataset/' + cwe + '/' + filename_extentions[i] + '/' + d_filename)
