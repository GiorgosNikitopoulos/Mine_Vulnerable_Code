#!/usr/env/bin python3
import pandas as pd
from commit_l import Commit
from commit_m import CommitM
import curses
from silence_tensorflow import silence_tensorflow
import tensorflow as tf
from curseXcel import Table
from nltk.stem import PorterStemmer
import pdb
import pyperclip
import pickle
import signal
from commit_message import CommitMessage
from mine_commits_class import CommitMiner
import os
import csv
import tensorflow.python.util.deprecation as deprecation
import logging
import base64

MAX_SEQ_LENGTH = 500
MINED_PATH = '../assets/mined_cms.list'
FALSE_POSITIVE_PATH = '../assets/false_positives_cms.list'
DENIED_PATH = '../assets/denied_cms.list'
DIRTY_DATA = '../assets/mined_coarse_web_search'

def common_prefix(sa, sb):
    def _iter():
        for a, b in zip(sa, sb):
            if a == b:
                yield a
            else:
                return
    return ''.join(_iter())

def main(stdscr):
    #signal.signal(signal.SIGINT, lambda sig, frame: pdb.Pdb().set_trace(frame))
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    deprecation._PRINT_DEPRECATION_WARNINGS = False
    logging.disable(logging.CRITICAL)
    x = 0
    #trips = pd.read_csv('mined_coarse', sep=';', header = None)
    #trips = pd.read_csv('pull_requests_coarse', sep=';', header = None, quoting=csv.QUOTE_ALL)
    trips = pd.read_csv(DIRTY_DATA, sep=';', header = None, quoting=csv.QUOTE_ALL)

    ps = PorterStemmer()
    #pdb.set_trace()
    for i in range(1, 252):
        curses.init_color(i, 1000, 1000 - ((i - 1) * 4), 1000 - ((i - 1) * 4))
        curses.init_pair(i, i, curses.COLOR_BLACK)
    max_y, max_x = stdscr.getmaxyx()
    table = Table(stdscr, len(trips), 4, 30, max_x, max_y, spacing=1, col_names=True)
    m = 0
    while m < 3:
        table.set_column_header("Col " + str(m+1), m)
        m += 1
    table.set_column_header("Commit Url ", 0)
    table.set_column_header("Neural Network Decisions (bad, good)", 1)
    table.set_column_header("Random Forest Decision", 2)
    table.set_column_header("CWE", 3)
    m = 0
    while m < len(trips):
        n = 0
        while n < 4:
            table.set_cell(m, n, trips.loc[m, n])
            n += 1
        m += 1
    #table.delete_row(2)
    table.refresh()
    while (x != 'q'):
        table.refresh()
        x = stdscr.getkey()
        if (x == 'j'):
            table.cursor_left()
        elif (x == 'l'):
            table.cursor_right()
        elif (x == 'k'):
            table.cursor_down()
        elif (x == 'i'):
            table.cursor_up()
        elif(x == 'c'):
            cursor_x = table.cursor[0]
            cursor_y = table.cursor[1]
            content = table.table[cursor_x][cursor_y]
            link = content.replace('api.github.com/repos', 'github.com')
            pyperclip.copy(str(link))
        elif(x == 'd'):
            cursor_x = table.cursor[0]
            cursor_y = table.cursor[1]
            link = table.table[cursor_x][0]
            idxnames = trips[trips[0] == link].index
            trips.drop(idxnames, inplace = True)
            with open(DENIED_PATH, 'a+') as fp:
                fp.write(link + ';' + cwe + '\n')
            table.delete_row(cursor_x - 1)
        elif(x == 'f'):
            cursor_x = table.cursor[0]
            cursor_y = table.cursor[1]
            link = table.table[cursor_x][0]
            cwe = table.table[cursor_x][3]
            idxnames = trips[trips[0] == link].index
            trips.drop(idxnames, inplace = True)
            with open(FALSE_POSITIVE_PATH, 'a+') as fp:
                fp.write(link + ';' + cwe + '\n')
            table.delete_row(cursor_x - 1)
        elif(x == 'a'):
            cursor_x = table.cursor[0]
            cursor_y = table.cursor[1]
            link = table.table[cursor_x][0]
            idxnames = trips[trips[0] == link].index
            trips.drop(idxnames, inplace = True)
            cwe = table.table[cursor_x][3]
            with open(MINED_PATH, 'a+') as fp:
                fp.write(link + ';' + cwe + '\n')
            table.delete_row(cursor_x - 1)
        elif(x == 'w'):
            cursor_x = table.cursor[0]
            cursor_y = table.cursor[1]

            link = table.table[cursor_x][0]

            if trips[trips[0] == link][5].values[0] != 'None':
                commit = CommitM(trips[trips[0] == link][4].values[0])
                original_message = commit.message
                message = commit.stemmed_message
                abs_nor_res = pickle.loads(base64.b64decode(trips[trips[0] == link][5].values[0]))
            else:
                commit = Commit(link)
                #Get saliency map
                miner = CommitMiner()
                #clean_message = commit.clean_message
                original_message = commit.message
                message = commit.stemmed_message
                nn_sequence = miner.nn_tokenizer.texts_to_sequences([message])
                nn_sequence = tf.keras.preprocessing.sequence.pad_sequences(nn_sequence,
                                                                            maxlen = MAX_SEQ_LENGTH,
                                                                            padding = 'post')
                grads = miner.compute_saliency_matrix(nn_sequence)
                abs_nor_res = miner.abs_nor_salmat(grads, nn_sequence, two_dimensions = False, range_normalize = True)

            mypad = curses.newpad(142, 140)
            mypad_pos = 0
            mypad.scrollok(True)

            broken_words = list()
            righter = original_message
            for word in commit.message_wlist_cs:
                lefter = righter.split(word, 1)[0]
                righter = righter.split(word, 1)[1]
                broken_words.append(lefter)
                broken_words.append(word)
            broken_words.append(righter)
            broken_words = [string for string in broken_words if string != ""]

            for broken_word in broken_words:
                try:
                    each_value = abs_nor_res[ps.stem(broken_word.lower())]
                    coloured_word = common_prefix(ps.stem(broken_word.lower()), broken_word.lower())
                    ending = broken_word.split(coloured_word)[1]
                    each_color = int(((each_value * 1000) / 4 )) + 1
                    mypad.addstr(coloured_word, curses.color_pair(each_color))
                    mypad.addstr(ending, curses.color_pair(1))
                    #PRINT COLOURED WORD
                except Exception as e:
                    #if e == KeyError:
                    #Print and colour white
                    mypad.addstr(broken_word, curses.color_pair(1))
                    #mypad.addstr(str(curses.COLORS), curses.color_pair(1))

            #mypad.addstr(commit.clean_message)
            #mypad.addstr(str(broken_message))


            mypad.refresh(mypad_pos, 0, 0, 0, 35, 140)
            y = 0
            while(y != 'q'):
                y = mypad.getkey()
                if y == 'j':
                    mypad_pos += 1
                    mypad.refresh(mypad_pos, 0, 0, 0, 35, 140)
                elif y == 'k':
                    if (mypad_pos >= 0):
                        mypad_pos -= 1
                        mypad.refresh(mypad_pos, 0, 0, 0, 35, 140)
                elif y == 'p':
                    pdb.set_trace()
        elif(x == 'e'):
            cursor_x = table.cursor[0]
            cursor_y = table.cursor[1]
            link = table.table[cursor_x][0]
            #Get API Link from browsable
            #pdb.set_trace()
            try:
                message = trips[trips[0] == link][4].values[0]
            except Exception as e:
                message = None
            mypad = curses.newpad(142, 140)
            mypad_pos = 0
            mypad.scrollok(True)
            if message != None:
                mypad.addstr(str(message), curses.color_pair(1))
            else:
                mypad.addstr('Message Error: None', curses.color_pair(1))
            y = 0
            mypad.refresh(mypad_pos, 0, 0, 0, 35, 140)
            while(y != 'e'):
                y = mypad.getkey()
                if y == 'j':
                    mypad_pos += 1
                    mypad.refresh(mypad_pos, 0, 0, 0, 35, 140)
                elif y == 'k':
                    if (mypad_pos >= 0):
                        mypad_pos -= 1
                        mypad.refresh(mypad_pos, 0, 0, 0, 35, 140)


    trips.to_csv('mined_coarse_web_search', sep = ';', index = False, header = False, quoting=csv.QUOTE_ALL)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
deprecation._PRINT_DEPRECATION_WARNINGS = False
logging.disable(logging.WARNING)
stdscr = curses.initscr()

curses.noecho()
curses.cbreak()
stdscr.keypad(True)

curses.wrapper(main)

curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()
