#!/usr/bin/env python
# coding: utf-8

# # Word2vecTokenizer
# <div style="position: absolute; right:0;top:0"><a href="./tokenizer.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# This module provides the `W2VTokenizer` class that transforms the `text` of a document into `tokens`.
# It keeps only those tokens that appear in the vocabulary of the corresponding embedding model,
# but tries to combine tokens into phrases if they appear in the model.
# 
# ---
# ## Setup and Settings
# ---

# In[124]:


from __init__ import init_vars
init_vars(vars(), ('info', {}), ('runvars', {}))

import re
    
import data
import config
from base import nbprint
from widgetbase import nbbox
from util import ProgressIterator, add_method

from embedding.main import get_model

import tokenizer.common
from tokenizer.token_util import TokenizerBase
from tokenizer.default_tokenizer import DefaultTokenizer
from tokenizer.widgets import token_picker, run_and_compare, show_comparison

if RUN_SCRIPT: token_picker(info, runvars, 'C')


# ---
# ## Tokenize Document
# ---
# The following functions consitute the `W2VTokenizer` class that transforms the raw text of a document into tokens.

# In[170]:


class W2VTokenizer(TokenizerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.embedding_model = get_model(self.info)
        self.filter = self.embedding_model.filter.filter

if RUN_SCRIPT:
    nbbox()
    w2v_tokenizer = W2VTokenizer(info)
    w2v_tokenizer.text = runvars['document']['text']


# ### Prepare Text
# 
# This step lowercases all characters and replaces the following:
# - `separator_token` by `separator_token_replacement`
# - all whitespaces by a single whitespace
# - `#` by nothing

# In[171]:


_re_whitespace = re.compile('[\s]+', re.UNICODE)
_re_url = re.compile('(http://[^\s]+)|(https://[^\s]+)|(www\.[^\s]+)')

@add_method(W2VTokenizer)
def prepare(self):
    self.text = self.text.lower()
    self.text = self.text.replace(tokenizer.common.separator_token,tokenizer.common.separator_token_replacement)
    self.text = self.text.replace('#', '')
    self.text, count = _re_url.subn(' ', self.text)
    self.text, count = _re_whitespace.subn(' ', self.text)
    
if RUN_SCRIPT:
    run_and_compare(w2v_tokenizer, w2v_tokenizer.prepare, 'text')


# ### Replace numbers
# 
# All numbers are replaced by `#`. This include all numbers in the Unicode 'Number, Decimal Digit' category.

# In[172]:


_re_decimal = re.compile('\d', re.UNICODE)

@add_method(W2VTokenizer)
def replace_numbers(self):
    self.text, count = _re_decimal.subn('#', self.text)
    
if RUN_SCRIPT:
    run_and_compare(w2v_tokenizer, w2v_tokenizer.replace_numbers, 'text')


# ### Split at breaking characters
# 
# This step splits the string into substrings $s_i$ at all sequences of non alphanumeric characters (`\w`), whitespace (`\s`), or apostrophes (`\'`). Later, the algorithm will only try to combine tokens from each $s_i$ separately into phrases, but not tokens from different substrings.

# In[173]:


_re_breaking = re.compile('[^\w\s\'\’#]+', re.UNICODE)

@add_method(W2VTokenizer)
def split_text(self):
    self.subtexts = _re_breaking.split(self.text)
    
if RUN_SCRIPT:
    run_and_compare(w2v_tokenizer, w2v_tokenizer.split_text, 'text', 'subtexts')


# ### Split at nonbreaking characters

# In[174]:


@add_method(W2VTokenizer)
def split_subtexts(self):
    self.tokenlists = [subtext.split()
                      for subtext in self.subtexts
                      if len(subtext) > 0]
    
if RUN_SCRIPT:
    run_and_compare(w2v_tokenizer, w2v_tokenizer.split_subtexts, 'subtexts', 'tokenlists')


# ### Filter

# In[175]:


@add_method(W2VTokenizer)
def build_tokens(self):
    self.tokens = []
    for tokenlist in self.tokenlists:
        self.tokens = self.tokens + self.filter(tokenlist)
    
if RUN_SCRIPT:
    run_and_compare(w2v_tokenizer, w2v_tokenizer.build_tokens, 'tokenlists', 'tokens')


# ---
# ## Complete function
# ---

# In[177]:


@add_method(W2VTokenizer)
def tokenize(self, text, *args):
    self.text = text
    self.prepare()
    self.replace_numbers()
    self.split_text()
    self.split_subtexts()
    self.build_tokens()
    return self.tokens


# ## Test tokenizer

# In[178]:


if RUN_SCRIPT:
    w2v_tokenizer.tokenize(runvars['document']['text'])
    show_comparison(runvars['document']['text'], w2v_tokenizer.tokens, 'Text', 'Tokens')

