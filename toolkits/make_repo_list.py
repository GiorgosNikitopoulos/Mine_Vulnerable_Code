#from commit_l import Commit
import pandas as pd
import pdb

allowed_cwes = ['CWE-79', 'CWE-89', 'CWE-352']
dataframe = pd.read_csv('commits.list', sep = ';')

#pdb.set_trace()
def remove_duplicates(x):
      return list(dict.fromkeys(x))

output_links = list()
for index, row in dataframe.iterrows():
    link = row[2]
    cwe = row[0]
    project = link.rsplit('/', 2)[0]
    #print(cwe)
    if cwe in allowed_cwes:
        output_links.append(project)
#print(output_links)
output_links = remove_duplicates(output_links)
for link in output_links:
    print(link)
