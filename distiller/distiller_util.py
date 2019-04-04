import numpy as np

import config
import data
from base import nbprint

from models.main import run_models
from vocab.main import run_vocab

def check_requirements(info, requirements):
    # Check if documents file exists
    if 'W' in requirements and not data.w_mat_exists(info):
        # Run Model
        nbprint('W mat missing.')
        run_models(info)
        # Check if it was successfull
        if not data.w_mat_exists(info):
            return False
    if 'vocab' in requirements and not data.vocab_exists(info):
        # Run Vocab
        nbprint('Vocab missing.')
        run_vocab(info)
        # Check if it was successfull
        if not data.vocab_exists(info):
            return False
    return True

def load_ground_truth_classes(info):
    if config.split(info['vector_version'])[0] == 'P':
        with data.document_reader(info) as documents:
            return [document['class_id'] for document in documents]
    
    mat_ids = data.load_mat_ids(info)
    ground_truth_classes = []
    with data.document_reader(info) as documents:
        for document in documents:
            if mat_ids[0] == document['id']:
                ground_truth_classes.append(document['class_id'])
                del mat_ids[0]
            if len(mat_ids) == 0:
                break
    return ground_truth_classes

def load_class_array_from_h_mat(info):
    h_mat = data.load_h_mat(info)
    return np.argmax(h_mat, axis=0)

def grab_metric_data_entry(metric_data, info, what):
    # Grab the corresponding entry from metric data
    try:
        metric_data_line = [line for line in metric_data if line['info'] == info][0]
    # If it doesn't exist create a new one
    except:
        metric_data.append({'info': info})
        metric_data_line = metric_data[-1]
    if what not in metric_data_line:
        metric_data_line[what] = {}
    return metric_data_line[what]

class DistillerBase():
    def __init__(self, info):
        self.info = info
        
    def run_distiller(self, info):
        self.topic_token_version = None
        self.topiclist = None
        self.runinfo = info.copy()
        self.run(info)   
        
    def save(self):
        if self.topiclist is None:
            nbprint('Distiller did not produce topiclist.')
            return
        
        if self.topic_token_version is None:
            nbprint('Distiller did not set "topic_token_version", discarding result.')
            return

        self.runinfo['topic_token_version'] = self.topic_token_version
        data.save_topiclist(self.topiclist, self.runinfo)
        
    def run(self, info):
        pass