#!/usr/bin/env python
# coding: utf-8

# # Vocab Builder
# <div style="position: absolute; right:0;top:0"><a href="./vocab.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# This module provides the `DefaultVocabBuilder` class that transforms the `tokens` of all documents into a `vocab`.
# First it counts all occurences of tokens in the dataset and the number of documents they appear in (`count_tokens()`).
# Subsequently, it executes various functions that are controlled by the `vocab_info` settings.
# You can chose dataset, token version and vector version to see the effect of various settings.
# 
# ---
# ## Setup and Settings
# ---

# In[ ]:


from __init__ import init_vars
init_vars(vars(), ('info', {}))

from operator import attrgetter
            
from base import config, data
from base.util import add_method
from interface import nbprint, nbbox, ProgressIterator

from tokenizer.common import split_tokens

from vocab.widgets import vocab_picker, show_tokens
from vocab.util import VocabItem,VocabBuilder
from vocab.stopwords import nltk_stopwords

if RUN_SCRIPT: vocab_picker(info)


# ---
# ## Vocab Builder
# ---
# 
# The following functions consitute the `DefaultVocabBuilder` class that produces a vocabulary by counting all tokens in a dataset and reducing the set of tokens according to various filters.

# In[ ]:


class DefaultVocabBuilder(VocabBuilder):
    
    def __init__(self, info):
        super().__init__(info)
        vocab_info = info.get('vocab_info', {})
        
        self.min_docs = vocab_info.get('min_docs', False)
        self.max_docs = vocab_info.get('max_docs', False)
        self.min_count = vocab_info.get('min_count', False)
        self.max_count = vocab_info.get('max_count', False)
        self.min_word_length = vocab_info.get('min_word_length', False)
        self.max_word_length = vocab_info.get('max_word_length', False)
        self.stopwords = vocab_info.get('stopwords', False)
        self.max_tokens = vocab_info.get('max_tokens', False)

        #self.urls = token_info.get('urls', 'skip')
        #try:
        #    self.urls_idx = URLS_OPTIONS.index(self.urls)
        #except ValueError:
        #    raise config.ConfigException(('Invalid DefaultTokenizer configuration option urls "{}". '
        #                                  'Valid options are "{}".').format(self.urls, '", "'.join(URLS_OPTIONS)))
        
if RUN_SCRIPT:
    default_vocab_builder = DefaultVocabBuilder(info)


# ### Relative to absolute counts
# 
# As some settings can be given in relative terms (e.g. `min_docs = 0.01` to only allow tokens that appear in at least 1% of the documents) this method transforms any number `<1` to an absolute count value.

# In[ ]:


@add_method(DefaultVocabBuilder)
def to_abs(self, count):
    if count <= 0:
        return 0
    elif count < 1:
        return int(count * self.num_docs)
    return count


# ---
# ## Count tokens
# ---

# ### `def count_tokens()`  
# Iterates over all tokens and accumulates counts in `rawcounts` dict.

# In[ ]:


@add_method(DefaultVocabBuilder)
def count_tokens(self):
    self.rawcounts = {} 
    self.num_docs = 0
    with data.tokenized_document_reader(self.info) as documents:   
        for document in ProgressIterator(documents, 'Counting Tokens'):
            self.num_docs += 1
            tokens = split_tokens(document['tokens'])
            for token in tokens:
                try:
                    self.rawcounts[token].increase_total()
                except KeyError:
                    self.rawcounts[token] = VocabItem(token, total=1)
            for token in set(tokens):
                self.rawcounts[token].increase_document() 
    self.num_tokens = len(self.rawcounts)
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.count_tokens()


# ### `def sort_counts()`  
# Turn `rawcounts` dict into list and sort tokens by number of total occurences.

# In[ ]:


@add_method(DefaultVocabBuilder)
def sort_counts(self):
    self.counts = sorted(self.rawcounts.values(), 
        key=attrgetter('total'),
        reverse=True)
if RUN_SCRIPT:
    default_vocab_builder.sort_counts()


# Show the tokens with the highest total counts and some random ones.

# In[ ]:


if RUN_SCRIPT:
    show_tokens(default_vocab_builder.counts,10)


# ---
# ## Filter Tokens
# ---

# ### `def filter_min_docs()`
# Remove tokens occuring in less than `min_docs` documents.

# In[ ]:


@add_method(DefaultVocabBuilder)
def filter_min_docs(self):
    if self.min_docs:
        min_docs = self.to_abs(self.min_docs)
        self.counts = [vocab_item 
                       for vocab_item in self.counts
                       if vocab_item.document >= min_docs]
        num_removed = self.num_tokens - len(self.counts)
        self.num_tokens = len(self.counts)
        nbprint('Removed {} tokens occuring in less than {} documents'
              .format(num_removed, min_docs))
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.filter_min_docs()


# ### `def filter_max_docs()`
# Remove tokens occuring in more than `max_docs` documents.

# In[ ]:


@add_method(DefaultVocabBuilder)
def filter_max_docs(self):
    if self.max_docs:
        max_docs = self.to_abs(self.max_docs)
        self.counts = [vocab_item 
                       for vocab_item in self.counts
                       if vocab_item.document <= max_docs]
        num_removed = self.num_tokens - len(self.counts)
        self.num_tokens = len(self.counts)
        nbprint('Removed {} tokens occuring in more than {} documents'
              .format(num_removed, max_docs))
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.filter_max_docs()


# ### `def filter_min_count()`
# Remove tokens occuring less than `min_count` times in total.

# In[ ]:


@add_method(DefaultVocabBuilder)
def filter_min_count(self):
    if self.min_count:
        min_count = self.to_abs(self.min_count)
        self.counts = [vocab_item 
                       for vocab_item in self.counts
                       if vocab_item.total >= min_count]
        num_removed = self.num_tokens - len(self.counts)
        self.num_tokens = len(self.counts)
        nbprint('Removed {} tokens occuring less than {} times in total.'
              .format(num_removed, min_count))
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.filter_min_count()


# ### `def filter_max_count()`
# Remove tokens occuring less than `max_count` times in total.

# In[ ]:


@add_method(DefaultVocabBuilder)
def filter_max_count(self):
    if self.max_count:
        max_count = self.to_abs(self.max_count)
        self.counts = [vocab_item 
                       for vocab_item in self.counts
                       if vocab_item.total >= max_count]
        num_removed = self.num_tokens - len(self.counts)
        self.num_tokens = len(self.counts)
        nbprint('Removed {} tokens occuring more than {} times in total.'
              .format(num_removed, max_count))
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.filter_max_count()


# ### `def filter_min_word_length()`
# Remove tokens of length less than `min_word_length`.

# In[ ]:


@add_method(DefaultVocabBuilder)
def filter_min_word_length(self):
    if self.min_word_length:
        self.counts = [vocab_item
                       for vocab_item in self.counts
                       if len(vocab_item.token) >= self.min_word_length]
        num_removed = self.num_tokens - len(self.counts)
        self.num_tokens = len(self.counts)
        nbprint('Removed {} tokens with length less than {}.'
              .format(num_removed, self.min_word_length))
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.filter_min_word_length()


# ### `def filter_max_word_length()`
# Remove tokens of length greater than `max_word_length`.

# In[ ]:


@add_method(DefaultVocabBuilder)
def filter_max_word_length(self):
    if self.max_word_length:
        self.counts = [vocab_item
                       for vocab_item in self.counts
                       if len(vocab_item.token) <= self.max_word_length]
        num_removed = self.num_tokens - len(self.counts)
        self.num_tokens = len(self.counts)
        nbprint('Removed {} tokens with length greater than {}'
              .format(num_removed, self.max_word_length))
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.filter_max_word_length()


# ### `def filter_stopwords()`
# Remove tokens that are in the nltk stopword corpus `stopwords`.

# In[ ]:


@add_method(DefaultVocabBuilder)
def filter_stopwords(self):
    if self.stopwords:
        stopword_corpus = nltk_stopwords[self.stopwords]
        self.counts = [vocab_item 
                       for vocab_item in self.counts
                       if vocab_item.token not in stopword_corpus]
        num_removed = self.num_tokens - len(self.counts)
        self.num_tokens = len(self.counts)
        nbprint('Removed {} tokens in the {} stopword corpus'
              .format(num_removed, self.stopwords))
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.filter_stopwords()


# ### `def filter_total_size()`
# Remove tokens until the vocabulary is shorter than `max_tokens`

# In[ ]:


@add_method(DefaultVocabBuilder)
def filter_total_size(self):
    if self.max_tokens:
        self.counts = self.counts[:self.max_tokens]
        num_removed = self.num_tokens - len(self.counts)
        self.num_tokens = len(self.counts)
        nbprint('Removed {} tokens to limit vocabulary size to {}'
              .format(num_removed, self.max_tokens))
if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.filter_total_size()


# ---
# ## Complete function
# ---

# In[ ]:


@add_method(DefaultVocabBuilder)
def build_vocab(self):
    self.count_tokens()
    self.sort_counts()
    self.filter_min_docs()
    self.filter_max_docs()
    self.filter_min_count()
    self.filter_max_count()
    self.filter_min_word_length()
    self.filter_max_word_length()
    self.filter_stopwords()
    self.filter_total_size()


# ### Test vocab

# In[ ]:


if RUN_SCRIPT:
    with nbbox():
        default_vocab_builder.build_vocab()
    show_tokens(default_vocab_builder.counts,10)

