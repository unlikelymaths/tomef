from importlib import import_module

import data
import config
from util import iterate, BreakIteration, convert_num_topics
from base import nbprint

from models.common import get_model
from models.model_util import check_requirements

def check_input_mat(info):
    # Check if input_mat exists
    if not check_requirements(info):
        nbprint('Skipping Model (requirements not satisfied)')
        raise BreakIteration()
    
def run_model(info):
    info['num_topics'] = convert_num_topics(info, info['num_topics'])
    
    # Check if input mat exists
    if config.skip_existing and info['model'].output_exists(info):
        nbprint('Skipping Model (file(s) exists)')
        return
    info['model'].run(info)
    info['model'].save(info)
    nbprint('Model: success')

def run_models(info = None):
    nbprint('Models').push()
    
    if info is None:
        iterate(['models', 'modelinputs', 'num_topics'], [check_input_mat, run_model])
    else:
        info['model_info'] = config.models['list'][info['model_name']]
        info['model'] = get_model(info)
        if not info['model'].output_of(info):
            nbprint('Model is not compatible to inputs.')
        else:
            try:
                check_input_mat(info)
                run_model(info)
            except BreakIteration:
                pass
    nbprint.pop()