#!/usr/bin/env python
# coding: utf-8

# # Export Results
# <div style="position: absolute; right:0;top:0"><a href="./tools.ipynb" style="text-decoration: none"> <font size="5">←</font></a>
# <a href="../evaluation.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# This script collects all HTML files and puts them into a `export.zip` archive in the results folder. Useful for sharing results outside of a jupyter lab.
# 
# https://nbconvert.readthedocs.io/en/5.x/nbconvert_library.html

# In[ ]:


from init import setup
setup(vars())

import os
import zipfile 

if _isMain:
    try:
        runvars = {'basepath': os.path.join(os.path.dirname(__file__),'../')}
    except:
        runvars = {'basepath': os.path.join(os.getcwd(),'../')}

def code_folders(runvars):
    runvars['basepath'] = os.path.abspath(runvars['basepath'])
    dir_list = ['./','./docs/','./tools/', './embedding/',
                './importer/', './tokenizer/', './vocab/', 
                './vectorizer/', './models/', './distiller/', 
                './metrics/']
    file_list = []
    
    file_types = ['.html', '.md', '.png']
    
    for directory in dir_list:
        directory_abs = os.path.abspath(os.path.join(runvars['basepath'],directory))
        for filename in os.listdir(directory_abs):
            if any([file_type for file_type in file_types if filename.endswith(file_type)]):
                filename_full = os.path.join(directory,filename)
                filename_abs= os.path.join(runvars['basepath'],filename_full)
                file_list.append((filename_abs, filename_full))
        
    zip_path = os.path.join(runvars['basepath'],'results/export.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip: 
        # writing each file one by one 
        for file in file_list: 
            zip.write(file[0], arcname = file[1]) 
            
def main(basepath):
    runvars = {'basepath': basepath}
    code_folders(runvars)
    
if _isMain:
    code_folders(runvars)

