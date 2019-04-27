#!/usr/bin/env python
# coding: utf-8

# # Clustering
# <div style="position: absolute; right:0;top:0"><a href="./metrics.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# `Description`
# 
# ---
# ## Setup
# ---

# In[2]:


from __init__ import init_vars
init_vars(vars(), ('info', {}))

from sklearn.metrics.cluster import normalized_mutual_info_score, adjusted_rand_score

import data
import config
from base import nbprint
from util import ProgressIterator
from widgetbase import nbbox

from metrics.widgets import h_mat_picker
from metrics.helper import load_ground_truth_classes, load_class_array_from_h_mat

if RUN_SCRIPT: h_mat_picker(info)


# ---
# ## NMI
# ---
# 
# `Definition`

# In[3]:


def nmi(labels_true, labels_pred):
    return normalized_mutual_info_score(labels_true, labels_pred)


# ---
# ## ARI
# ---
# 
# `Definition`

# In[4]:


def ari(labels_true, labels_pred):
    return adjusted_rand_score(labels_true, labels_pred)


# ---
# ## Show all
# ---

# In[5]:


if RUN_SCRIPT:
    nbbox(mini=True)
    labels_true = load_ground_truth_classes(info)
    labels_pred = load_class_array_from_h_mat(info)
    
    nbprint('NMI score: {}'.format(nmi(labels_true, labels_pred)))
    nbprint('ARI score: {}'.format(ari(labels_true, labels_pred)))
    

