from base import data
from interface import nbprint

from tokenizer.main import run_tokenizer

def check_requirements(info):
    # Check if tokens file exists
    if not data.tokenized_document_exists(info):
        # Run Tokenizer
        nbprint('Tokens missing.')
        run_tokenizer(info)
        # Check if it was successfull
        return data.tokenized_document_exists(info)
    return True
    
    
class VocabItem:
    def __init__(self, token, total = 0, document = 0):
        self.token = token
        self.total = total
        self.document = document
    def increase_total(self, count = 1):
        self.total += count
    def increase_document(self, count = 1):
        self.document += count
    def to_dict(self, id):
        return {'id': id, 
                'token': self.token, 
                'total': self.total, 
                'document': self.document}
        
class VocabBuilder:
    def __init__(self, info):
        self.info = info

    def build_vocab(self):
        self.counts = []
    
    def get_vocab(self):
        return [vi.to_dict(id) for id, vi in enumerate(self.counts)]