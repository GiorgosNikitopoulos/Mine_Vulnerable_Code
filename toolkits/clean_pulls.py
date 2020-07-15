import lxml.html
import requests



def clean_number_pull(url):
    right_hander = url.split("pull/")[1]
    left_hander = url.split("pull/")[0]
    right_hander = right_hander.split("/", 1)[1]

    whole = left_hander + right_hander
    whole = whole.replace("commits", "commit")
    if(whole.count('www.gi') != 0):
        entire_url = "https://www.github.com" + whole
    else:
        entire_url = whole
    return entire_url

link_file = open('cve_cwe.list', 'r')
content = link_file.readlines()
content = [x.strip() for x in content]
for link in content:
    cwe = link.split(';', 2)[0]
    cve = link.split(';', 2)[1]
    link = link.split(';', 2)[2]
    #print('===============')
    #print(cve)
    #print(link)
    #print('===============')
    if(link.split("/")[-1] == "commits"):
        html = requests.get(link)
        doc = lxml.html.fromstring(html.content)
        list_of_urls = doc.xpath('//*[@id="commits_bucket"]/div/div/ol[*]/li/div[1]/p/a/@href')
        for url in list_of_urls:
            if("issues" in url):
                continue
            res = clean_number_pull(url)
            print(cwe + ';' + cve + ";" + res)


    elif("pull" in link):
        print(cwe + ';' + cve + ';' + clean_number_pull(link))
    else:
        print(cwe + ';' + cve + ";" + link)

