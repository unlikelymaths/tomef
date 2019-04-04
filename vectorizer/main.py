import data
import config
from util import iterate
from base import nbprint

from vectorizer.helper import check_requirements, check_phrase_requirements
from vectorizer.vectorize_bow import make_term_doc_mat_count, make_term_doc_mat_tf_idf
from vectorizer.vectorize_cbow import make_cbow_mat_tf_idf, make_cbow_mat_minmaxmean, make_cbow_fv
from vectorizer.vectorize_phrase import make_phrase_mat

def count_mat(info):
    # Reset runvars
    global runvars
    runvars = None
    
    # Check if Vocab and Tokens exist
    if not check_requirements(info):
        nbprint('Skipping Vectorizer (requirements not satisfied)')
        raise BreakIteration()

def init_count_mat(info):
    global runvars
    if runvars is None:
        runvars = {}
        make_term_doc_mat_count(info, runvars)
        data.save_mat_ids(runvars['mat_ids'], info)
    
def bow(info):
    global runvars
    
    # Check if input mat exists
    if config.skip_existing and data.input_mat_exists(info):
        nbprint('Skipping Vectorizer (file exists)')
        return
    
    # Make count_mat if necessary
    init_count_mat(info)
    
    # Run Tf-Idf
    make_term_doc_mat_tf_idf(info, runvars)
    data.save_sparse_input_mat(runvars['term_doc_mat_tf_idf'], info)
   
def cbow(info):
    global runvars
    
    # Check if input mat exists
    if config.skip_existing and data.input_mat_exists(info):
        nbprint('Skipping Vectorizer (file exists)')
        return
    
    # Make count_mat if necessary
    init_count_mat(info)
    
    # Make input mat
    vector_type = info['vector_info']['type']
    if vector_type == 'TfIdf':
        make_cbow_mat_tf_idf(info, runvars)
    elif vector_type == 'MinMaxMean':
        make_cbow_mat_minmaxmean(info, runvars)
    elif vector_type == 'FV':
        make_cbow_fv(info, runvars)
    data.save_dense_input_mat(runvars['cbow_mat'], info)
    
def phrase(info):
    # Check if Documents exist
    if not check_phrase_requirements(info):
        nbprint('Skipping Vectorizer (requirements not satisfied)')
        return
    
    # Check if input mat exists
    if config.skip_existing and data.input_mat_exists(info):
        nbprint('Skipping Vectorizer (file exists)')
        return
    
    make_phrase_mat(info, runvars)
    data.save_dense_input_mat(runvars['phrase_mat'], info)

def run_vectorizer(info = None):
    nbprint('Vectorizer').push()
    global runvars
    
    if info is None:
        if config.vectorizer['run_B']:
            nbprint('BoW').push()
            runvars = {}
            iterate(['data', 'token:BC', 'vocab', 'vector:B'], [count_mat, bow])
            nbprint.pop()
        
        if config.vectorizer['run_C']:
            nbprint('cBoW').push()
            runvars = {}
            iterate(['data', 'token:C', 'vocab', 'vector:C'], [count_mat, cbow])
            nbprint.pop()
            
        if config.vectorizer['run_P']:
            nbprint('Phrase').push()
            runvars = {}
            iterate(['data', 'vector:P'], [phrase])
            nbprint.pop()
    else:
        runvars = {}
        vector_bcp, vector_id = config.split(info['vector_version'])
        if vector_bcp == 'B' or vector_bcp == 'C':
            count_mat(info)
            if vector_bcp == 'B':
                bow(info)
            else:
                cbow(info)
        else:
            phrase(info)
            
    runvars = None
    nbprint.pop()