from base import data, config
from interface import nbprint

from vocab.main import run_vocab
from tokenizer.main import run_tokenizer
from importer.main import run_importer

def check_requirements(info):
    bcp, id = config.split(info['vector_version'])
    if bcp == 'B' or bcp == 'C':
        # Check if vocab file exists
        if not data.vocab_exists(info):
            # Run Vocab
            nbprint('Vocab missing.')
            run_vocab(info)
            # Check if it was successfull
            if not data.vocab_exists(info):
                return False
        # Check if tokens file exists
        if not data.tokenized_document_exists(info):
            # Run Tokenizer
            nbprint('Tokens missing.')
            run_tokenizer(info)
            # Check if it was successfull
            if not data.tokenized_document_exists(info):
                return False
    else:
        # Check if documents file exists
        if not data.documents_exists(info):
            # Run Importer
            nbprint('Documents missing.')
            run_importer(info)
            # Check if it was successfull
            if not data.documents_exists(info):
                return False
    return True