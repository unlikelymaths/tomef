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
from util import ProgressIterator

import tokenizer.common
import tokenizer.emoticons
from tokenizer.token_util import iterate_tokens, TokenizerBase
from tokenizer.widgets import token_picker, run_and_compare

if RUN_SCRIPT: token_picker(info, runvars)


# ---
# ## Tokenize Document
# ---
# The following functions consitute the `DefaultTokenizer` class that transforms the raw text of a document into tokens. The default options are:

# In[2]:


default_options = {
    'urls': 'skip',
    'ascii_emotes': 'skip',
    'unicode_emotes': 'skip',
    'numbers': 'drop',
    'lowercase': True,
    'numbers_split': False,
    'alnum_only': True,
    'ascii_only': True,
}
def get_option(token_info, option_key):
    return token_info.get(option_key, default_options[option_key])


# ### URLs
# Supports the following options for `urls`:
# - `skip`: this step will be skipped
# - `keep`: keeps every URL as it is, no further processing
# - `domain`: replaces every URL by its top and second level domain
# - `drop`: completely removes every URL from the text
# - `replace`: replaces every URL with the URL Token

# In[3]:


def url_drop_fct(runvars, url_str):
    pass
def url_domain_fct(runvars, url_str):
    for prefix in ['http://', 'https://']:
        url_str = url_str.replace(prefix,'')
    slash_index = url_str.find('/')
    if slash_index > 0:
        url_str = url_str[:slash_index]
    if url_str.count('.') > 1:
        url_str = url_str[url_str.rfind('.',0,url_str.rfind('.'))+1:]
    runvars['fixed_tokens'].append(url_str)
def url_replace_fct(runvars, url_str):
    runvars['fixed_tokens'].append(tokenizer.common.url_token) 
def url_keep_fct(runvars, url_str):
    runvars['fixed_tokens'].append(url_str) 
def url_fct_selector(option):
    if option == "drop":
        return url_drop_fct
    elif option == "domain":
        return url_domain_fct
    elif option == "replace":
        return url_replace_fct
    elif option == "keep":
        return url_keep_fct
    raise config.ConfigException('token_info setting "{}" for urls not defined.'.format(option))
    
def process_urls(info, runvars):
    option = get_option(info['token_info'],'urls')
    runvars['fixed_tokens'] = []
    if option == 'skip':
        runvars['text'] = runvars['document']['text']
    else:
        url_fct = url_fct_selector(option)
        words = runvars['document']['text'].split()
        new_words = []
        runvars['fixed_tokens'] = []
        for word in words:
            if (word.startswith("http://") or
                word.startswith("https://") or
                word.startswith("www.")):
                url_fct(runvars, word)
            else:
                new_words.append(word)
        runvars['text'] = ' '.join(new_words)
    
if RUN_SCRIPT: run_and_compare(info, runvars, process_urls, ['document','text'], 'fixed_tokens', 'Input', 'Fixed Tokens')


# ### ASCII Emoticons
# 
# Supports the following options for `ascii_emotes`:
# - `skip`: this step will be skipped
# - `keep`: keeps every ASCII emoticon as it is, no further processing
# - `drop`: ompletely removes every ASCII emoticon from the text
# - `replace`: replaces with the emote token
# 
# **TODO**: Prevent it from removing parts of words, e.g. `xp` from `experiment`

# In[4]:


def emoticon_drop_fct(runvars,emoticon,count=1):
    pass
def emoticon_keep_fct(runvars,emoticon,count=1):
    runvars['fixed_tokens'] += [emoticon,] * count
def emoticon_replace_fct(runvars,emoticon,count=1):
    runvars['fixed_tokens'] += [tokenizer.common.emote_token,] * count
def emoticon_fct_selector(option):
    if option == 'keep':
        return emoticon_keep_fct
    elif option == 'drop':
        return emoticon_drop_fct
    elif option == 'replace':
        return emoticon_replace_fct
    raise config.ConfigException('token_info setting "{}" for emoticons not defined.'.format(option))


def process_ascii_emoticons(info, runvars):
    option = get_option(info['token_info'],'ascii_emotes')
    if option != 'skip':
        emoticon_fct = emoticon_fct_selector(option)
        text = runvars['text']
        for e in tokenizer.emoticons.western:
            ecount = text.count(e)
            if ecount > 0:
                emoticon_fct(runvars,e,ecount)
                text = text.replace(e, ' ')
        runvars['text'] = text
            
if RUN_SCRIPT: run_and_compare(info, runvars, process_ascii_emoticons, 'text', 'fixed_tokens', 'Input', 'Fixed Tokens')


# ### Unicode Emoticons
# 
# Supports the following options for `unicode_emotes`:
# - `skip`: this step will be skipped
# - `keep`: keeps every ASCII emoticon as it is, no further processing
# - `drop`: ompletely removes every ASCII emoticon from the text
# - `replace`: replaces with the emote token

# In[5]:


def process_unicode_emoticons(info, runvars):
    option = get_option(info['token_info'],'unicode_emotes')
    if option != 'skip':
        emoticon_fct = emoticon_fct_selector(option)
        text = runvars['text']
        new_text = ''
        for c in text:
            if c in emoji.UNICODE_EMOJI:
                emoticon_fct(runvars,c)
                new_text += ' '
            else:
                new_text += c
        runvars['text'] = new_text
            
if RUN_SCRIPT: run_and_compare(info, runvars, process_unicode_emoticons, 'text', 'fixed_tokens', 'Input', 'Fixed Tokens')


# ### Split
# 
# The text is split into tokens. The `separator_token` is replaced with the `separator_token_replacement`, so that it can be used for saving the tokens as a string, i.e.
# ```
# This;is;a;token;list
# ```

# In[6]:


def split(info, runvars):
    text = runvars['text']
    text = text.replace(tokenizer.common.separator_token,tokenizer.common.separator_token_replacement)
    runvars['tokens'] = text.split()
if RUN_SCRIPT: run_and_compare(info, runvars, split, 'text', 'tokens')


# ### Lowercase (Optional)
# 
# All letters are lowercased.

# In[7]:


def lowercase_word(word):
    return word.lower()

def lowercase(info, runvars):
    if get_option(info['token_info'],'lowercase'):
        iterate_tokens(runvars['tokens'], lowercase_word)
        
if RUN_SCRIPT: run_and_compare(info, runvars, lowercase, 'tokens', 'tokens')


# ### Split Numbers (Optional)
# 
# This step splits words that consist of letters and numbers into distinct words.
# `ignore_in_decimal` are characters that are allowed to occur within numbers and do not lead to splitting up the string.

# In[8]:


def split_numbers_word(word):
    words = []
    current_word = word[0]
    current_word_isdecimal = current_word.isdecimal()
    ignore_in_decimal = [",","."]
    ignore_count = 0 # counts how many consecutive ignore_in_decimal characters have appeared
    for char in word[1:]:
        if char.isdecimal() != current_word_isdecimal:
            if current_word_isdecimal and char in ignore_in_decimal and ignore_count == 0:
                ignore_count += 1
                current_word += char
            else:
                if ignore_count:
                    current_word = current_word[:-ignore_count]
                    ignore_count = 0
                words.append(current_word)
                current_word = char
                current_word_isdecimal = current_word.isdecimal()
        else:
            ignore_count = 0
            current_word += char
    
    if ignore_count:
        current_word = current_word[:-ignore_count]
    words.append(current_word)
    return words

def split_numbers(info, runvars):
    if get_option(info['token_info'],'numbers_split'):
        iterate_tokens(runvars['tokens'], split_numbers_word)
        
if RUN_SCRIPT: run_and_compare(info, runvars, split_numbers, 'tokens', 'tokens')


# ### Remove Non-alphanumeric characters

# In[9]:


re_number_only_single = re.compile("^(\d+)[\.,](\d+)$")
re_word_single_apostrophe = re.compile("^[^']+'[^']{1,3}$")

def remove_nonalnum_word(word):
    if word.isalnum():
        return word
    
    if re_number_only_single.match(word):
        return word
    elif re_word_single_apostrophe.match(word):
        parts = word.split("'")
        part_left = ''.join([char for char in parts[0] if char.isalnum()])
        part_right = ''.join([char for char in parts[1] if char.isalnum()])
        return "'".join([part_left, part_right])
        
    new_word = [char for char in word if char.isalnum()]
    return ''.join(new_word)

def remove_nonalnum(info, runvars):
    if get_option(info['token_info'],'alnum_only'):
        iterate_tokens(runvars['tokens'], remove_nonalnum_word)
    
if RUN_SCRIPT: run_and_compare(info, runvars, remove_nonalnum, 'tokens', 'tokens')


# ### Remove non-ascii characters

# In[10]:


def remove_nonascii_word(word):
    return word.encode('ascii',errors='ignore').decode()

def remove_nonascii(info, runvars):
    if get_option(info['token_info'],'ascii_only'):
        iterate_tokens(runvars['tokens'], remove_nonascii_word)
        
if RUN_SCRIPT: run_and_compare(info, runvars, remove_nonascii, 'tokens', 'tokens')


# ### Replace Numbers

# In[12]:


re_number_single = re.compile("[0-9]")
def _replace_numbers(word):
    return re_number_single.sub(tokenizer.common.number_token, word)


re_number_complete = re.compile("([0-9][0-9\.,]*)|([0-9\.,]*[0-9])")
def _replace_numbers_single(word):
    return re_number_complete.sub(tokenizer.common.number_token, word)

re_number_only_single = re.compile("^(\d+)[\.,](\d+)$")
def _replace_numbers_drop(word):
    return re_number_complete.sub("", word)

replace_numbers_selector = {
    'replace': _replace_numbers,
    'replace_single': _replace_numbers_single,
    'drop': _replace_numbers_drop
}

def replace_numbers(info, runvars):
    option = get_option(info['token_info'],'numbers')
    if option == "keep":
        pass
    else:
        iterate_tokens(runvars['tokens'], replace_numbers_selector[option])
        
if RUN_SCRIPT: run_and_compare(info, runvars, replace_numbers, 'tokens', 'tokens')


# ---
# ## Build DefaultTokenizer class
# ---

# In[13]:


class DefaultTokenizer(TokenizerBase):
    
    def tokenize(self, text, *args):
        runvars = {'document': {'text': text}}
        
        process_urls(self.info, runvars)
        process_ascii_emoticons(self.info, runvars)
        process_unicode_emoticons(self.info, runvars)
        split(self.info, runvars)
        lowercase(self.info, runvars)
        split_numbers(self.info, runvars)
        remove_nonalnum(self.info, runvars)
        remove_nonascii(self.info, runvars)
        replace_numbers(self.info, runvars)
        
        return runvars['tokens'] + runvars['fixed_tokens']


# ## Test tokenizer

# In[14]:


def execute_default_tokenizer(info, runvars):
    token = DefaultTokenizer(info)
    runvars['tokens'] = token.tokenize(runvars['document']['text'])

if RUN_SCRIPT: run_and_compare(info, runvars, execute_default_tokenizer, ['document','text'], 'tokens')

