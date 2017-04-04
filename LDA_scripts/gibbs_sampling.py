#!/usr/bin/env python
# SOURCE: Data Science from Scratch

# Chap 20: pg 245 An Aside: Gibbs Sampling
# Gibbs sampling is a technique for generating samples from multidimensional
# distributions when we only know some of the conditional distributions.
#
# here y(x) = x + roll_a_die()
#
import random
from collections import defaultdict
from collections import Counter

def roll_a_die():
    """P(x) Returns the random roll of one six sided die"""
    return random.choice([1,2,3,4,5,6])

# This essentialy returns x, y
def direct_sample():
    """P(y), roll both. Returns roll of first die, plus the sum of both"""
    d1 = roll_a_die()
    d2 = roll_a_die()
    return d1, d1 + d2

def random_y_given_x(x):
    """P(y|x), Roll x first.  Y is equally likely to be x+1, x+2...x+6"""
    return x + roll_a_die()

#########################################################################
# P(x), P(x), and P(y|x) are EZ.
# What about P(x|y)?  This case is more interesting.
#########################################################################

def random_x_given_y(y):
    if y <= 7:
        # x is in range 1-6, since together both die can cover 1-7.
        return random.randrange(1, y)
    else:
        # x can't be less than (y-6), so it's max if of course, 6
        return random.randrange(y-6, 7)


#########################################################################
# Gibbs sampling works by starting with any valid value for x and y and
# alternating x, then finding (y|x), then (x|y), repeat.  Eventually
# the pair x, y will represent a sample from unconditional joint dist.
#########################################################################

def gibbs_sample(num_iters=100):
    x, y = 1, 2 # doesn't really matter
    for idx in range(num_iters):
        #print "{} : {} iter {}".format(x,y,idx)
        x = random_x_given_y(y)
        y = random_y_given_x(x)
    return x, y

# Check it against direct distributions
def compare_distributions(num_samples=1000):
    counts = defaultdict(lambda: [0,0])
    for _ in range(num_samples):
        counts[gibbs_sample()][0] += 1
        counts[direct_sample()][1] += 1
    return counts

# KEY FUNCTION 1 general sampling function, given [1,1,3] it will return probabily
# of slot 0 (1) as 1/5, 1 (1) as 1/5 and (2) as 3/5
def sample_from(weights):
    """returns i with probability weights[i]/sum(weights)"""
    total = sum(weights)
    rnd = total*random.random()
    for i, w in enumerate(weights):
        rnd -= w
        if rnd <= 0: return i

def p_topic_given_document(topic, d, alpha=0.1):
    """the fraction of words in document _d_that are assigned to _topic_ (plus some smoothing)"""
    return ((document_topic_counts[d][topic] + alpha) /(document_lengths[d] + K * alpha))

def p_word_given_topic(word, topic, beta=0.1):
    """the fraction of words assigned to _topic_that equal _word_ (plus some smoothing)"""
    return ((topic_word_counts[topic][word] + beta) /(topic_counts[topic] + W * beta))

# KEY FUNCTION 2 calculate the probabiilty of finding a word in a topic times prob of finding topic in document
def topic_weight(d, word, k):
    """given a document and a word in that document,return the weight for the kth topic"""
    return p_word_given_topic(word, k) * p_topic_given_document(k, d)

def choose_new_topic(d, word):
    return sample_from([topic_weight(d, word, k) for k in range(K)])

if __name__ == "__main__":
    print gibbs_sample()

    print compare_distributions()

    # sample documents for our test
    documents = [
        ["Hadoop", "Big Data", "HBase", "Java", "Spark", "Storm", "Cassandra"],
        ["NoSQL", "MongoDB", "Cassandra", "HBase", "Postgres"],
        ["Python", "scikit-learn", "scipy", "numpy", "statsmodels", "pandas"],
        ["R", "Python", "statistics", "regression", "probability"],
        ["machine learning", "regression", "decision trees", "libsvm"],
        ["Python", "R", "Java", "C++", "Haskell", "programming languages"],
        ["statistics", "probability", "mathematics", "theory"],
        ["machine learning", "scikit-learn", "Mahout", "neural networks"],
        ["neural networks", "deep learning", "Big Data", "artificial intelligence"],
        ["Hadoop", "Java", "MapReduce", "Big Data"],
        ["statistics", "R", "statsmodels"],
        ["C++", "deep learning", "artificial intelligence", "probability"],
        ["pandas", "R", "Python"],
        ["databases", "HBase", "Postgres", "MySQL", "MongoDB"],
        ["libsvm", "regression", "support vector machines"]
    ]
    
    # a list of Counters, one for each document
    document_topic_counts = [Counter() for _ in documents]
    
    K = 4
    # a list of Counters, one for each topic
    topic_word_counts = [Counter() for _ in range(K)]
    
    # a list of numbers, one for each topic
    topic_counts = [0 for _ in range(K)]
    
    # a list of numbers, one for each document
    document_lengths = map(len, documents)
    
    distinct_words = set(word for document in documents for word in document)
    W = len(distinct_words)
    
    D = len(documents)
    random.seed(0)
    document_topics = [[random.randrange(K) for word in document] for document in documents]

    for d in range(D):
        for word, topic in zip(documents[d], document_topics[d]):
            document_topic_counts[d][topic] += 1
            topic_word_counts[topic][word] += 1
            topic_counts[topic] += 1
    
    
    for iter in range(1000):
        for d in range(D):
            for i, (word, topic) in enumerate(zip(documents[d], document_topics[d])):
               # remove this word / topic from the counts
               # so that it doesn't influence the weights
               document_topic_counts[d][topic] -= 1
               topic_word_counts[topic][word] -= 1
               topic_counts[topic] -= 1
               document_lengths[d] -= 1
               
               # choose a new topic based on the weights
               new_topic = choose_new_topic(d, word)
               document_topics[d][i] = new_topic
               
               # and now add it back to the counts
               document_topic_counts[d][new_topic] += 1
               topic_word_counts[new_topic][word] += 1
               topic_counts[new_topic] += 1
               document_lengths[d] += 1
    
    for k, word_counts in enumerate(topic_word_counts):
        for word, count in word_counts.most_common():
            if count > 0: print k, word, count
    
    
