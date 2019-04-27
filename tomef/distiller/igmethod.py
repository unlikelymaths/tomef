#!/usr/bin/env python
# coding: utf-8

# # Information Gain
# <div style="position: absolute; right:0;top:0"><a href="./distiller.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# `Description`
# 
# ---
# ## Setup and Settings
# ---

# In[3]:


from __init__ import init_vars
init_vars(vars(), ('info',{}))

import numpy as np
from sklearn.feature_selection import mutual_info_classif

import data
import config
from base import nbprint
from widgetbase import nbbox

from distiller.widgets import h_mat_and_bow_picker
from distiller.common import TopicEntry
from distiller.distiller_util import DistillerBase

if RUN_SCRIPT: h_mat_and_bow_picker(info)


# ---
# ## Mutual Information
# ---

# In[7]:


def load_c_vec(info):
    if data.c_vec_exists(info):
        return data.load_c_vec(info)
    elif data.h_mat_exists(info):
        h_mat = data.load_h_mat(info)
        return np.argmax(h_mat, axis=0)
    
def load_mat_ids(info):
    if config.split(info['vector_version'])[0] == 'P':
        meta = data.load_document_meta(info)
        return range(meta['num_documents'])
    else:
        return data.load_mat_ids(info)


# In[8]:


class IGMutualInfo(DistillerBase):
    def run(self, info):
        c_vec = load_c_vec(info)
        if c_vec is None:
            return
        second_info = info['second_info'] 
        num_tokens = config.distiller['num_tokens']
        num_topics = info['num_topics']
        vocab = data.load_vocab_list(second_info)
        input_mat = data.load_input_mat(second_info)
        c_vec_ids = load_mat_ids(info)
        input_mat_ids = data.load_mat_ids(second_info)
        
        common_ids = [i for i in c_vec_ids if i in input_mat_ids]
        filter_c_vec = [idx for idx, docid in enumerate(c_vec_ids) if docid in common_ids]
        c_vec = c_vec[filter_c_vec]
        filter_input_mat = [idx for idx, docid in enumerate(input_mat_ids) if docid in common_ids]
        input_mat = input_mat[:, filter_input_mat]
        
        topiclist = []
        for topic_idx in range(num_topics):
            topic = []
            target_vector = (c_vec == topic_idx).astype(int)
            mi = mutual_info_classif(input_mat.transpose(), target_vector)
            sorted_idcs = np.argsort(mi)
            for idx in sorted_idcs[-num_tokens:][::-1]:
                topic.append(TopicEntry(idx = int(idx), 
                                        weight = mi[idx], 
                                        token = vocab[idx]))
            topiclist.append(topic)
            
        self.topic_token_version = second_info['token_version']
        self.topiclist = topiclist


# In[9]:


if RUN_SCRIPT:
    nbbox(mini=True)
    distiller_model = IGMutualInfo(info)
    distiller_model.run_distiller(info)
    for topic_idx, topic in enumerate(distiller_model.topiclist):
        nbprint('**Topic {}**'.format(topic_idx))
        nbprint('  \n'.join(["- `{}` ({})".format(entry.token,entry.weight) for entry in topic[:10]]))

