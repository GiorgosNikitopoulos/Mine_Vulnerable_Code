import csv
import json

NAME_FILE = "file_names.list"
COMMIT_FILE = "commits.list"
OUTPUT_FILE = "out.json"

num_lines = sum(1 for line in open(COMMIT_FILE))
json_list = list()
names = [[] for n in range((num_lines))]
with open(NAME_FILE, newline = '') as name_file:
    reader = csv.reader(name_file, delimiter=';')
    for row in reader:
        index = int(row[0].split('_')[1])
        #print(index)
        #print(row)
        names[index].append({'database_name': row[0], 'original_name': row[1]})

with open(COMMIT_FILE, newline = '') as f:
    reader = csv.reader(f, delimiter=';')
    i = 0
    for row in reader:
        data = {'cwe': row[0], 'cve': row[1], 'url': row[2], 'files': names[i]}
        json_list.append(data)
        i = i + 1

with open(OUTPUT_FILE, 'w') as out_file:
    json.dump(json_list, out_file)
