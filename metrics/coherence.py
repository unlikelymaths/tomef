#!/usr/bin/env python
# coding: utf-8

# # Coherence
# <div style="position: absolute; right:0;top:0"><a href="./metrics_index.doc.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# `Description`
# 
# ---
# ## Setup and Settings
# ---

# In[15]:


from __init__ import init_vars
init_vars(vars(), ('info', {}))

import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import CoherenceModel, KeyedVectors
from gensim.corpora import WikiCorpus, Dictionary

import data
import config
from base import nbprint
from util import ProgressIterator
from widgetbase import nbbox
from os.path import join, isfile
from tokenizer.main import get_tokenizer

from metrics.widgets import topiclist_picker

if RUN_SCRIPT: topiclist_picker(info)


# ---
# ## $C_v$ Coherence (Wiki)
# ---
# 
# `Definition`

# In[20]:


def wiki_dict_filename(wiki_raw_filename, token_version):
    return join(config.paths["misc"], wiki_raw_filename + "{}.txt.bz2".format(token_version))
        
def wiki_corpus_filename(wiki_raw_filename, token_version):
    return join(config.paths["misc"], wiki_raw_filename + "{}.bow.mm".format(token_version))

def get_tokenizer_func(token_version):
    bcp, id = config.split(token_version)
    info = {'token_version': token_version}
    if bcp == 'B':
        info['token_info'] = config.tokenizer['B'][id]
    elif bcp == 'C':
        info['embedding_name'] = id
        info['embedding_info'] = config.embeddings['C'][id]
        info['token_info'] = config.embeddings['C'][id]['token_info']
    return get_tokenizer(info)
    
def make_wikicorpus(wiki_raw_filename, token_version):
    nbprint('Scanning Wiki for vocab')
    keep_n = 1000000
    no_above = 1
    no_below = 1
    wiki_raw_path = join(config.paths["rawdata"], 'wiki/' + wiki_raw_filename)
    tokenizer_func = get_tokenizer_func(token_version).tokenize
    
    wiki = WikiCorpus(wiki_raw_path, lemmatize=False, tokenizer_func=tokenizer_func)
    wiki.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_n)
    wiki.dictionary.save_as_text(wiki_dict_filename(wiki_raw_filename, token_version))
    nbprint(' MmCorpus.serialize')
    MmCorpus.serialize(wiki_corpus_filename(wiki_raw_filename, token_version), wiki, progress_cnt=10000)

def get_dict(wiki_raw_filename, token_version):
    nbprint('Loading Dictionary')
    wiki_dict_fn = wiki_dict_filename(wiki_raw_filename, token_version)
    if not isfile(wiki_dict_fn):
        make_wikicorpus(wiki_raw_filename, token_version)
    return Dictionary.load_from_text(wiki_dict_fn)

def get_corpus(wiki_raw_filename, token_version, dictionary):
    nbprint('Loading Corpus')
    wiki_raw_path = join(config.paths["rawdata"], 'wiki/' + wiki_raw_filename)
    tokenizer_func = get_tokenizer_func(token_version).tokenize
    return WikiCorpus(wiki_raw_path, dictionary=dictionary, tokenizer_func=tokenizer_func)

def filter_tokens(topiclist, dictionary):
    nbprint('Filtering Tokens')
    topiclist_reduced = []
    removed_tokens = {}
    for topic in topiclist:
        topic_reduced = []
        for entry in topic:
            if entry.token in dictionary.token2id:
                topic_reduced.append(entry.token)
            else:
                try:
                    removed_tokens[entry.token] += 1
                except KeyError:
                    removed_tokens[entry.token] = 1
        topiclist_reduced.append(topic_reduced)
    nbprint("Removed {} tokens from {} topics.".format(len(removed_tokens), len(topiclist)))
    return topiclist_reduced

def get_coherence_per_topic(topiclist, token_version, coherence_model):
    idx = 0
    slice_len = 2000
    coherences = []
    wiki_raw_filename = 'enwiki-20180920-pages-articles1.xml-p10p30302.bz2'
    dictionary = get_dict(wiki_raw_filename, token_version)
    wiki_corpus = get_corpus(wiki_raw_filename, token_version, dictionary)
    nbprint('Computing Coherence')
    while idx < len(topiclist):
        nbprint('Slice {}-{} of {}'.format(idx, idx+slice_len-1, len(topiclist)))
        topiclist_slice = topiclist[idx:idx+slice_len]
        topiclist_reduced = filter_tokens(topiclist_slice, dictionary)
        cm = CoherenceModel(topics=topiclist_reduced, texts=wiki_corpus.get_texts(), dictionary=dictionary, coherence=coherence_model)
        coherences += cm.get_coherence_per_topic()
        idx += slice_len
    return coherences

def cv_wiki(topiclist, token_version):
    return get_coherence_per_topic(topiclist, token_version, 'c_v')
    
def umass_wiki(topiclist, token_version):
    return get_coherence_per_topic(topiclist, token_version, 'u_mass')


# ---
# ## Show all
# ---

# In[ ]:


if RUN_SCRIPT:
    nbbox(mini=True)
    topiclist = data.load_topiclist(info)
    topiclist = [topic[:10] for topic in topiclist[:2]]
    token_version = info['token_version']
    if 'second_info' in info:
        token_version = info['second_info']['token_version']
    u_mass = umass_wiki(topiclist, token_version)
    #c_v = cv_wiki(topiclist, token_version)

