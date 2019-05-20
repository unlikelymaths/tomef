#!/usr/bin/env python
# coding: utf-8

# # PT Tokenizer
# <div style="position: absolute; right:0;top:0"><a href="./tokenizer.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# This is a wrapper around the Penn Treebank tokenizer provided by the NLTK.
# For more information see https://www.nltk.org/api/nltk.tokenize.html
# 
# ---
# ## Setup and Settings
# ---

# In[ ]:


from __init__ import init_vars
init_vars(vars())

import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
from nltk.tokenize import word_tokenize
    
import tokenizer.common
from tokenizer.util import TokenizerBase


# ---
# ## Build PTTokenizer class
# ---

# In[ ]:


class PTTokenizer(TokenizerBase):
    
    def tokenize(self, text, *args):
        text = text.replace(tokenizer.common.separator_token,tokenizer.common.separator_token_replacement)
        return word_tokenize(text)

