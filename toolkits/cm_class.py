import requests
import json

ACCESS_TOKEN = ''
class Commit(object):
    def __init__(self):
        self.sha = None
        self.url = None
        self.repository = None
        self.message = None
        self.nn = None
        self.rf = None
        self.languages_url = None
    def populate_languages(self):
        header = {'Accept': 'application/vnd.github.cloak-preview'}
        response = requests.get(self.languages_url, headers = header, auth = ('GiorgosNikitopoulos', ACCESS_TOKEN))
        response = json.loads(response.text)
        self.languages = response
