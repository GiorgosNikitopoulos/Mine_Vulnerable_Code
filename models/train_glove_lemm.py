# WORD-level
MAX_NUM_WORDS     = 1000
EMBEDDING_DIM     = 300
MAX_SEQ_LENGTH    = 150
USE_GLOVE         = True
KERNEL_SIZES      = [3,4,5]
FEATURE_MAPS      = [150,150,150]

# GENERAL
DROPOUT_RATE      = 0.4
HIDDEN_UNITS      = 100
NB_CLASSES        = 2
USE_CHAR          = False

# LEARNING
BATCH_SIZE        = 100
NB_EPOCHS         = 5
RUNS              = 5
VAL_SIZE          = 0.2
CUTOFF = 0.7


import pickle
import numpy as np
from cnn_model import CNN
from sklearn.model_selection import train_test_split
import os
import re
import string
from nltk.corpus import stopwords
import pandas as pd
import tensorflow as tf
import pdb
from sklearn import metrics

TRAIN_PATH = "lemmatized_train.csv"
TEST_PATH = "lemmatized_test.csv"



def create_glove_embeddings():
    print('Pretrained embedding GloVe is loading...')

    embeddings_index = {}
    with open('vectors_lemmatized.txt') as glove_embedding:
        for line in glove_embedding.readlines():
            values = line.split()
            word   = values[0]
            coefs  = np.asarray(values[1:], dtype='float64')
            embeddings_index[word] = coefs
    print('Found %s word vectors in GloVe embedding\n' % len(embeddings_index))

    embedding_matrix = np.zeros((MAX_NUM_WORDS, EMBEDDING_DIM))

    for word, i in tokenizer.word_index.items():

        if i >= MAX_NUM_WORDS:
            continue

        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

    return tf.keras.layers.Embedding(
        input_dim=MAX_NUM_WORDS,
        output_dim=EMBEDDING_DIM,
        input_length=MAX_SEQ_LENGTH,
        weights=[embedding_matrix],
        trainable=True,
        name="word_embedding"
    )


train_df = pd.read_csv(TRAIN_PATH, encoding = 'utf-8', sep = ';')
train_df["vuln"] = train_df["vuln"].apply(str)
train_df["vuln"] = train_df["vuln"].replace(to_replace = "good", value = 1)
train_df["vuln"] = train_df["vuln"].replace(to_replace = "bad", value = 0)
train_df["all_text"] = train_df["all_text"].apply(str)
y_train = train_df["vuln"]
x_train = train_df["all_text"]
test_df = pd.read_csv(TEST_PATH, encoding = 'utf-8', sep = ';')
test_df["vuln"] = test_df["vuln"].apply(str)
test_df["vuln"] = test_df["vuln"].replace(to_replace = "good", value = 1)
test_df["vuln"] = test_df["vuln"].replace(to_replace = "bad", value = 0)
test_df["all_text"] = test_df["all_text"].apply(str)

y_test = test_df["vuln"]
x_test= test_df["all_text"]

tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=MAX_NUM_WORDS)
tokenizer.fit_on_texts(x_train)
sequences = tokenizer.texts_to_sequences(x_train)
#pdb.set_trace()
#print(sequences)
#matrix = tokenizer.sequences_to_matrix(sequences)

word_index = tokenizer.word_index

pickle.dump(word_index, open('word_index_oh.pickle', "wb"))
pickle.dump(tokenizer, open('tokenizer_oh.pickle', "wb"))
id2word = {v: k for k, v in word_index.items()}


result = [len(x.split()) for x in x_train]

histories = []

for i in range(RUNS):
    print('Running iteration %i/%i' % (i+1, RUNS))
    random_state = np.random.randint(1000)

    word_data = tf.keras.preprocessing.sequence.pad_sequences(sequences, maxlen=MAX_SEQ_LENGTH, padding='post')
    #pdb.set_trace()
    X_train, X_val, y_train, y_val = train_test_split(word_data, tf.keras.utils.to_categorical(y_train), test_size=VAL_SIZE, random_state=random_state)
    #X_train = tokenizer.sequences_to_matrix(X_train.tolist(), mode='freq')
    #X_val = tokenizer.sequences_to_matrix(X_val.tolist(), mode='freq')
    #print(type(X_train))
    #pdb.set_trace()
    emb_layer = None
    emb_layer = create_glove_embeddings()
    model = CNN(
                embedding_layer   = emb_layer,
                num_words         = MAX_NUM_WORDS,
                embedding_dim     = EMBEDDING_DIM,
                kernel_sizes      = KERNEL_SIZES,
                feature_maps      = FEATURE_MAPS,
                max_seq_length    = MAX_SEQ_LENGTH,
                use_char          = USE_CHAR,
                dropout_rate      = DROPOUT_RATE,
                hidden_units      = HIDDEN_UNITS,
                nb_classes        = NB_CLASSES

    ).build_model()
    model.compile(
                #loss='categorical_crossentropy',
                loss='binary_crossentropy',
                optimizer=tf.optimizers.Adam(learning_rate=0.001),
                #optimizer=tf.optimizers.SGD(learning_rate = 0.0001, momentum=0.9),
                metrics=['accuracy']

    )
    history = model.fit(
                X_train, y_train,
                epochs=NB_EPOCHS,
                batch_size=BATCH_SIZE,
                validation_data=(X_val, y_val),
        callbacks=[
            tf.keras.callbacks.ModelCheckpoint(
                                'model-glove-lemmoh.h5', monitor='val_loss', verbose=1, save_best_only=True, mode='min'

            ), tf.keras.callbacks.ReduceLROnPlateau()

        ]
    )

    test_sequences = tokenizer.texts_to_sequences(x_test)
    padded_test_sequences = tf.keras.preprocessing.sequence.pad_sequences(test_sequences, maxlen=MAX_SEQ_LENGTH, padding='post')
    results = model.predict(padded_test_sequences)
    #print(results[0])
    #print(results[0][0])
    y_results = list()
    for result in results:
        if result[0] > CUTOFF:
            y_results.append(0)
        else:
            y_results.append(1)
    #print(y_results)
    print(metrics.classification_report(y_test.tolist(), y_results ))
    histories.append(history.history)



