from base import data, config, iterator, util
from interface import nbprint, ProgressIterator

from embedding.common import EmbeddingError

from tokenizer.common import join_tokens, get_tokenizer
from tokenizer.util import check_requirements
    
def tokenize(info):    
    if not check_requirements(info):
        nbprint('Skipping Tokenizer (requirements not satisfied)')
        return
    if config.skip_existing and data.tokenized_document_exists(info):
        nbprint('Skipping Tokenizer (file exists)')
        return
    
    try:
        current_tokenizer = get_tokenizer(info)
    
        with util.ModuleTimer('tokenizer', info):
            with data.document_reader(info) as documents:
                with data.tokenized_document_writer(info) as tokenized_documents:
                    for document in ProgressIterator(documents, "Documents"):
                        tokens = current_tokenizer.tokenize(document['text'])
                        token_str = join_tokens(tokens)
                        tokenized_document = {'id': document['id'],
                            'tokens': token_str, 
                            'class_id': document['class_id']}
                        tokenized_documents.write(tokenized_document)
                    
    except EmbeddingError as err:
        nbprint(err)
        data.clear_file(data.tokenized_document_filename(info))
        return
    
    nbprint('Tokenizer: success')
    
def run_tokenizer(info = None):
    nbprint('Tokenizer').push()
    
    if info is None:
        iterator.iterate(['token:BC', 'data'], tokenize)
    else:
        tokenize(info)
            
    nbprint.pop()