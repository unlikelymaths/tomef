import os
import sys
from IPython import get_ipython

def init_vars(vars_dict, *args):
    if vars_dict['__name__'] == '__main__':
        ipython = get_ipython()
        ipython.magic("reload_ext autoreload")
        ipython.magic("autoreload 2")
        parent_path = os.path.join(os.path.dirname(__file__),os.pardir)
        if parent_path not in sys.path:
            sys.path.append(parent_path)
        vars_dict['RUN_SCRIPT'] = True
        
        for arg in args:
            if arg[0] not in vars_dict:
                vars_dict[arg[0]] = arg[1]
    else:
        vars_dict['RUN_SCRIPT'] = False