#!/usr/bin/env python
# coding: utf-8

# # Tools
# <div style="position: absolute; right:0;top:0"><a href="../evaluation.py.ipynb" style="text-decoration: none"> <font size="5">↑</font></a></div>
# 
# Various Scripts. Command line use:
# 
# `python evaluation.py --script scriptname`
# 
# ## Overview
# `scriptname` in brackets
# - [Export Results](./export_results.ipynb) (export)
# - [Clear Data](./clear_data.ipynb) (cleardata)

# In[ ]:


import argparse
from os.path import join, dirname

def run_tools_():
    parser = argparse.ArgumentParser(description="Topic Modeling Evaluation Framework")
    parser.add_argument('-s','--script',
        action='store',
        choices=['letter', 'wiki', 'tweetsodp', 'export', 'cleardata'],
        help='Runs a script from the tools folder')
    parser.add_argument('-p','--printconfig',
        action='store_true',
        help='Prints the configuration')
    args = parser.parse_args()
    
    if args.script:
        if args.script == "letter":
            pass
        elif args.script == "wiki":
            pass
        elif args.script == "tweetsodp":
            pass
        elif args.script == "export":
            from tools.export_results import main as export_results_main
            export_results_main(join(dirname(__file__),'../'))
        elif args.script == 'cleardata':
            from tools.clear_data import main as clear_data_main
            clear_data_main()
        exit()
        
def run_tools():
    try:
        get_ipython
    except:
        run_tools_()

