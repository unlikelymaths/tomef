#!/usr/bin/env python
# coding: utf-8

# # DefaultTokenizer
# <div style="position: absolute; right:0;top:0"><a href="./tokenizer.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# This module provides the `DefaultTokenizer` class that transforms the `text` of a document into `tokens`.
# It executes various functions that are controlled by the `token_info` settings.
# You can chose dataset, token version and a document to see the effect of various settings.
# The array `fixed_tokens` is used for all tokens that are no further processed.
# 
# ---
# ## Setup and Settings
# ---

# In[1]:


from __init__ import init_vars
init_vars(vars(), ('info', {}), ('runvars', {}))

import re
import emoji
    
import data
import config
from base import nbprint
from util import ProgressIterator, add_method

import tokenizer.common
import tokenizer.emoticons
from tokenizer.token_util import iterate_tokens, TokenizerBase
from tokenizer.widgets import token_picker, run_and_compare, show_comparison

if RUN_SCRIPT: token_picker(info, runvars)


# ---
# ## Tokenize Document
# ---
# The following functions consitute the `DefaultTokenizer` class that transforms the raw text of a document into tokens.

# In[2]:


URLS_OPTIONS = ['skip', 'keep', 'domain', 'replace', 'drop']
EMOTES_OPTIONS = ['skip', 'keep', 'replace', 'drop']
ALNUM_OPTIONS = ['skip', 'weak', 'apostrophe', 'strict']
NUMBERS_OPTIONS = ['skip', 'decimal-on-one', 'all-on-one', 'drop']

class DefaultTokenizer(TokenizerBase):
    
    def __init__(self, info):
        super().__init__(info)
        token_info = info.get('token_info', {})
        
        self.urls = token_info.get('urls', 'skip')
        try:
            self.urls_idx = URLS_OPTIONS.index(self.urls)
        except ValueError:
            raise config.ConfigException(('Invalid DefaultTokenizer configuration option urls "{}". '
                                          'Valid options are "{}".').format(self.urls, '", "'.join(URLS_OPTIONS)))
        
        self.ascii_emotes   = token_info.get('ascii_emotes', 'skip')
        try:
            self.ascii_emotes_idx = EMOTES_OPTIONS.index(self.ascii_emotes)
        except ValueError:
            raise config.ConfigException(('Invalid DefaultTokenizer configuration option ascii_emotes "{}". '
                                          'Valid options are "{}".').format(self.ascii_emotes, '", "'.join(EMOTES_OPTIONS)))
        
        self.unicode_emotes = token_info.get('unicode_emotes', 'skip')
        try:
            self.unicode_emotes_idx = EMOTES_OPTIONS.index(self.unicode_emotes)
        except ValueError:
            raise config.ConfigException(('Invalid DefaultTokenizer configuration option unicode_emotes "{}". '
                                          'Valid options are "{}".').format(self.unicode_emotes, '", "'.join(EMOTES_OPTIONS)))
        
        self.alnum_only     = token_info.get('alnum_only', True)
        try:
            self.alnum_only_idx = ALNUM_OPTIONS.index(self.alnum_only)
        except ValueError:
            raise config.ConfigException(('Invalid DefaultTokenizer configuration option alnum_only "{}". '
                                          'Valid options are "{}".').format(self.alnum_only, '", "'.join(ALNUM_OPTIONS)))
        
        self.numbers        = token_info.get('numbers', 'skip')
        try:
            self.numbers_idx = NUMBERS_OPTIONS.index(self.numbers)
        except ValueError:
            raise config.ConfigException(('Invalid DefaultTokenizer configuration option numbers "{}". '
                                          'Valid options are "{}".').format(self.numbers, '", "'.join(NUMBERS_OPTIONS)))
        
        
        self.lowercase      = token_info.get('lowercase', True)
        self.numbers_split  = token_info.get('numbers_split', False)
        self.ascii_only     = token_info.get('ascii_only', True)
        
if RUN_SCRIPT:
    default_tokenizer = DefaultTokenizer(info)


# ### Prepare
# 
# Splits the text at whitespace and initializes an empty list of fixed tokens. The `separator_token` is replaced with the `separator_token_replacement`, so that it can be used for saving the tokens as a string, i.e.
# ```
# This:is:a:token:list
# ```

# In[3]:


@add_method(DefaultTokenizer)
def init_tokenization(self, text):
    self.fixed_tokens = []
    self.text = text.replace(tokenizer.common.separator_token,tokenizer.common.separator_token_replacement)
    self.tokens = text.split()

if RUN_SCRIPT:
    default_tokenizer.init_tokenization(runvars['document']['text'])
    show_comparison(default_tokenizer.text, default_tokenizer.tokens, 'Text', 'Tokens')


# ### URLs
# Supports the following options for `urls`:
# - `skip`: this step will be skipped
# - `keep`: keeps every URL as it is, no further processing
# - `domain`: replaces every URL by its top and second level domain
# - `drop`: completely removes every URL from the text
# - `replace`: replaces every URL with the URL Token

# In[4]:


def _process_urls_keep_fct(url_str):
    return url_str
def _process_urls_domain_fct(url_str):
    for prefix in ['http://', 'https://']:
        url_str = url_str.replace(prefix,'')
    slash_index = url_str.find('/')
    if slash_index > 0:
        url_str = url_str[:slash_index]
    if url_str.count('.') > 1:
        url_str = url_str[url_str.rfind('.',0,url_str.rfind('.'))+1:]
    return url_str
def _process_urls_replace_fct(url_str):
    return tokenizer.common.url_token
def _process_urls_drop_fct(url_str):
    pass
_process_urls_fct_selector = [None,
                              _process_urls_keep_fct, 
                              _process_urls_domain_fct, 
                              _process_urls_replace_fct, 
                              _process_urls_drop_fct]
    
@add_method(DefaultTokenizer)
def process_urls_token(self, token):
    if (token.startswith("http://") or
        token.startswith("https://") or
        token.startswith("www.")):
        url_str = self._process_urls_fct(token)
        if url_str is not None:
            self.fixed_tokens.append(url_str)
        return None
    return token

@add_method(DefaultTokenizer)
def process_urls(self):
    self._process_urls_fct = _process_urls_fct_selector[self.urls_idx]
    if self._process_urls_fct is not None:
        iterate_tokens(self.tokens, self.process_urls_token)         
    
if RUN_SCRIPT:
    run_and_compare(default_tokenizer, default_tokenizer.process_urls, 'tokens', 'fixed_tokens', 'Input', 'Fixed Tokens')


# ### ASCII Emoticons
# 
# Supports the following options for `ascii_emotes`:
# - `skip`: this step will be skipped
# - `keep`: keeps every ASCII emoticon as it is, no further processing
# - `drop`: ompletely removes every ASCII emoticon from the text
# - `replace`: replaces with the emote token

# In[5]:


def _process_emotes_keep_fct(emoticon):
    return emoticon
def _process_emotes_replace_fct(emoticon):
    return tokenizer.common.emote_token
def _process_emotes_drop_fct(emoticon):
    pass
_process_emotes_fct_selector = [None,
                                _process_emotes_keep_fct,
                                _process_emotes_replace_fct,
                                _process_emotes_drop_fct]

@add_method(DefaultTokenizer)
def process_ascii_emotes_token(self, token):
    for e, remainder in tokenizer.emoticons.western_dict.items():
        parts = token.split(e, 1)
        if len(parts) == 1:
            continue
        else:
            # Test if it is preceded by alphanumeric characters
            pre = parts[0][-1:]
            if pre.isalnum():
                continue
                
            for r in remainder:
                if not parts[1].startswith(r):
                    continue
                post = parts[1][len(r):]
                
                # Test if it is followed by alphanumeric characters
                if post[:1].isalnum():
                    continue
                
                emoticon = self._process_ascii_emotes_fct(e + r)
                if emoticon is not None:
                    self.fixed_tokens.append(emoticon)
                remaining = []
                if len(pre) >= 2:
                    remaining += self.process_ascii_emotes_token(pre)
                else:
                    remaining += pre
                if len(post) >= 2:
                    remaining += self.process_ascii_emotes_token(post)
                else:
                    remaining += post
                return [s for s in parts if len(s) > 0]
    return token

@add_method(DefaultTokenizer)
def process_ascii_emotes(self):
    self._process_ascii_emotes_fct = _process_emotes_fct_selector[self.ascii_emotes_idx]
    if self._process_ascii_emotes_fct is not None:
        iterate_tokens(self.tokens, self.process_ascii_emotes_token)    
            
if RUN_SCRIPT:
    run_and_compare(default_tokenizer, default_tokenizer.process_ascii_emotes, 'tokens', 'fixed_tokens', 'Input', 'Fixed Tokens')


# ### Unicode Emoticons
# 
# Supports the following options for `unicode_emotes`:
# - `skip`: this step will be skipped
# - `keep`: keeps every ASCII emoticon as it is, no further processing
# - `drop`: ompletely removes every ASCII emoticon from the text
# - `replace`: replaces with the emote token

# In[6]:


@add_method(DefaultTokenizer)
def process_unicode_emotes_token(self, token):
    tokens = []
    new_token = ''
    for c in token:
        if c in emoji.UNICODE_EMOJI:
            emoticon = self._process_ascii_emotes_fct(c)
            if emoticon is not None:
                self.fixed_tokens.append(emoticon)
            if len(new_token) > 0:
                tokens.append(new_token)
                new_token = ''
        else:
            new_token += c
    if len(tokens) == 0:
        return new_token
    return tokens + [new_token]
    
@add_method(DefaultTokenizer)
def process_unicode_emoticons(self):
    self._process_ascii_emotes_fct = _process_emotes_fct_selector[self.ascii_emotes_idx]
    if self._process_ascii_emotes_fct is not None:
        iterate_tokens(self.tokens, self.process_unicode_emotes_token) 
        
if RUN_SCRIPT:
    run_and_compare(default_tokenizer, default_tokenizer.process_unicode_emoticons, 'tokens', 'fixed_tokens', 'Input', 'Fixed Tokens')


# ### Split Numbers
# 
# This step splits words that consist of letters, special characters and numbers into distinct words.
# `,` and `.` are allowed to occur within numbers and do not lead to splitting up the string.

# In[7]:


dezimal_re = re.compile('([0-9]+(?:[,.]+[0-9,.]+)*)')

@add_method(DefaultTokenizer)
def split_numbers_token(self, token):
    return [s for s in dezimal_re.split(token) if len(s) > 0]

@add_method(DefaultTokenizer)
def split_numbers(self):
    if self.numbers_split:
        iterate_tokens(self.tokens, self.split_numbers_token) 
        
if RUN_SCRIPT:
    run_and_compare(default_tokenizer, default_tokenizer.split_numbers, 'tokens')


# ### Lowercase
# 
# All letters are lowercased.

# In[8]:


@add_method(DefaultTokenizer)
def process_lowercase_token(self, token):
    return token.lower()

@add_method(DefaultTokenizer)
def process_lowercase(self):
    if self.lowercase:
        iterate_tokens(self.tokens, self.process_lowercase_token)
        
if RUN_SCRIPT:
    run_and_compare(default_tokenizer, default_tokenizer.process_lowercase, 'tokens')


# ### Remove non-ascii characters

# In[9]:


@add_method(DefaultTokenizer)
def remove_nonascii_token(self, token):
    return token.encode('ascii',errors='ignore').decode()

@add_method(DefaultTokenizer)
def remove_nonascii(self):
    if self.ascii_only:
        iterate_tokens(self.tokens, self.remove_nonascii_token)
        
if RUN_SCRIPT:
    run_and_compare(default_tokenizer, default_tokenizer.remove_nonascii, 'tokens')


# ### Remove Non-alphanumeric characters
# 
# Removes non alphanumeric characters. Possible options for `alnum_only` are:
# - `skip`: Retains all characters
# - `weak`: Retains `'`, `@`, `#`, and `_`
# - `apostrophe`: Retains `'`
# - `strict`: Removed all characters except `a-z`, `A-Z` and `0-9`

# In[10]:


_remove_nonalnum_re_selector = [
    None,
    re.compile('[^a-zA-Z0-9\'@#_]'),
    re.compile('[^a-zA-Z0-9\']'),
    re.compile('[^a-zA-Z0-9]')]

@add_method(DefaultTokenizer)
def remove_nonalnum_token(self, token):
    return [s 
            for s in _remove_nonalnum_re_selector[self.alnum_only_idx].split(token) 
            if len(s) > 0]

@add_method(DefaultTokenizer)
def remove_nonalnum(self):
    if self.alnum_only:
        iterate_tokens(self.tokens, self.remove_nonalnum_token)
    
if RUN_SCRIPT:
    run_and_compare(default_tokenizer, default_tokenizer.remove_nonalnum, 'tokens')


# ### Replace Numbers
# 
# Replace numbers by number tokens. Supports the following options for `numbers`:
# - `skip`: 
# Either replace each single digit by a token or replace the whole number (possibly including `.` and `,`) by a single token.

# In[11]:


_re_numbers_decimal  = re.compile("[0-9]")
_re_numbers_complete = re.compile("([0-9][0-9\.,]*)|([0-9\.,]*[0-9])")
_replace_numbers_re_selector = [None,
    _re_numbers_decimal,
    _re_numbers_complete,
    _re_numbers_complete]
_replace_numbers_sub_selector = [None,
    tokenizer.common.number_token,
    tokenizer.common.number_token,
    '']

@add_method(DefaultTokenizer)
def replace_numbers_token(self, token):
    token, count = self._replace_numbers_re.subn(self._replace_numbers_sub, token)
    if count > 0:
        self.fixed_tokens.append(token)
        return None
    return token

@add_method(DefaultTokenizer)
def replace_numbers(self):
    if self.numbers_idx > 0:
        self._replace_numbers_re= _replace_numbers_re_selector[self.numbers_idx]
        self._replace_numbers_sub = _replace_numbers_sub_selector[self.numbers_idx]
        iterate_tokens(self.tokens, self.replace_numbers_token)
        
if RUN_SCRIPT: 
    run_and_compare(default_tokenizer, default_tokenizer.replace_numbers, 'tokens', 'fixed_tokens')


# ---
# ## Complete function
# ---

# In[12]:


@add_method(DefaultTokenizer)
def tokenize(self, text, *args):
    self.init_tokenization(text)
    self.process_urls()
    self.process_ascii_emotes()
    self.process_unicode_emoticons()
    self.split_numbers()
    self.process_lowercase()
    self.remove_nonascii()
    self.remove_nonalnum()
    self.replace_numbers()
    self.tokens = self.tokens + self.fixed_tokens
    return self.tokens


# ## Test tokenizer

# In[13]:


if RUN_SCRIPT:
    default_tokenizer = DefaultTokenizer(info)
    default_tokenizer.tokenize(runvars['document']['text'])
    show_comparison(default_tokenizer.text, default_tokenizer.tokens, 'Text', 'Tokens')

