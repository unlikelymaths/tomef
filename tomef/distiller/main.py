from importlib import import_module

import config
import data
from util import iterate, info_summary_str
from base import nbprint

from distiller.distiller_util import check_requirements
from distiller.rejector import Rejector

def run_distiller_on(first_info, second_info):
    global rejector
    must_execute = False
    info = first_info.copy()
    if second_info is None:
        must_execute = True
    else:
        must_execute = (first_info.get('token_version',None) == second_info['token_version'] and
                        first_info.get('vocab_version',None) == second_info['vocab_version'] and
                        first_info.get('vector_version',None) == second_info['vector_version'])
        info['second_info'] = second_info
    if must_execute or rejector.allow():
        nbprint('({}), ({})'.format(info_summary_str(first_info),info_summary_str(second_info))).push()
        if config.skip_existing and data.topiclist_exists(info):
            nbprint('Skipping Distiller (file(s) exists)')
        else:
            info['distiller'].run_distiller(info)
            info['distiller'].save()
            nbprint('Distiller: success')
        nbprint.pop()
    
def add_second_info(info):
    if info['distiller_info'].get('requires_bow', False):
        second_info = {'data_name': info['data_name']}
        iterate(['token:BC', 'vocab', 'vector:B'], 
                lambda second_info: run_distiller_on(info, second_info), 
                info = second_info, 
                print_iterates = False)
    else:
        run_distiller_on(info, None)
            
def run_distiller():
    global rejector
    rejector = Rejector(0.99)
    
    nbprint('Distiller').push()
    
    iterate(['distiller', 'distillerinputs'], 
            add_second_info, 
            print_iterates = False)
    
    nbprint.pop()