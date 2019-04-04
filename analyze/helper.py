import numpy as np

import config

def get_bins(metric_name, num_bins = 20):
    if metric_name == 'ari':
        return np.linspace(-0.25, 1, num_bins)
    elif metric_name == 'nmi':
        return np.linspace(0, 1, 20)
    elif metric_name == 'svm_5fold_micro_f1':
        return np.linspace(0, 1, 20)
    elif metric_name == 'umass_wiki':
        return np.linspace(-12, 0, 20)
    elif metric_name == 'mean_pairwise_jaccard':
        return np.linspace(0, 1, 20)

def get_category(metric_name):
    if metric_name == 'ari':
        return 'clustering'
    elif metric_name == 'nmi':
        return 'clustering'
    elif metric_name == 'svm_5fold_micro_f1':
        return 'classification'
    elif metric_name == 'umass_wiki':
        return 'coherence'
    elif metric_name == 'mean_pairwise_jaccard':
        return 'similarity'
    
def metric_fct(value):
    if isinstance(value, list):
        value = sum(value) / len(value)
    if np.isnan(value):
        return -np.inf
    return value
        