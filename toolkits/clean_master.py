import pandas as pd

df = pd.read_csv('commits.list', sep=';', header=None)
masters = pd.read_csv('repos_with_master_in_name.list', header = None)
all_master_commits = df[df[2].str.contains('master')]

for repo in masters.itertuples():
    #print(repo[1])
    all_master_commits = all_master_commits[all_master_commits[2].str.contains(repo[1]) == False]
    print(all_master_commits)
df = df.drop(all_master_commits.index)
