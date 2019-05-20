import time
import matplotlib.pyplot as plt
from importlib import import_module
from types import MethodType

from base import config, data

def add_method(cls):
    """Decorator to bind a function to a class.
    
    Example:
        @add_method(cls)
        def method(args):
            pass
    """
    
    def decorator(func):
        #method = MethodType(func,cls)                                    
        #setattr(cls, func.__name__, method)
        setattr(cls, func.__name__, func)
        return func
    return decorator


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


def wait_for_plots():
    while len(plt.get_fignums()) > 0:
        try:
            plt.pause(60*60)
        except:
            pass

def strip_info(info):
    stripped_info = {}
    for entry in ['data_name', 'token_version', 'vocab_version',
                  'vector_version', 'model_name', 'num_topics',
                  'distiller_name']:
        if entry in info:
            stripped_info[entry] = info[entry]
    return stripped_info
        
class ModuleTimer():
    """Provides timing of modules with automatic saving"""
    
    def __init__(self, module, info):
        self.module = module
        self.meta_file = '{}_timings'.format(module)
        self.info = strip_info(info)
    
    def __enter__(self):
        self.start = time.time()
        
    def __exit__(self, exc_type, exc_value, traceback):
        # Do not save runtime when an exception occured
        if exc_type is not None:
            return
        # Get runtime
        end = time.time()
        runtime = end - self.start
        # Grab meta data entry
        meta_data = data.load_meta_data(self.meta_file)
        try:
            meta_data_line = [line for line in meta_data if line['info'] == self.info][0]
        # If it doesn't exist create a new one
        except:
            meta_data_line = {'info': self.info}
            meta_data.append(meta_data_line)
        meta_data_line['runtime'] = runtime
        data.save_meta_data(meta_data,self.meta_file)