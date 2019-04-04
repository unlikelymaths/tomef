from operator import itemgetter

import data
from base import nbprint

class EmbeddingModel():
    _current_model = None
    
    def __init__(self, info):
        EmbeddingModel._current_model = self
        self.model_loaded = False
        self.info = info
    
    def load_model(self):
        if not self.model_loaded:
            nbprint('Loading embedding model...')
            self._load_model()
            nbprint.clear_last()
            self.model_loaded = True
    
    def vector_size(self):
        self.load_model()
        return self._vector_size()
    
    def clear():
        EmbeddingModel._current_model = None
              
    def current_model():
        return EmbeddingModel._current_model
        
    def current_model_is_same(typename, info):
        return (isinstance(EmbeddingModel._current_model, typename) and
                EmbeddingModel._current_model.info.get('embedding_info') == info.get('embedding_info'))
                
class WordembeddingModel(EmbeddingModel):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.vocab_loaded = False
        self.filter_loaded = False
        self.excluded = {}
    
    def load_vocab(self):
        if not self.vocab_loaded:
            nbprint('Loading embedding vocab...')
            if data.embedding_vocab_exists(self.info):
                self._vocab = data.load_embedding_vocab(self.info)
            else:
                self.load_model()
                self._vocab = self._load_vocab()
                data.save_embedding_vocab(self._vocab, self.info)
            nbprint.clear_last()
            self.vocab_loaded = True
            
    def get_excluded(self, num = 1000):
        excluded = list(self.excluded.items())
        excluded.sort(key=itemgetter(1), reverse=True)
        return excluded[:num]
    
    def vocab(self):
        self.load_vocab()
        return self._vocab
    
    def get_embeddings(self):
        self.load_model()
        return self._get_embeddings()
        
    def load_filter(self):
        if not self.filter_loaded:
            nbprint('Loading embedding filter...')
            self._load_filter()
            nbprint.clear_last()
            self.filter_loaded = True
    
    def filter(self, tokens):
        self.load_filter()
        return self._filter(tokens)
        
class PhraseembeddingModel(EmbeddingModel):
    def embed(self, messages):
        self.load_model()
        return self._embed(messages)