import matplotlib.pyplot as plt
from importlib import import_module
from types import MethodType

import config, data
from base import nbprint

###############################################################################
# Exceptions
###############################################################################

class UtilException(Exception):
    pass

class BreakIteration(Exception):
    pass

###############################################################################
# Decorators
###############################################################################

def add_method(cls):
    """Decorator. @add_method(cls) binds the following function to the class cls."""
    def decorator(func):
        #method = MethodType(func,cls)                                    
        #setattr(cls, func.__name__, method)
        setattr(cls, func.__name__, func)
        return func
    return decorator

###############################################################################
# Progress bar in console and jupyter 
###############################################################################
    
_last_prefix_length = 0
_progress_widget = None
    
def print_progress(progress, prefix = ""):
    global _last_prefix_length, _progress_widget
    if _progress_widget is None:
        _last_prefix_length = len(prefix)
        progress = max(min(1,progress),0)
        print("\r{0}[{1:50s}] {2:.1f}%"
            .format(prefix,'#' * int(progress * 50), progress*100), end="", flush=True)
    else:
        _progress_widget.layout.visibility = 'visible'
        _progress_widget.description = prefix
        _progress_widget.value = progress
        
        
def clear_progress():
    global _last_prefix_length, _progress_widget
    if _progress_widget is None:
        print("\r{}".format(" "*(_last_prefix_length + 60)), end="", flush=True)
        print("\r", end="", flush=True)
    else:
        _progress_widget.layout.visibility = 'hidden'
        _progress_widget.value = 0

class ProgressIterator:
    def __init__(self, sequence, prefix = "", print_every = 100, length = None):
        self.prefix = prefix
        self.print_every = print_every
        self.sequence = sequence
        self.length = length
        self.pseudo = False
        
    def __del__(self):
        clear_progress()
        
    def __iter__(self):
        if self.length is None:
            try:
                self.length = len(self.sequence)
            except:
                self.pseudo = True
                self.direction = 1
                self.current = 0
        self.iter = enumerate(iter(self.sequence))
        return self

    def __next__(self):
        idx, object = next(self.iter)
        if idx%self.print_every == 0:
            if self.pseudo:
                print_progress(self.current/100, self.prefix)
                if self.current >= 100:
                    self.direction = -1
                elif self.current <= 0:
                    self.direction = 1
                self.current += self.direction
            else:
                print_progress(idx/self.length, self.prefix)
        return object    
        
class EnumerateProgressIterator:
    def __init__(self, sequence, prefix = "", print_every = 100, length = None):
        self.prefix = prefix
        self.print_every = print_every
        self.sequence = sequence
        self.length = length
        self.pseudo = False
        
    def __iter__(self):
        if self.length is None:
            try:
                self.length = len(self.sequence)
            except:
                self.pseudo = True
                self.direction = 1
                self.current = 0
        self.iter = enumerate(iter(self.sequence))
        return self

    def __next__(self):
        try:
            idx, object = next(self.iter)
        except StopIteration:
            clear_progress()
            raise StopIteration
        if idx%self.print_every == 0:
            if self.pseudo:
                print_progress(self.current/100, self.prefix)
                if self.current >= 100:
                    self.direction = -self.direction
                elif self.current <= 0:
                    self.direction = -self.direction
                self.current += self.direction
            else:
                print_progress(idx/self.length, self.prefix)
        return idx, object    
    
###############################################################################
# Importer    
###############################################################################

def import_base(base_mod, mod, im_name):
    mod = import_module("{}.{}".format(base_mod, mod))
    return getattr(mod, im_name)
    
def import_cls(base_mod, mod, cls_name):
    return import_base(base_mod, mod, cls_name)

def import_fct(base_mod, mod, fct_name):
    return import_base(base_mod, mod, fct_name)


def convert_num_topics(info, num_topics):
    if isinstance(num_topics, str):
        gt = len(data.load_classes(info))
        if num_topics == "gt":
            num_topics = gt
        elif num_topics.endswith("gt"):
            num_topics = int(float(num_topics[:-2]) * gt)
        else:
            raise config.ConfigException('Unknown "num_topics" format: {}'.format(num_topics))
    return num_topics

def info_summary_str(info):
    if info is None:
        return '-'
    summary_str = []
    for entry in ['data_name', 'token_version', 'vocab_version', 'vector_version',
                  'model_name', 'distiller_name']:
        if entry in info:
            summary_str.append('{}:{}'.format(entry, info[entry]))
    return ', '.join(summary_str)    

###############################################################################
# Iterators    
###############################################################################
           
def check_model_output(info, original_callback):
    global _required_model_outputs
    output = info['model'].output_of(info)
    if _required_model_outputs is None:
        if len(output) == 0:
            raise BreakIteration()
    else:
        for required_output in _required_model_outputs:
            if required_output not in output:
                raise BreakIteration()
                
    if original_callback is not None:
        original_callback(info)
    
def call_next(what, callbacks, print_string, new_data, info, depth, print_iterates):
    if print_string and print_iterates == True:
        nbprint(print_string)
    if print_iterates == True:
        nbprint.push()
    new_info = {**info, **new_data}
    if len(callbacks) < len(what):
        iterate(what[1:], callbacks, new_info, depth + 1)
    else:
        try:
            if callbacks[0]:
                callbacks[0](new_info)
            if len(what) > 1:
                iterate(what[1:], callbacks[1:], new_info, depth + 1, print_iterates)
        except BreakIteration:
            if print_iterates == True:
                nbprint('skipping')
            pass
    if print_iterates == True:
        nbprint.pop()
    
def iterate(what, callbacks, info = {}, depth = 1, print_iterates = True):
    global _required_model_outputs
    if not isinstance(what, list):
        what = [what,]
    if not isinstance(callbacks, list):
        callbacks = [callbacks,]
    callbacks = [None] * (len(what) - len(callbacks)) + callbacks
    
    # data
    # token[:BC]
    # vocab
    # vector[:BCP]
    # models[:W,H]
    # modelinputs
    # num_topics
    try:
        category, detail = what[0].split(':')
    except ValueError:
        category, detail = what[0], None
        
    if category == "data":
        for data_name, data_info in config.datasets.items():
            if data_info["run"]:
                new_data = {"data_name": data_name, 
                    "data_info": data_info}
                call_next(what, callbacks, data_info["name"], 
                    new_data, info, depth, print_iterates)
    elif category == 'token':
        for token_version in config.token_version_list(detail or 'BCP'):
            bcp, id = config.split(token_version)
            if bcp == 'B':
                token_info = config.tokenizer['B'][id]
                if token_info["run"]:
                    new_data = {'token_version': token_version, 
                                'token_info': token_info}
                    call_next(what, callbacks, "Token {}".format(token_version), 
                        new_data, info, depth, print_iterates)
            elif bcp == 'C':
                embedding_info = config.embeddings['C'][id]
                if embedding_info["run"]:  
                    new_data = {'token_version': token_version, 
                                'token_info': embedding_info['token_info'],
                                'embedding_name': id,
                                'embedding_info': embedding_info}
                    call_next(what, callbacks, "Token {}".format(token_version), 
                        new_data, info, depth, print_iterates)
    elif category == "vocab":
        if "token_version" not in info:
            print("{}WARNING: Cannot iterate 'vocab' without knowing token version"
                .format("  "*depth))
            return
        bcp = config.split(info["token_version"])[0]
        for vocab_version in config.vocab_version_list(bcp):
            bcp, id = config.split(vocab_version)
            vocab_info = config.vocab[bcp][id]
            if vocab_info["run"]:
                new_data = {"vocab_version": vocab_version, 
                    "vocab_info": vocab_info}
                call_next(what, callbacks, "Vocab {}".format(new_data["vocab_version"]), 
                    new_data, info, depth, print_iterates)
    elif category == 'vector':
        for vector_version in config.vector_version_list(detail or 'BCP'):
            bcp, id = config.split(vector_version)
            if bcp == 'B' or bcp == 'C':
                vector_info = config.vectorizer[bcp][id]
                if vector_info["run"]:
                    new_data = {"vector_version": vector_version, 
                                "vector_info": vector_info}
                    call_next(what, callbacks, "Vector {}".format(new_data["vector_version"]), 
                                new_data, info, depth, print_iterates)
            elif bcp == 'P':
                embedding_info = config.embeddings['P'][id]
                if embedding_info["run"]:
                    new_data = {"vector_version": vector_version, 
                        "embedding_info": embedding_info}
                    call_next(what, callbacks, "Vector {}".format(new_data["vector_version"]), 
                                new_data, info, depth, print_iterates)
    elif category == "models":
        if detail is not None:
            detail = detail.split(',')
        _required_model_outputs = detail
        for model_name, model_info in config.models['list'].items():
            if model_info["run"]:
                model = import_cls('models', model_info['mod'], model_info['cls'])(model_info)
                new_data = {'model_name': model_name,
                            'model_info': model_info,
                            'model': model}
                call_next(what, callbacks, "Model {}".format(model_info["name"]), 
                    new_data, info, depth, print_iterates)
    elif category == 'modelinputs':
        vector_bcps = info['model_info'].get('vector', 'BCP')
        original_callback = callbacks[0]
        callbacks[0] = lambda i : check_model_output(i, original_callback)
        if 'B' in vector_bcps:
            token_bcps = info['model_info'].get('token', 'BC')
            what_b = what.copy()
            what_b[1:1] = ['data', 'token:{}'.format(token_bcps), 'vocab', 'vector:B']
            callbacks_b = [None] * (len(what_b) - len(callbacks)) + callbacks
            call_next(what_b, callbacks_b, 'Model Input BoW', {}, info, depth, print_iterates)
        if 'C' in vector_bcps:
            what_c = what.copy()
            what_c[1:1] = ['data', 'token:C', 'vocab', 'vector:C']
            callbacks_c = [None] * (len(what_c) - len(callbacks)) + callbacks
            call_next(what_c, callbacks_c, 'Model Input cBoW', {}, info, depth, print_iterates)
        if 'P' in vector_bcps:
            what_p = what.copy()
            what_p[1:1] = ['data', 'vector:P']
            callbacks_p = [None] * (len(what_p) - len(callbacks)) + callbacks
            call_next(what_p, callbacks_p, 'Model Input Phrase', {}, info, depth, print_iterates)
    elif category == "num_topics":
        if "data_info" in info:
            for num_topics in info["data_info"]["num_topics"]:
                num_topics = convert_num_topics(info, num_topics)
                new_data = {"num_topics": num_topics}
                call_next(what, callbacks, "Topics {}".format(num_topics), 
                    new_data, info, depth, print_iterates)
        else:
            raise UtilException('Cannot iterate "num_topics" without knowing data')
    elif category == "distiller":
        for distiller_name, distiller_info in config.distiller['list'].items():
            if distiller_info["run"]:
                distiller = import_cls('distiller', distiller_info['mod'], distiller_info['cls'])(distiller_info)
                new_data = {'distiller_name': distiller_name,
                            'distiller_info': distiller_info,
                            'distiller': distiller}
                call_next(what, callbacks, "Distiller {}".format(distiller_info["name"]), 
                    new_data, info, depth, print_iterates)
    elif category == "distillerinputs":
        model_out = info['distiller_info']['model_out']
        original_callback = callbacks[0]
        for model_out_entry in model_out:
            what_version = what.copy()
            what_version[1:1] = ['models:{}'.format(model_out_entry),'modelinputs','num_topics']
            callbacks_version = [None] * (len(what_version) - len(callbacks)) + callbacks
            call_next(what_version, callbacks_version, 'Model Input BoW', {}, info, depth, print_iterates)
    else:
        print("{}WARNING: Cannot iterate '{}'".format("  "*depth, what[0]))
    
###############################################################################
# Matplotlib helper
###############################################################################

def wait_for_plots():
    while len(plt.get_fignums()) > 0:
        try:
            plt.pause(60*60)
        except:
            pass