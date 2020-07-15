import glob
import json


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

#commits_file = open('commits.list', 'w+')
#cve_cwe_file = open('cvw_cwe.list', 'w+')
root_dir = 'nvd/'
#Each NVD file
for filename in glob.iglob(root_dir + '*.json', recursive=True):
    #print(filename)
    with open(filename, 'r') as my_file:
        year_data = json.load(my_file)

    for cve_item in range(len(year_data['CVE_Items'])):
        cwe = 'None'
        cve_id = year_data['CVE_Items'][cve_item]['cve']['CVE_data_meta']['ID']
        #Get CWE
        for pt_data in year_data['CVE_Items'][cve_item]['cve']['problemtype']['problemtype_data']:
            for description in pt_data['description']:
                temp_cwe = description['value']
                if hasNumbers(temp_cwe) == True:
                    cwe = temp_cwe
        #Get CWE: End

        references = [year_data['CVE_Items'][cve_item]['cve']['references']['reference_data'][i] for i in range(len(year_data['CVE_Items'][cve_item]['cve']['references']['reference_data']))]
        for reference in year_data['CVE_Items'][cve_item]['cve']['references']['reference_data']:
            url = reference['url']
            if(url.count("github") >= 1):
                if(url.count("commit") >= 1):
                    print(cwe + ';' + cve_id + ';' + url )


