#!/usr/bin/env python
# coding: utf-8

# # Classification
# <div style="position: absolute; right:0;top:0"><a href="./metrics.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# `Description`
# 
# ---
# ## Setup
# ---

# In[10]:


from __init__ import init_vars
init_vars(vars(), ('info', {}))

import numpy as np
from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
import data
import config
from base import nbprint
from util import ProgressIterator
from widgetbase import nbbox

from metrics.widgets import h_mat_picker
from metrics.helper import load_ground_truth_classes

if RUN_SCRIPT: h_mat_picker(info)


# ---
# ## SVM with 5-fold cross-validation: Micro F1 score
# ---
# 
# `Definition`

# In[11]:


def svm_5fold_micro_f1(labels_true, h_mat):
    scaler = StandardScaler()
    h_mat = scaler.fit_transform(h_mat)
    clf = svm.SVC(kernel='linear', C=1, max_iter = 200)
    scores = cross_val_score(clf, h_mat.transpose(),labels_true, cv=5, scoring='f1_micro')
    return list(scores)


# In[12]:


if RUN_SCRIPT:
    nbbox(mini=True)
    labels_true = load_ground_truth_classes(info)
    h_mat = data.load_h_mat(info)
    score = svm_5fold_micro_f1(labels_true, h_mat)
    nbprint('Average Micro F1 Score: {}'.format(np.mean(score)))

