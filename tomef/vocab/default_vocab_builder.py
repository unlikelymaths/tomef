#!/usr/bin/env python
# coding: utf-8

# # Vocab Builder
# <div style="position: absolute; right:0;top:0"><a href="./vocab.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# This module provides the `count_tokens()` and the `filter_tokens()` functions.
# 
# ---
# ## Setup and Settings
# ---

# In[1]:


from __init__ import init_vars
init_vars(vars(), ('info', {}), ('runvars', {}))

import random
from operator import attrgetter
from nltk.corpus import stopwords
import nltk
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
            
import data
import config
from base import nbprint
from util import ProgressIterator
from widgetbase import nbbox

from tokenizer.common import split_tokens

from vocab.widgets import vocab_picker
from vocab.vocab_util import VocabItem,VocabBuilder

if RUN_SCRIPT: vocab_picker(info)


# ---
# ## Vocab Builder
# ---

# In[8]:


default_options = {
    'min_docs': False,
    'max_docs': False,
    'min_count': False,
    'min_word_length': False,
    'max_word_length': False,
    'stopwords': False,
    'max_tokens': False,
}
def get_option(info, option_key):
    return info['vocab_info'].get(option_key, default_options[option_key])
def to_abs(count, num_docs):
    if count <= 0:
        return 0
    elif count < 1:
        return int(count * num_docs)
    return count


# ### `def count_tokens()`  
# Iterates over all tokens and accumulates counts in `rawcounts` dict.

# In[9]:


def count_tokens(info, runvars):
    rawcounts = {} 
    num_docs = 0
    with data.tokenized_document_reader(info) as documents:   
        for document in ProgressIterator(documents, 'Counting Tokens'):
            num_docs += 1
            tokens = split_tokens(document['tokens'])
            for token in tokens:
                try:
                    rawcounts[token].increase_total()
                except KeyError:
                    rawcounts[token] = VocabItem(token, total=1)
            for token in set(tokens):
                rawcounts[token].increase_document() 
    runvars['rawcounts'] = rawcounts
    runvars['num_docs'] = num_docs
if RUN_SCRIPT:
    nbbox()
    count_tokens(info, runvars)


# ### `def sort_counts()`  
# Turn `rawcounts` dict into list and sort tokens by number of total occurences.

# In[10]:


def sort_counts(info, runvars):
    runvars['counts'] = sorted(runvars['rawcounts'].values(), 
        key=attrgetter('total'),
        reverse=True)
if RUN_SCRIPT:
    sort_counts(info, runvars)


# Show the tokens with the highest total counts and some random ones.

# In[11]:


if RUN_SCRIPT:
    nbbox()
    num_tokens = 15
    format_str = '| {} | {} | {} |'
    split_line = [VocabItem('Random Tokens:','-','-')]
    
    nbprint(format_str.format('Token', 'Total', 'Documents'), prefix=False)
    nbprint('|---|---|---|', prefix=False)
    first_list = runvars['counts'][:num_tokens]
    random_list = random.sample(runvars['counts'], num_tokens)
    for vocab_item in first_list + split_line + random_list:
        nbprint(format_str.format(vocab_item.token, vocab_item.total, vocab_item.document), prefix=False)


# ---
# ## Filter Tokens
# ---

# ### `def filter_min_docs()`
# Remove tokens occuring in less than `min_docs` documents.

# In[12]:


def filter_min_docs(info, runvars):
    min_docs = get_option(info, 'min_docs')
    if min_docs:
        min_docs = to_abs(min_docs, runvars['num_docs'])
        old_length = len(runvars['counts'])
        runvars['counts'][:] = [vocab_item for vocab_item in runvars['counts']
                                if vocab_item.document >= min_docs]
        nbprint('Removed {} tokens occuring in less than {} documents'
              .format(old_length - len( runvars['counts']), min_docs))
if RUN_SCRIPT:
    nbbox(mini = True)
    filter_min_docs(info, runvars)


# ### `def filter_max_docs()`
# Remove tokens occuring in more than `max_docs` documents.

# In[13]:


def filter_max_docs(info, runvars):
    max_docs = get_option(info, 'max_docs')
    if max_docs:
        max_docs = to_abs(max_docs, runvars['num_docs'])
        old_length = len(runvars['counts'])
        runvars['counts'][:] = [vocab_item for vocab_item in runvars['counts']
                                if vocab_item.document <= max_docs]
        nbprint('Removed {} tokens occuring in more than {} documents'
              .format(old_length - len( runvars['counts']), max_docs))
if RUN_SCRIPT:
    nbbox(mini = True)
    filter_max_docs(info, runvars)


# ### `def filter_min_count()`
# Remove tokens occuring less than `min_count` times in total.

# In[14]:


def filter_min_count(info, runvars):
    min_count = get_option(info, 'min_count')
    if min_count:
        old_length = len(runvars['counts'])
        runvars['counts'][:] = [vocab_item for vocab_item in runvars['counts']
                                if vocab_item.total >= min_count]
        nbprint('Removed {} tokens occuring less than {} times in total.'
              .format(old_length - len( runvars['counts']), min_count))
if RUN_SCRIPT:
    nbbox(mini = True)
    filter_min_count(info, runvars)


# ### `def filter_min_word_length()`
# Remove tokens of length less than `min_word_length`.

# In[10]:


def filter_min_word_length(info, runvars):
    min_word_length = get_option(info, 'min_word_length')
    if min_word_length:
        old_length = len(runvars['counts'])
        runvars['counts'][:] = [vocab_item for vocab_item in runvars['counts']
                                if len(vocab_item.token) >= min_word_length]
        nbprint('Removed {} tokens with length less than {}'
              .format(old_length - len( runvars['counts']), min_word_length))
if RUN_SCRIPT:
    nbbox(mini = True)
    filter_min_word_length(info, runvars)


# ### `def filter_max_word_length()`
# Remove tokens of length greater than `max_word_length`.

# In[11]:


def filter_max_word_length(info, runvars):
    max_word_length = get_option(info, 'max_word_length')
    if max_word_length:
        old_length = len(runvars['counts'])
        runvars['counts'][:] = [vocab_item for vocab_item in runvars['counts']
                                if len(vocab_item.token) <= max_word_length]
        nbprint('Removed {} tokens with length greater than {}'
              .format(old_length - len( runvars['counts']), max_word_length))
if RUN_SCRIPT:
    nbbox(mini = True)
    filter_max_word_length(info, runvars)


# ### `def filter_stopwords()`
# Remove tokens that are in the nltk stopword corpus `stopwords`.

# In[12]:


def filter_stopwords(info, runvars):
    stopwords_corpus_name = get_option(info, 'stopwords')
    if stopwords_corpus_name:
        stopword_corpus = set(stopwords.words(stopwords_corpus_name))
        old_length = len(runvars['counts'])
        runvars['counts'][:] = [vocab_item for vocab_item in runvars['counts']
                                if vocab_item.token not in stopword_corpus]
        nbprint('Removed {} tokens in the {} stopword corpus'
              .format(old_length - len( runvars['counts']), stopwords_corpus_name))
if RUN_SCRIPT:
    nbbox(mini = True)
    filter_stopwords(info, runvars)


# ### `def filter_total_size()`
# Remove tokens until the vocabulary is shorter than `max_tokens`

# In[ ]:


def filter_total_size(info, runvars):
    max_tokens = get_option(info, 'max_tokens')
    if max_tokens:
        old_length = len(runvars['counts'])
        runvars['counts'][:] = runvars['counts'][:max_tokens]
        nbprint('Removed {} tokens to limit vocabulary size to {}'
              .format(old_length - len( runvars['counts']), max_tokens))
if RUN_SCRIPT:
    nbbox(mini = True)
    filter_stopwords(info, runvars)


# ### `def print_size()`
# Add an `id` to each token in the final vocabulary

# In[13]:


def print_size(info, runvars):
    nbprint('{} tokens in vocabulary.'
          .format(len(runvars['counts'])))
if RUN_SCRIPT:
    nbbox(mini = True)
    print_size(info, runvars)


# ---
# ## Build complete vocab functions
# ---

# In[14]:


class DefaultVocabBuilder(VocabBuilder):
    def build_vocab(self):
        runvars = {}
        count_tokens(self.info, runvars)
        sort_counts(self.info, runvars)
        filter_min_docs(self.info, runvars)
        filter_max_docs(self.info, runvars)
        filter_min_count(self.info, runvars)
        filter_min_word_length(self.info, runvars)
        filter_max_word_length(self.info, runvars)
        filter_stopwords(self.info, runvars)
        filter_total_size(self.info, runvars)
        print_size(self.info, runvars)
        self.counts = runvars['counts']

