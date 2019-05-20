from base import data
from interface import nbprint

class EmbeddingModel():
    current_model = None
    
    def __init__(self, info):
        EmbeddingModel.current_model = self
        self._model = None
        self._vector_size = None
        self._embedding_function = None
        self.info = info
    
    @property
    def model(self):
        if self._model is None:
            nbprint('Loading embedding model...')
            self._model = self._load_model()
            nbprint.clear_last()
        return self._model
    
    @property
    def vector_size(self):
        if self._vector_size is None:
            self._vector_size = self._load_vector_size()
        return self._vector_size
    
    @property
    def embedding_function(self):
        if self._embedding_function is None:
            self._embedding_function = self._load_embedding_function()
        return self._embedding_function
    
    def clear():
        EmbeddingModel.current_model = None
                      
    def current_model_is_same(typename, info):
        return (isinstance(EmbeddingModel.current_model, typename) and
                EmbeddingModel.current_model.info.get('embedding_info') == info.get('embedding_info'))


class WordembeddingModel(EmbeddingModel):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._vocab = None
        
    @property
    def vocab(self):
        if self._vocab is None:
            nbprint('Loading embedding vocab...')
            if data.embedding_meta_exists('vocab', self.info):
                self._vocab = data.load_embedding_meta('vocab', self.info)
            else:
                self._vocab = self._load_vocab()
                data.save_embedding_meta(self._vocab, 'vocab', self.info)
            nbprint.clear_last()
        return self._vocab
                
class PhraseembeddingModel(EmbeddingModel):
    pass