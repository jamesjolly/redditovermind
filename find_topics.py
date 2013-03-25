#!/usr/bin/env python
"""
redditovermind 0.1
Copyright (C) 2013, James Jolly (jamesjolly@gmail.com)
See MIT-LICENSE.txt for legalese and README.md for usage.
"""

import pickle
import commands
from collections import defaultdict
import nimfa
from numpy.matrixlib import matrix
from string import punctuation

c_DATA_DIR = 'data' # dir containing output of grab_reddits

c_K = 5 # number of topics
c_NMF_MAXITR = 5000 # when to bail if taking too long to factorize

c_MIN_WORD_LEN = 3 # keep words longer than this
c_MAX_WORD_LEN = 15 # but under this length

c_MIN_WC_CUTOFF = 10 # don't keep words that are too specific (only appearing a handful of posts)
c_MAX_WC_CUTOFF = 100 # don't keep non-specific words (that appear frequently everywhere)

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
        words = [word.lower().strip(punctuation) for word in comment.split()]
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

def get_top_feature_items(M, items_per_feature=10):
    top_items = [ ]
    feature_count, item_count = M.shape
    for feature_id in range(feature_count):
        weighted_items = [(item_id, M[feature_id, item_id]) for item_id in range(item_count)]
        weighted_items = sorted(weighted_items, key=lambda l:l[1])
        top_items.append(weighted_items[-items_per_feature:])
    return top_items

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
    
    print "factorized into:", \
          "\nbasis (posts x topics)", basis.shape, \
          "\ncoef (topics x words)", coef.shape
    for top_words, top_posts in zip(get_top_feature_items(coef), get_top_feature_items(basis.transpose())):
        print "\n~~~\ntop words:", " ".join([vocab[word_id][0] for word_id, weight in top_words]), \
              "\ntop posts:", "\n".join([post_word_bags[post_id][0] for post_id, weight in top_posts]), "\n~~~"
    
