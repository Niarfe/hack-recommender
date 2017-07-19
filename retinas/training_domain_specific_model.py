#!/usr/bin/env python
"""
Source: Natural Language Processing in Action, Chapter 6
Section: 6.5.2 Training domain specific word2vec model
"""
from ptpython.repl import embed
import re
import sys


data_source = 'fairy_tales_every_child_should_know_pg14916'

num_features   = 300  # number of vector elements in represantation
min_word_count = 3    # Min number of word count to be considered
num_workers    = 2    # Number of threads to run in parallel
window_size    = 6    # Context window size
subsampling    = 1e-3 # subsampling rate for frequent terms

#open input file and tokenize
tokens = []
with open("data/{}.txt".format(data_source), 'r') as source:
    for line in source:
        line = re.sub(r'\W', ' ', line) 
        line_tokens = line.split( )
        line_tokens = [token.strip().lower() for token in line_tokens]
        tokens.append(line_tokens)

model = word2vec.Word2Vec(
    tokens,
    workers=num_workers,
    size=num_features,
    window=window_size,
    sample=subsampling
)

# freeze training model and only store weights of hidden neurons
# this saves disk space.  We lose the neuron output weights tho.
model.init_sims(replace=True)

model_name = "{}_model".format(data_source)
model.save(model_name)

from gensim.models import word2vec
model = word2vec.Word2Vec.load(model_name)

# It works!!
#print model.most_similar(positive=['king','prince','aladdin'], topn=20)
embed(globals(), locals())