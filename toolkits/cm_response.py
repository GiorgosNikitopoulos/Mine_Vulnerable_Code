import requests
import json
import math
from cm_class import Commit
import pickle
import logging
import datetime
import tensorflow as tf
import pickle
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from keras import backend as K
from keras import activations
import numpy as np

ACCESS_TOKEN = ''
MAX_SEQ_LENGTH = 500
MODEL_PATH = '../assets/model.pickle'
VECTORIZER_PATH = '../assets/vectorizer.pickle'
class Commit_Response(object):
    def __init__(self, search_words):
        self.nn_tokenizer = pickle.load(open('../assets/tokenizer.pickle', "rb"))
        self.model = tf.keras.models.load_model('../assets/model-1.h5')
        self.model_linear_activation = tf.keras.models.load_model('../assets/model-1.h5')
        self.model_linear_activation.layers[-1].activation = activations.linear
        self.model_linear_activation.save('../assets/model-1-linear.h5')
        self.model_linear_activation = tf.keras.models.load_model('../assets/model-1-linear.h5')
        self.nn_word2id= pickle.load(open('../assets/word_index.pickle', "rb"))
        self.id2word = {v: k for k, v in self.nn_word2id.items()}

        self.forest = pickle.load(open(MODEL_PATH, 'rb'))
        self.forest.verbose = False
        self.vectorizer = pickle.load(open(VECTORIZER_PATH, 'rb'))


        self.url_search_string = 'https://api.github.com/search/commits?q='
        for each_search_word in search_words:
            self.url_search_string = self.url_search_string + '+' + each_search_word



        self.items = list()
        header = {'Accept': 'application/vnd.github.cloak-preview'}
        previous_count = 0
        self.length = 0
        date = datetime.date.today()
        delta = datetime.timedelta(days=20)
        for i in range(300):
            datestring = date.strftime('%Y-%m-%d')
            url = self.url_search_string + '+author-date:%3E' + datestring + '&sort=created&order=asc'
            print(url)
            out = requests.get(url, headers = header, auth=('GiorgosNikitopoulos', ACCESS_TOKEN))
            response = json.loads(out.text)
            try:
                current_count = response['total_count']
            except Exception as e:
                logging.warning(e)
                break

            print('CurrentCount is:')
            print(current_count)
            count = current_count - previous_count
            print('Count is:')
            print(count)

            #Obscure case in which Github fetches results on false dates
            if(count < 0):
                count = 0
                if current_count < previous_count:
                    current_count = previous_count

            j = count
            if count > 1000:
                j = 1000

            #Iterate Through pages, k = page, j = count for each year
            for page in range(1, 10):
                if j > 100:
                    per_page = 100
                else:
                    per_page = j
                url = self.url_search_string + '+author-date:%3E' + datestring + '&sort=created&order=asc' +  '&page=' + str(page) + '&per_page=' + str(per_page)
                print(url)
                out = requests.get(url, headers = header, auth=('GiorgosNikitopoulos', ACCESS_TOKEN))
                response = json.loads(out.text)
                self.items.extend(response['items'])
                self.length = self.length + per_page
                j = j - per_page
                if(j == 0):
                    break

            previous_count = current_count
            date = date - delta
        self.prs = [Commit() for i in range(len(self))]
    def __len__(self):
        return self.length
    def populate_prs(self):
        for i in range(len(self)):
            self.prs[i].sha = self.items[i]['sha']
            self.prs[i].message = self.items[i]['commit']['message']
            self.prs[i].repository = self.items[i]['repository']['url']
            self.prs[i].languages_url = self.items[i]['repository']['languages_url']
            self.prs[i].url = self.items[i]['url']
            self.prs[i].nn, self.prs[i].rf = self.get_scores(self.prs[i].message)
            self.prs[i].populate_languages()
            nn_sequence = self.nn_tokenizer.texts_to_sequences([self.prs[i].message])
            nn_sequence = tf.keras.preprocessing.sequence.pad_sequences(nn_sequence,
                                                                    maxlen = MAX_SEQ_LENGTH,
                                                                    padding = 'post')
            grads = self.compute_saliency_matrix(nn_sequence)
            abs_nor_res = self.abs_nor_salmat(grads, nn_sequence, two_dimensions = False, range_normalize = True)
            self.prs[i].abs_nor_res = pickle.dumps(abs_nor_res)


    def get_scores(self, message):
        ##NN Stuff
        nn_sequence = self.nn_tokenizer.texts_to_sequences([message])
        nn_sequence = tf.keras.preprocessing.sequence.pad_sequences(nn_sequence,
                                                                    maxlen = MAX_SEQ_LENGTH,
                                                                    padding = 'post')
        nn_prediction_str = self.model.predict(nn_sequence)

        #RF Stuff
        vector = self.vectorize_text(message)
        #print(vector)
        #print(message)
        rf_result_str = str(self.forest.predict(vector))

        return nn_prediction_str, rf_result_str


    def vectorize_text(self, text):
        text = self.clean_chars(text)
        text = self.stem_words(text)
        text = [text]
        X = self.vectorizer.transform(text)
        X = X.toarray()

        return X

    def clean_chars(self, text):
        clean = re.sub(r"[-()/:,.;<>@#{}'?!&$]+\ *", " ", text)
        return(clean)

    def stem_words(self, text):
        ps = PorterStemmer()
        words = word_tokenize(text)
        out_words = list()
        for w in words:
            out_words.append(ps.stem(w))
        return(" ".join(out_words))

    def compute_saliency_matrix(self, input_x):
        input_tensors = [self.model_linear_activation.input, K.learning_phase()]
        saliency_input = self.model_linear_activation.layers[2].output
        saliency_output = self.model_linear_activation.layers[-1].output
        gradients = self.model_linear_activation.optimizer.get_gradients(saliency_output, saliency_input)
        compute_gradients = K.function(inputs = input_tensors, outputs = gradients)
        matrix = compute_gradients([np.array(input_x), 0])[0][0, :, :]

        return matrix

    def abs_nor_salmat(self, matrix, input_x, two_dimensions = False, range_normalize = True):
        input_x = input_x[0]
        tokens = [self.id2word[x] for x in input_x if x != 0]
        absolute_mat = np.absolute(matrix[:len(tokens), :])
        if two_dimensions == False:
            summed_mat = [np.sum(i) for i in absolute_mat]
            if range_normalize == True:
                summed_mat = [i / max(summed_mat) for i in summed_mat]

        return (dict(zip(tokens, summed_mat)))

