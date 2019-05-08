from embedding.main import get_model

from tokenizer.token_util import TokenizerBase
from tokenizer.default_tokenizer import DefaultTokenizer


class W2VTokenizer(TokenizerBase):
    def initialize(self):
        self.default_tokenizer = DefaultTokenizer(
            info = {'token_info': {'numbers': 'decimal-on-one',
                                   'numbers_split': False,
                                   'links': 'keep',
                                   'lowercase': False,
                                   'ascii_only': True,
                                   'alnum_only': 'weak'}})
        
        self.embedding_model = get_model(self.info)
        self.embedding_model.load_filter()
        self.embedding_model.excluded = {}
    
    def tokenize(self, text, *args):
        tokens = self.default_tokenizer.tokenize(text)
        return self.embedding_model.filter(tokens)