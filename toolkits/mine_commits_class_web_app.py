import glob
import logging
import time
import pandas as pd
import re
import shutil
import os
import pickle
import json
import requests
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from keras import backend as K
from keras import activations
from commit import Commit
import tensorflow as tf
import warnings
import pickle
import numpy as np
import pdb
import base64
import csv

CHECKPOINT_PATH = '../assets/web_app.ckpt'
OUTPUT_PATH = '../assets/web_vulns.list'
OUTPUT_PATH_CSV = '../assets/web_vulns.csv'
TRAIN_TEST_PATH = '../assets/train_test_stem.csv'
MODEL_PATH = '../assets/model.pickle'
VECTORIZER_PATH = '../assets/vectorizer.pickle'
REPO_PATH = '../assets/web_app.list'
ACCESS_TOKEN = ''
MAX_SEQ_LENGTH    = 500

class CommitMiner(object):
    def __init__(self, repo_path=REPO_PATH, model_path=MODEL_PATH,
                 vectorizer_path=VECTORIZER_PATH,
                 ):
        self.csv_file = pd.read_csv(repo_path, sep = ';')
        self.repo_list = self.csv_file[self.csv_file.columns[0]]

        self.forest = pickle.load(open(model_path, 'rb'))
        self.vectorizer = pickle.load(open(vectorizer_path, 'rb'))

        #Load neural network data
        self.model = tf.keras.models.load_model('../assets/model-1.h5')
        self.model_linear_activation = tf.keras.models.load_model('../assets/model-1.h5')
        self.model_linear_activation.layers[-1].activation = activations.linear
        self.model_linear_activation.save('../assets/model-1-linear.h5')
        self.model_linear_activation = tf.keras.models.load_model('../assets/model-1-linear.h5')
        self.nn_tokenizer = pickle.load(open('../assets/tokenizer.pickle', "rb"))
        self.nn_word2id= pickle.load(open('../assets/word_index.pickle', "rb"))
        self.id2word = {v: k for k, v in self.nn_word2id.items()}
        #iterate_through_repos(repo_list, forest, vectorizer)


    def get_cwe(self, description):
        cwe_dict = {
            '79': ['cross site scripting', 'xss', 'cross-site scripting'],
            '89': ['sql injection', 'sqli'],
            '352': ['csrf', 'cross site request forgery', 'request forgery', 'cross-site request forgery']
        }
        description = description.lower()
        description = self.clean_chars(description)
        description = self.stem_words(description)
        description = description.split()
        for key in cwe_dict:
            for each_string in cwe_dict[key]:
                comparable = self.clean_chars(each_string)
                comparable = self.stem_words(comparable)
                comparable = comparable.split()
                #print(description)
                #print(comparable)
                if self.is_sublist(comparable, description) == True:
                    return key
        return None

    def is_sublist(self, ys, xs):
        for i in range(len(xs) - len(ys)):
            if xs[i:i + len(ys)] == ys:
                return True
        return False

    def get_browsable_url(self, url):
        url = url.replace('api', 'www')
        url = url.replace('commits', 'commit')
        url = url.replace('/repos', '')
        url = url.replace('/git', '')
        return url

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

    def vectorize_text(self, text):
        text = self.clean_chars(text)
        text = self.stem_words(text)
        text = [text]
        X = self.vectorizer.transform(text)
        X = X.toarray()

        return X

    def iterate_through_commits(self, repo):
        clipped_link = repo.split('github.com/', 1)[1]
        clipped_link = clipped_link.split('.git', 1)[0]

        with open(CHECKPOINT_PATH, 'w') as ckpt_path:
            ckpt_path.write(clipped_link)


        #Iterate through pages
        i = 0
        while True:
            api_link = 'https://api.github.com/repos/' + clipped_link + '/commits?per_page=100&page=' + str(i)
            out = requests.get(api_link, auth=('GiorgosNikitopoulos', ACCESS_TOKEN))

            try:
                data = json.loads(out.text)
            except Exception as e:
                logging.exception(api_link)
                logging.exception(e.message)
                break
            #print(len(data))
            i = i + 1

            if i % 10 == 0:
                logging.warning(clipped_link)
                logging.warning(data)
            if(len(data) == 0):
                break
            #print(data)
            for count, commit in enumerate(data):
                message = (commit['commit']['message'])
                #print(message)
                url = (commit['commit']['url'])
                sha = (commit['sha'])
                #pdb.set_trace()
                nn_sequence = self.nn_tokenizer.texts_to_sequences([message])
                nn_sequence = tf.keras.preprocessing.sequence.pad_sequences(nn_sequence,
                                                                            maxlen=MAX_SEQ_LENGTH,
                                                                            padding='post')


                #nn_sequence = tf.expand_dims(nn_sequence, axis=0)
                vector = self.vectorize_text(message)
                self.forest.verbose = False
                result = (self.forest.predict(vector))
                #if result == 0:
                #    print('FOREST;' + self.get_browsable_url(url))
                if self.get_cwe(message) == None:
                    pass
                else:
                    if result == 0:
                        forest_result = 0
                    else:
                        forest_result = 1
                    my_commit = Commit(sha, clipped_link)
                    #print(my_commit.merge_tag)
                    if my_commit.merge_tag == True:
                        #print('Start for')
                        continue
                    #print(self.get_cwe(message) + ';' + self.get_browsable_url(url))
                    #print(self.model.predict(nn_sequence))
                    grads = self.compute_saliency_matrix(nn_sequence)
                    abs_nor_res = self.abs_nor_salmat(grads, nn_sequence, two_dimensions = False, range_normalize = True)

                    anr_pickled = pickle.dumps(abs_nor_res) # Abs_nor_res pickled
                    anr_b64_encoded = base64.b64encode(anr_pickled).decode('utf-8')
                    output_file = open(OUTPUT_PATH, 'a')
                    print(self.get_browsable_url(url) + ';' + str(self.model.predict(nn_sequence)) + ';' + str(forest_result) + ';' + self.get_cwe(message) + ';' + str(anr_b64_encoded))
                    output_file.write(self.get_browsable_url(url) + ';' + str(self.model.predict(nn_sequence)) + ';' + str(forest_result) + ';' + self.get_cwe(message) + ';' + str(anr_b64_encoded) + '\n')
                    output_file.close()
                    with open(OUTPUT_PATH_CSV, 'a', newline = '') as csvfile:
                        writer = csv.writer(csvfile, delimiter = ';', quotechar = '"', quoting = csv.QUOTE_ALL)
                        writer.writerow(self.get_browsable_url(url),  str(self.model.predict(nn_sequence)),str(forest_result), self.get_cwe(message), str(anr_b64_encoded))
                    #self.html_abs_nor_res(abs_nor_res)

            time.sleep(1)

    def iterate_through_repos(self):
        with open(CHECKPOINT_PATH, 'r') as ckpt_path:
            checkpoint = ckpt_path.read()
            checkpoint = checkpoint.strip()
        START_FLAG = 0
        for repo in self.repo_list:
            if checkpoint in repo:
                START_FLAG = 1
            if repo.count('github') >= 1 and START_FLAG == 1:
                print('Here')
                self.iterate_through_commits(repo)

    def compute_saliency_matrix(self, input_x):
        input_tensors = [self.model_linear_activation.input, K.learning_phase()]
        #pdb.set_trace()
        saliency_input = self.model_linear_activation.layers[2].output
        saliency_output = self.model_linear_activation.layers[-1].output
        gradients = self.model_linear_activation.optimizer.get_gradients(saliency_output, saliency_input)
        compute_gradients = K.function(inputs=input_tensors, outputs=gradients)
        #matrix = compute_gradients([np.array([input_x]),0])[0][0,:,:]
        matrix = compute_gradients([np.array(input_x),0])[0][0,:,:]

        return matrix

    def html_abs_nor_res(self, abs_nor_res):
        for k, v in abs_nor_res.items():
            print('<font style="background: rgba(255, 0, 0, {})">{}</font>'.format(v, k))

    #Absolute and normalize saliency matrix
    #If two_dimensions == False then the embedding size dimension values are all summed
    #If range_normalize == True then all values are divided by the max
    #Returns dictionary of words/values
    def abs_nor_salmat(self, matrix, input_x, two_dimensions = False, range_normalize = True):
        input_x = input_x[0]
        tokens = [self.id2word[x] for x in input_x if x!=0]
        absolute_mat = np.absolute(matrix[:len(tokens),:])
        if two_dimensions == False:
            summed_mat = [np.sum(i) for i in absolute_mat]
            if range_normalize == True:
                summed_mat = [i / max(summed_mat) for i in summed_mat]

        return (dict(zip(tokens, summed_mat)))
