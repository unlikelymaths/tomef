#!/usr/bin/env python
# coding: utf-8

# # Pseudo W Method
# <div style="position: absolute; right:0;top:0"><a href="./distiller.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# `Description`
# 
# ---
# ## Setup
# ---

# In[1]:


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
# ## Show all
# ---

# In[2]:


def load_h_mat(info):
    return data.load_h_mat(info)
    
def load_mat_ids(info):
    if config.split(info['vector_version'])[0] == 'P':
        meta = data.load_document_meta(info)
        return range(meta['num_documents'])
    else:
        return data.load_mat_ids(info)


# In[7]:


class WMethod(DistillerBase):
    def run(self, info):
        h_mat = load_h_mat(info)
        if h_mat is None:
            return
        second_info = info['second_info'] 
        num_tokens = config.distiller['num_tokens']
        num_topics = info['num_topics']
        vocab = data.load_vocab_list(second_info)
        input_mat = data.load_input_mat(second_info)
        h_mat_ids = load_mat_ids(info)
        input_mat_ids = data.load_mat_ids(second_info)
        
        #common_ids = [i for i in h_mat_ids if i in input_mat_ids]
        common_ids = {}
        input_mat_ids2 = input_mat_ids.copy()
        for i in h_mat_ids:
            try:
                while input_mat_ids2[0] < i:
                    input_mat_ids2 = input_mat_ids2[1:]
                if input_mat_ids2[0] == i:
                    input_mat_ids2 = input_mat_ids2[1:]
                    common_ids[i] = True
            except IndexError:
                break
        filter_h_mat = [idx for idx, docid in enumerate(h_mat_ids) if docid in common_ids]
        h_mat = h_mat[:,filter_h_mat]
        filter_input_mat = [idx for idx, docid in enumerate(input_mat_ids) if docid in common_ids]
        input_mat = input_mat[:, filter_input_mat]
                
        eps = 1e-16
        threshold = 1e-16
        Ht = (h_mat / np.maximum(np.sum(h_mat,0),1e-16)).T
        W = input_mat @ Ht
        W = W / np.maximum(np.sum(W,0),eps)
        for iteration in range(100):
            HHT = np.dot(Ht.T,Ht)
            W_old = np.copy(W)
            for r in range(num_topics):
                hr = Ht[:,r]
                idx = [i for i in range(num_topics) if i!=r]
                wr = 1/HHT[r,r] * (input_mat @ hr - W[:,idx] @ HHT[idx,r])
                W[:,r] = np.maximum(wr, eps).T
            mean_w_change = np.mean(np.abs((W - W_old) / W_old))
            if mean_w_change < threshold:
                nbprint('Converged after {} iterations. (threshold = {})'.format(iteration+1,threshold))
                break
        for r in range(num_topics):
            W[:,r] /= np.sqrt(np.sum(np.square(W[:,r])))
        mean_topic = np.mean(W, axis=1)
        mean_topic /= np.sqrt(np.sum(np.square(mean_topic)))
        for r in range(num_topics):
            W[:,r] = W[:,r] - np.sum(W[:,r]*mean_topic) * mean_topic
        
        num_tokens = config.distiller['num_tokens']
        sorted_idcs = np.argsort(W, axis=0)
        topiclist = []
        for col in range(W.shape[1]):
            topic = []
            for idx in sorted_idcs[-num_tokens:,col][::-1]:
                topic.append(TopicEntry(idx = int(idx), 
                                        weight = W[idx, col], 
                                        token = vocab[idx]))
            topiclist.append(topic)
        self.topic_token_version = second_info['token_version']
        self.topiclist = topiclist


# In[11]:


if RUN_SCRIPT:
    nbbox(mini=True)
    info['num_topics'] = int(info['num_topics'])
    distiller_model = WMethod(info)
    distiller_model.run_distiller(info)
    for topic_idx, topic in enumerate(distiller_model.topiclist):
        nbprint('**Topic {}**'.format(topic_idx))
        nbprint('  \n'.join(["- `{}` ({})".format(entry.token,entry.weight) for entry in topic[:10]]))


# In[ ]:




