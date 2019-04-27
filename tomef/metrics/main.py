import time
from collections import defaultdict

import data
import config
from util import ProgressIterator
from base import nbprint

from metrics.helper import load_ground_truth_classes, load_class_array_from_h_mat, grab_metric_data_entry, load_metric_fcts



def clustering_metrics():
    metric_fcts = load_metric_fcts('clustering')
    clustering_data = data.load_metric_data('clustering')
    
    # First everything by taking the column wise maximum as cluster idx
    nbprint('H Matrix').push()
    h_mat_infos = data.get_all_h_mat_infos(labeled_only = True)
    for info in ProgressIterator(h_mat_infos, print_every=1):
        # Grab the corresponding entry from clustering data
        metric_data_entry = grab_metric_data_entry(clustering_data, info)
        
        # Iterate all metric functions and store result in entry
        for metric_id, metric_fct in metric_fcts.items():
            # Skip metric if it already exists:
            if metric_id in metric_data_entry:
                continue
                
            # Compute the metric
            labels_true = load_ground_truth_classes(info)
            labels_pred = load_class_array_from_h_mat(info)
            metric_data_entry[metric_id] = metric_fct(labels_true, labels_pred)
    
            # Save everything in between
            data.save_metric_data(clustering_data, 'clustering')
            
    # Taking indices directly from c
    nbprint.pop()('C Vector').push()
    c_vec_infos = data.get_all_c_vec_infos(labeled_only = True)
    for info in ProgressIterator(c_vec_infos, print_every=1):
        # Grab the corresponding entry from clustering data
        metric_data_entry = grab_metric_data_entry(clustering_data, info)
        
        # Iterate all metric functions and store result in entry
        for metric_id, metric_fct in metric_fcts.items():
            # Skip metric if it already exists:
            if metric_id in metric_data_entry:
                continue
                
            # Compute the metric
            labels_true = load_ground_truth_classes(info)
            labels_pred = data.load_c_vec(info)
            metric_data_entry[metric_id] = metric_fct(labels_true, labels_pred)
    
            # Save everything in between
            data.save_metric_data(clustering_data, 'clustering')
    nbprint.pop()
    
    
    
def classification_metrics():
    metric_fcts = load_metric_fcts('classification')
    classification_data = data.load_metric_data('classification')
    
    h_mat_infos = data.get_all_h_mat_infos(labeled_only = True)
    for info in ProgressIterator(h_mat_infos, print_every=1):
        nbprint(info)
        # Grab the corresponding entry from clustering data
        metric_data_entry = grab_metric_data_entry(classification_data, info)
        
        # Iterate all metric functions and store result in entry
        for metric_id, metric_fct in metric_fcts.items():
            # Skip metric if it already exists:
            if metric_id in metric_data_entry:
                continue
                
            # Compute the metric
            labels_true = load_ground_truth_classes(info)
            h_mat = data.load_h_mat(info)
            metric_data_entry[metric_id] = metric_fct(labels_true, h_mat)
    
            # Save everything in between
            data.save_metric_data(classification_data, 'classification')
    


# We load all topiclists from all infos in the batch and
# group them into a single topiclist to pass to the coherence function fct.
def coherence_metric_batch(token_version, batch, metric_id, fct):
    if token_version != 'Cw2v':
        return
    
    coherence_data = data.load_metric_data('coherence')
    coherence_data_entries = []
    topiclist_slices = []
    batch_topiclist = []
    for info in batch:
        coherence_data_entry = grab_metric_data_entry(coherence_data, info)
        if fct in coherence_data_entry:
            continue
        topiclist = data.load_topiclist(info)
        topiclist = [topic[:info['num_tokens']] for topic in topiclist]
        start_idx = len(batch_topiclist)
        end_idx = start_idx + len(topiclist)
        
        coherence_data_entries.append(coherence_data_entry)
        batch_topiclist = batch_topiclist + topiclist
        topiclist_slices.append(slice(start_idx, end_idx))
    
    coherences = fct(batch_topiclist, token_version)
    
    for coherence_data_entry, topiclist_slice in zip(coherence_data_entries, topiclist_slices):
        coherence_data_entry[metric_id] = coherences[topiclist_slice]
        
    data.save_metric_data(coherence_data, 'coherence')
    
def coherence_metrics():
    metric_fcts = load_metric_fcts('coherence')
    if len(metric_fcts) == 0:
        nbprint('No metrics active.')
        return
    
    topiclist_infos = data.get_all_topiclist_infos()
    if len(topiclist_infos) == 0:
        nbprint('No topics found.')
        return
    
    # Group them into batches based on topic_version and add num_tokens
    topiclist_info_batches = defaultdict(list)
    for info in topiclist_infos:
        for num_tokens in config.metrics['num_tokens']:
            extended_info = info.copy()
            extended_info['num_tokens'] = num_tokens
            if 'second_info' in info:
                token_version = info['second_info']['token_version']
            else:
                token_version = info['token_version']
            topiclist_info_batches[token_version].append(extended_info)
        
    for token_version, batch in topiclist_info_batches.items():
        nbprint('Batch {}'.format(token_version)).push()
        for metric_id, fct in metric_fcts.items():
            start = time.time()
            nbprint('Metric: {}'.format(config.metrics['coherence'][metric_id]['name'])).push()
            coherence_metric_batch(token_version, batch, metric_id, fct)
            end = time.time()
            nbprint('Runtime: {} minutes'.format((end - start)/60)).pop()
        nbprint.pop()
        
def similarity_metrics():
    similarity_data = data.load_metric_data('similarity')
    metric_fcts = load_metric_fcts('similarity')
    if len(metric_fcts) == 0:
        nbprint('No metrics active.')
        return
    
    topiclist_infos = data.get_all_topiclist_infos()
    if len(topiclist_infos) == 0:
        nbprint('No topics found.')
        return
    
    topiclist = None
    for info in topiclist_infos:
        for num_tokens in config.metrics['num_tokens']:
            extended_info = info.copy()
            extended_info['num_tokens'] = num_tokens
            # Grab the corresponding entry from clustering data
            metric_data_entry = grab_metric_data_entry(similarity_data, extended_info)
            
            # Iterate all metric functions and store result in entry
            for metric_id, metric_fct in metric_fcts.items():
                # Skip metric if it already exists:
                if metric_id in metric_data_entry:
                    continue
                
                # Load data if neccessary
                if topiclist is None:
                    topiclist = data.load_topiclist(info)
                    
                # Compute the metric
                shortened_topiclist = [topic[:num_tokens] for topic in topiclist]
                metric_data_entry[metric_id] = metric_fct(shortened_topiclist)
        
                # Save everything in between
                data.save_metric_data(similarity_data, 'similarity')
        topiclist = None
        
def run_model_metrics():
    nbprint('Model Metrics').push()
    
    nbprint('Clustering').push()
    clustering_metrics()
    nbprint.pop()
    
    nbprint('Classification').push()
    classification_metrics()
    nbprint.pop()
    
    nbprint.pop()
    
def run_topic_metrics():
    nbprint('Topic Metrics').push()
    
    nbprint('Coherence').push()
    coherence_metrics()
    nbprint.pop()
    
    nbprint('similarity').push()
    similarity_metrics()
    nbprint.pop()
    
    nbprint.pop()
    