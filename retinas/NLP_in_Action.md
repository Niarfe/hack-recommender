# Natural Language Processing in Action

## Chapter 6

### Word2Vec Approaches

| **Skip-Gram**| |
|:- |:- |
| Description | **Predict context words from a given source word** |
| Usage-:     | Input: Target word | 
|             | Output: Words of context usually surrounding that word |
| Description | ANN with one hidden layer, with input size M and hidden size N. (M-N-M) |
|             | Input layer:  one-hot vector representing word to be encoded. |
|             | Hiden layer:  N neurons which will become the vector representation, (~300)      |
|             | Output layer: M neurons representing words, and values represent prob of input word near output word. (Softamax)|
| Example:    | For training on a context size of +-1, (one word behind or forward): |
|             | Convert a corpora of words into 3-grams, thus 'snails are not the fastest runners' becomes |
|             | (snails,are,not), (are,not,the),(not,the,fastest),(the,fastest,runners) |
|             | Then each center word becomes an input, and the remaining tuple becomes the training vector. |
|             | IMPORTANT: After training: |
|             |    The hidden neuron matrix, which is an m x n matrix, gives us the embeddings: |
|             |    For the nth word, embedding(n) = w(m) dot Hidden(mxn) |

| **(CBOW)**| Continuous Bag of Words |
|:- |:-|
| Description | **Predict center word from surrounding words** |
| Usage:      | Input: context words |
|             | Output: most likely center word |
| Description | Basically a flipped skip-gram model |
|             | Input vector is a binary vector representing the words of the word window |
|             | Output vector is softmax activation with the *most likely center word* |


## Using it as a demo
### Good examples
* ```word_vectors.most_similar(positive['cloud', 'internet', 'server'], topn=5)``` 
    - `servers`, `virtualized_servers`, `Amazon_EC2_cloud`
* 'cloud', 'mountain', 'rain' yeilds 'clouds', 'mountains', 'snow'
* violin, orchestra versus violin software not a good result, but violin against *two* keywords yeilds right context as in violin embedded software
* The classic example ```word_vectors.most_similar(positive=['king','woman'], negative=['man'], topn=2)
[(u'queen', 0.7118192315101624), (u'monarch', 0.6189674139022827)]```
* get array underneath by using ```word_vectors['phone']``` for example


### More good examples for demo
* I created a set of vectors from my staffing raw data after I cleaned it up....
* From taht set, look for staffing, you get some interesting results, like recruiting, contract ...
* english, yielded languges, etc...
* server -> sql, desktop, linux
* cloud -> computing, azure etc
* cloud,azure, versus running cloud,azure - aws, which yeilds microsoft, the first combo yielded saas.
* jobs -> salaries, etc
* job -> resume, etc... good stuff!
* azure, microsoft, versus azure,microsoft-aws, yields also intersting because saas moves out of the way...

