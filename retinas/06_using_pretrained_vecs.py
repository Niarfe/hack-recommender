#!/usr/bin/env python
"""
Source: Natural Language Processing in Action, Chapter 6
Section: 6.4 How to use Gensim's word2vec module
"""
from ptpython.repl import embed

import gensim
from gensim.models.keyedvectors import KeyedVectors

# Using google's pretrained word set from news articles
word_vectors = KeyedVectors.load_word2vec_format(
    'data/GoogleNews-vectors-negative300.bin.gz', binary=True
)

# Determining synonyms:
# most_similar, pass array of words as 'positive' argument
print word_vectors.most_similar(positive=['cooking', 'potatoes'], topn=5)

# Determining antonyms:
# most_similar, pass arry of words as 'negative'
print word_vectors.most_similar(negative=['fly','airplane'], topn=5)

# Find unrelated terms
# doesnt_match, pass string with words that represent opposite context
word_vectors.doesnt_match("potatoes milk cake computer")

embed(globals(), locals())