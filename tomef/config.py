import os
import json
import collections
import pdb
import random
import sys

from base import nbprint

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

###############################################################################
# Exceptions
###############################################################################

class ConfigException(Exception):
    pass

###############################################################################
# Content
###############################################################################

skip_existing = None
graceful_errors = None

paths = None
plots = None
datasets = None
embeddings = None

importer = None
tokenizer = None
vocab = None
vectorizer = None

models = None
distiller = None
metrics = None
display = None

def error_occured():
    if not graceful_errors:
        nbprint('Stopping Execution...')
        sys.exit()

###############################################################################
# BCP to/from string
###############################################################################

def merge(bcp, id):
    return "{}{}".format(bcp, id)

def split(version_string):
    try:
        id = int(version_string[1:])
    except:
        id = version_string[1:]
    return version_string[:1], id

###############################################################################
# Version lists
###############################################################################

def _indexed_list(bcp_dict, bcps):
    return [merge(bcp,idx) 
            for bcp in bcps 
              for idx in range(len(bcp_dict[bcp]))]

def token_version_list(bcps):
    version_list = []
    for bcp in bcps:
        if bcp == 'B':
            version_list +=  _indexed_list(tokenizer, 'B')
        elif bcp == 'C':
            version_list += [merge('C',embedding_name) 
                             for embedding_name in embeddings['C'].keys()]
    return version_list

def vocab_version_list(bcps):
    return _indexed_list(vocab, bcps)

def vector_version_list(bcps):
    version_list = []
    for bcp in bcps:
        if bcp == 'B' or bcp == 'C':
            version_list +=  _indexed_list(vectorizer, bcp)
        elif bcp == 'P':
            version_list += [merge('P',embedding_name) 
                             for embedding_name in embeddings['P'].keys()]
    return version_list

# Config Printing
def _print_line():
    print("  |" + "-"*(80-3))

def print_value(keystring, value, indent):
    value_position = 20
    spacing = max(value_position - (len(keystring) + 2 * indent),0)
    print("  | {}{}: {}{}".format("  "*indent,keystring," "*spacing,value))
    
def _print_list(list, indent = 1):
    for pos,item in enumerate(list):
        if type(item) is dict:
            print("  | {}[{}]:".format("  "*indent,pos))
            _print_dict(item, indent+1)
        elif type(item) is list:
            print("  | {}[{}]:".format("  "*indent,pos))
            _print_list(item, indent+1)
        else:
            print_value("[{}]".format(pos), item, indent)

def _print_dict(dictionary, indent = 1):
    if "run" in dictionary and not dictionary["run"]:
        print("  | {}[not active]".format("  "*indent))
        return
    for key, val in dictionary.items():
        if type(val) is dict:
            if "name" in val:
                print("  | {}{} ({})".format("  "*indent,val["name"],key))
            else:
                print("  | {}{}".format("  "*indent,key))
            _print_dict(val, indent+1)
        elif type(val) is list:
            print("  | {}{}:".format("  "*indent,key))
            _print_list(val, indent+1)
        else: 
            if "_info" in key or key in ["run","name"]:
                continue
            print_value(key, val, indent)
 
def show():
    print("  " + "#"*(80-2))
    print("  | Configuration")
    _print_line()
    print("  | Paths")
    _print_dict(paths)
    _print_line()
    print("  | Plots")
    _print_dict(plots)
    _print_line()
    print("  | Datasets")
    _print_dict(datasets)
    _print_line()
    print("  | Embeddings")
    _print_list(embeddings)
    _print_line()
    print("  | Importer")
    _print_dict(importer)
    _print_line()
    print("  | Tokenizer")
    _print_dict(tokenizer)
    _print_line()
    print("  | Vocab")
    _print_dict(vocab)
    _print_line()
    print("  | Vectorizer")
    _print_dict(vectorizer)
    _print_line()
    print("  | Models")
    _print_dict(models)
    _print_line()
    print("  | Distiller")
    _print_dict(distiller)
    _print_line()
    print("  | Metrics")
    _print_dict(metrics)
    print("  " + "#"*(80-2))
    print("")
    
# Load config
def _load_json(filename):
    global skip_existing, graceful_errors
    global paths, plots, datasets, embeddings
    global importer, tokenizer, vocab, vectorizer
    global models, distiller, metrics, display
    with open(filename, "r") as file:
        jsonconfig = json.load(file)
        skip_existing = jsonconfig["skip_existing"]
        graceful_errors = jsonconfig["graceful_errors"]
        
        paths = jsonconfig["paths"]
        plots = jsonconfig["plots"]
        datasets = jsonconfig["datasets"]
        embeddings = jsonconfig["embeddings"]
        
        importer = jsonconfig["importer"]
        tokenizer = jsonconfig["tokenizer"]
        vocab = jsonconfig["vocab"]
        vectorizer = jsonconfig["vectorizer"]
        
        models = jsonconfig["models"]
        distiller = jsonconfig["distiller"]
        metrics = jsonconfig["metrics"]
        display = jsonconfig["display"]

def _set_paths(dirname):
    oldpaths = paths.copy()
    for pathname,path_rel in oldpaths.items():
        if pathname.endswith("_rel"):
            del paths[pathname]
            path = os.path.join(dirname,path_rel)
            paths[pathname[:-4]] = os.path.abspath(path)
            
def load_config(filename = None):
    config_dir = os.path.join(base_dir,'config')
    data_base_dir = base_dir
    if filename is None:
        filename = os.path.join(config_dir,'default.json')
    elif not os.path.isabs(filename):
        filename = os.path.join(config_dir,filename)
    else:
        data_base_dir = os.path.dirname(filename)
    _load_json(filename)
    _set_paths(data_base_dir)

load_config()