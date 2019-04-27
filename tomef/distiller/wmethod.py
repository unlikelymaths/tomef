#!/usr/bin/env python
# coding: utf-8

# # W Method
# <div style="position: absolute; right:0;top:0"><a href="./distiller.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# `Description`
# 
# ---
# ## Setup and Settings
# ---

# In[1]:


from __init__ import init_vars
init_vars(vars(), ('info',{}))

import numpy as np

import data
import config
from base import nbprint
from widgetbase import nbbox

from distiller.widgets import w_mat_picker
from distiller.common import TopicEntry
from distiller.distiller_util import DistillerBase

if RUN_SCRIPT: w_mat_picker(info)


# ---
# ## Show all
# ---

# In[2]:


class WMethod(DistillerBase):
    def run(self, info):
        num_tokens = config.distiller['num_tokens']
        w_mat = data.load_w_mat(info)
        vocab = data.load_vocab_list(info)
        sorted_idcs = np.argsort(w_mat, axis=0)
        topiclist = []
        for col in range(w_mat.shape[1]):
            topic = []
            for idx in sorted_idcs[-num_tokens:,col][::-1]:
                topic.append(TopicEntry(idx = int(idx), 
                                        weight = float(w_mat[idx, col]), 
                                        token = vocab[idx]))
            topiclist.append(topic)
        self.topic_token_version = info['token_version']
        self.topiclist = topiclist


# In[3]:


if RUN_SCRIPT:
    nbbox(mini=True)
    distiller_model = WMethod(info)
    distiller_model.run_distiller(info)
    for topic_idx, topic in enumerate(distiller_model.topiclist):
        nbprint('**Topic {}**'.format(topic_idx))
        nbprint('  \n'.join(["- `{}` ({})".format(entry.token,entry.weight) for entry in topic[:10]]))

