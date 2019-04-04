import numpy as np

import config
import data
from base import nbprint
from util import import_fct
from util import ProgressIterator

def load_metric_fcts(which):
    metric_fcts = {}
    for id, info in config.metrics[which].items():
        if info['run']:
            metric_fcts[id] = import_fct('metrics', info['mod'], info['fct'])
    return metric_fcts

def load_ground_truth_classes(info):
    if config.split(info['vector_version'])[0] == 'P':
        with data.document_reader(info) as documents:
            _labels_true = [document['class_id'] for document in documents]
    else:
        mat_ids = data.load_mat_ids(info)
        _labels_true = [0] * len(mat_ids)
        idx = 0
        with data.document_reader(info) as documents:
            for document in documents:
                if mat_ids[idx] == document['id']:
                    _labels_true[idx] = document['class_id']
                    idx = idx + 1
                if idx >= len(_labels_true):
                    break
    return _labels_true

def load_class_array_from_h_mat(info):
    h_mat = data.load_h_mat(info)
    return np.argmax(h_mat, axis=0)

def grab_metric_data_entry(metric_data, info):
    # Grab the corresponding entry from metric data
    try:
        metric_data_line = [line for line in metric_data if line['info'] == info][0]
    # If it doesn't exist create a new one
    except:
        metric_data_line = {'info': info, 'data': {}}
        metric_data.append(metric_data_line)
    return metric_data_line['data']