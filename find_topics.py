#!/usr/bin/env python

import pickle
import commands
from collections import defaultdict
import nimfa
from matplotlib import pyplot
from numpy.matrixlib import matrix

c_K = 10 # number of topics
c_NMF_MAXITR = 10

c_DATA_DIR = 'data'

c_MIN_WORD_LEN = 3
c_MAX_WORD_LEN = 15

c_MIN_WC_CUTOFF = 10
c_MAX_WC_CUTOFF = 100

def run(cmd):
   status, output = commands.getstatusoutput(cmd)
   if status != 0:
       print "problem running: ", cmd
   return output

def load_data(data_dir):
    posts = [ ]
    for dump_file in run('ls ' + c_DATA_DIR).split():
        dump = pickle.load(open(c_DATA_DIR + '/' + dump_file))
        for post in dump:
            posts.append(post)
    return posts

def get_post_words(post):
    word_counts = defaultdict(int)
    for comment in post['comments']:
        words = [word.lower().strip() for word in comment.split()]
        for word in words:
            if len(word) >= c_MIN_WORD_LEN and len(word) <= c_MAX_WORD_LEN:
                word_counts[word] += 1
    return word_counts

def add_to_vocab(post_words, vocab):
    for word in post_words:
        vocab[word] += 1

def post_words_matrix(post_word_bags, vocab):
    post_x_words = [ ]
    for url, words in post_word_bags:
        row = [ ]
        for word, count in vocab:
            if word in words:
                row.append(count)
            else:
                row.append(0)
        post_x_words.append(row)
    return post_x_words

def nmf(matrix, k=c_K):
    fctr = nimfa.mf(matrix, seed='random_vcol', method='lsnmf', rank=k, max_iter=c_NMF_MAXITR)
    fctr_res = nimfa.mf_run(fctr)
    return fctr_res.basis(), fctr_res.coef()

if __name__ == "__main__":
    
    vocab = defaultdict(int)
    posts = load_data(c_DATA_DIR)
    post_word_bags = [ ]
    for post in posts:
        post_words = get_post_words(post)
        add_to_vocab(post_words, vocab)
        post_word_bags.append((post['url'], post_words))
    
    vocab = [(word, count) for (word, count) in vocab.items() 
             if count < c_MAX_WC_CUTOFF and count > c_MIN_WC_CUTOFF]
    post_x_words = matrix(post_words_matrix(post_word_bags, vocab))
    basis, coef = nmf(post_x_words)

