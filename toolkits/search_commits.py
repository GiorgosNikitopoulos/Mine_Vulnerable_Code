from cm_response import Commit_Response
import requests
import json
import pandas as pd
import csv
import base64

OUT_FILE = 'mined_coarse_web_search_noned'

xss_cms = Commit_Response(['xss', 'vulnerability'])
print("Populating Commits")
xss_cms.populate_prs()
xss_cms.prs = [x for x in xss_cms.prs if 'PHP' in x.languages]
dataframe = pd.DataFrame()
dataframe['url'] = [x.url for x in xss_cms.prs]

#Scores nn and rf 

#dataframe['nn'] = [x.nn for x in xss_cms.prs]
#dataframe['rf'] = [x.rf for x in xss_cms.prs]

dataframe['nn'] = ['None' for x in xss_cms.prs]
dataframe['rf'] = ['None' for x in xss_cms.prs]

dataframe['cwe'] = ['79' for x in xss_cms.prs]
dataframe['message'] = [x.message for x in xss_cms.prs]
#dataframe['abs_nor_res'] = [base64.b64encode(x.abs_nor_res).decode('utf-8') for x in xss_cms.prs]
dataframe['abs_nor_res'] =  ['None' for x in xss_cms.prs]
dataframe.to_csv(OUT_FILE, sep = ';', quoting = csv.QUOTE_ALL, header = None, index = None)

