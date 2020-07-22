import json
import re
import requests
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
import pdb


ACCESS_TOKEN = '0f493cc6faa42fc640003ab0276c570cb952609d'

class Commit(object):
    def __init__(self, sha, clipped_link):
        #Request and json: START
        self.api_link = 'https://api.github.com/repos/' + clipped_link + '/commits/' + sha
        #print(self.api_link)
        self.out = requests.get(self.api_link, auth=('GiorgosNikitopoulos', ACCESS_TOKEN))
        self.data = json.loads(self.out.text)
        #Request and json: END
        try:
            if self.data['message'] == "Not found":
                return None
        except Exception as e:
            if e == KeyError:
                pass

        #print(self.data)
        #File related: START
        try:
            self.files = self.data['files']
        except Exception as e:
            self.files = None

        if self.files != None:
            self.file_urls = [x['raw_url'] for x in self.files]
            self.file_paths = [x['filename'] for x in self.files]
            self.filenames = [x.rsplit('/', 1)[-1] for x in self.file_paths]
        #File related: END

        #Message related: START
        self.message = self.data['commit']['message']
        self.lmessage = self.message.lower()
        self.clean_message = self.clean_chars(self.lmessage)
        self.message_lines = self.clean_message.splitlines()
        #print(self.message_lines)
        self.stemmed_message = self.stem_words(self.clean_message)
        self.message_wlist_s = self.stemmed_message.split()
        self.message_wlist = self.clean_message.split()
        self.merge_tag = self.is_merge_tag(self.clean_message)
        #print(self.merge_tag)

        #Message related: END

    def is_merge_tag(self, description):
        if description.count('merge tag') > 0:
            return True
        else:
            return False

    def get_cwe(self, description):
        cwe_dict = {'476': ['null pointer dereference'],
            '79': ['cross site scripting', 'xss', 'cross-site scripting'],
            '22': ['path traversal', 'directory traversal'],
            '89': ['sql injection', 'sqli'],
            '426': ['untrusted search path'],
            '20': ['improper input validation'],
            '125': ['out-of-bounds read', 'out of bounds read'],
            '416': ['use after free'],
            '119': ['buffer overflow', 'bof'],
            '190': ['integer overflow']
        }
        description = description.lower()
        description = self.clean_chars(description)
        description = self.stem_words(description)
        for key in cwe_dict:
            for each_string in cwe_dict[key]:
                comparable = self.clean_chars(each_string)
                comparable = self.stem_words(comparable)
                if comparable in description:
                    return key
        return None

    def stem_words(self, text):
        ps = PorterStemmer()
        words = word_tokenize(text)
        out_words = list()
        for w in words:
            out_words.append(ps.stem(w))
        return(" ".join(out_words))

    def clean_chars(self, text):
        clean = re.sub(r"[-()/:,.;<>@#{}'?!&$]+\ *", " ", text)
        return(clean)

