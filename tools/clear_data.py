#!/usr/bin/env python
# coding: utf-8

# # Clear Data
# <div style="position: absolute; right:0;top:0"><a href="./tools.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# This script deletes all files in the following folders to free up disk space. Use with caution!
# - imported
# - tokenized
# - vocab
# - vectorized
# - models

# In[ ]:


from init import setup
setup(vars())
try:
    get_ipython().run_line_magic('reload_ext', 'autoreload')
    get_ipython().run_line_magic('autoreload', '2')
except NameError: pass

from os import listdir, remove
from os.path import isfile, join

import config
from base import nbprint

def clear_data(dryrun):
    folders = [config.paths['imported'],
             config.paths['tokenized'],
             config.paths['vocab'],
             config.paths['vectorized'],
             config.paths['models'],
             ]
    
    for clear_dir in folders:
        for f in listdir(clear_dir):
            f_abs = join(clear_dir, f)
            if isfile(f_abs) and not f_abs.endswith('.gitignore'):
                nbprint('Deleting {}'.format(f_abs))
                if not dryrun:
                    remove(f_abs) 
                    
def main():
    clear_data(False)
    
if _isMain:
    clear_data(True)

