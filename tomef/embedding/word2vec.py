import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import KeyedVectors
from difflib import get_close_matches

from collections import defaultdict

from base import data
from interface import nbprint, ProgressIterator

from embedding.embedding_model import WordembeddingModel
from embedding.common import EmbeddingError, OOVException

exists_token = "###WORD_EXISTS###"

class Word2VecFilter():
    def __init__(self, vocab, track_exclusion):
        self.track_exclusion = track_exclusion
        self.build_lookup(vocab)
        self.reset_excluded()
        
    def reset_excluded(self):
        self.excluded = defaultdict(lambda: 0)
        
    def build_lookup(self, vocab):
        self.lookup = {}
        for token in ProgressIterator(vocab, print_every=10000):
            words = token.replace("_"," ").split()
            if len(words) == 0:
                continue
            current_lookup = self.lookup
            for word in words:
                lower_word = word.lower()
                if not lower_word in current_lookup:
                    current_lookup[lower_word] = {}
                current_lookup = current_lookup[lower_word]
            if exists_token in current_lookup:
                current_lookup[exists_token].append(token)
            else:
                current_lookup[exists_token] = [token,]
    
    def filter(self, all_tokens):
        idx = 0
        tokens = []
        while idx < len(all_tokens):
            phrase = []
            valid = 0
            currentidx = idx
            current_lookup = self.lookup
            phrase_list = None
            while currentidx < len(all_tokens) and all_tokens[currentidx].lower() in current_lookup:
                phrase.append(all_tokens[currentidx])
                current_lookup = current_lookup[all_tokens[currentidx].lower()]
                if exists_token in current_lookup:
                    valid = len(phrase)
                    phrase_list = current_lookup[exists_token]
                currentidx = currentidx + 1
            if valid > 0:
                phrase = "_".join(phrase[:valid])
                if phrase in phrase_list:
                    tokens.append(phrase)
                else:
                    match = get_close_matches(phrase, phrase_list, n=1, cutoff=0)[0]
                    if match:
                        tokens.append(match)
                    else:
                        print("WARNING: No match found in phrase_list. This should never happen...")
            elif self.track_exclusion:
                self.excluded[all_tokens[idx]] += 1
            idx += max(valid,1)
        return tokens

class FastWord2VecFilter(Word2VecFilter):
    def build_lookup(self, vocab):
        self.lookup = {}
        for token in ProgressIterator(vocab, print_every=10000):
            words = token.split('_')
            if '' in words or len(words) == 0:
                continue
            current_lookup = self.lookup
            for word in words:
                lower_word = word.lower()
                if not lower_word in current_lookup:
                    current_lookup[lower_word] = {}
                current_lookup = current_lookup[lower_word]
            if exists_token not in current_lookup:
                current_lookup[exists_token] = token
    
    def filter(self, all_tokens):
        idx = 0
        tokens = []
        while idx < len(all_tokens):
            phrase = None
            currentidx = idx
            valid = 0
            current_lookup = self.lookup
            while currentidx < len(all_tokens) and all_tokens[currentidx].lower() in current_lookup:
                current_lookup = current_lookup[all_tokens[currentidx].lower()]
                if exists_token in current_lookup:
                    phrase = current_lookup[exists_token]
                    valid = valid + 1
                currentidx = currentidx + 1
            if phrase is not None:
                tokens.append(phrase)
            elif self.track_exclusion:
                self.excluded[all_tokens[idx]] += 1
            idx += max(valid,1)
        return tokens
    

class Word2vecModel(WordembeddingModel):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._filter = None
        self.track_exclusion = self.info.get('track_exclusion', False)
        self.fast_filter = self.info.get('fast_filter', True)
    
    def _load_model(self):
        if not data.embedding_file_exists(self.info):
            raise EmbeddingError(self.info, 'File "{}" does not exist.'.format(embedding_filename))
        return KeyedVectors.load_word2vec_format(
            data.embedding_filename(self.info), 
            binary=True)
    
    def _load_vector_size(self):
        return self.model.wv.vector_size
    
    def _load_embedding_function(self):
        wv = self.model.wv
        def embedding_function(token):
            try:
                return wv[token]
            except:
                raise OOVException('Word2vecModel',token)
        return embedding_function
    
    def _load_vocab(self):
        return [str(token) for token in self.model.vocab]

    @property
    def filter(self):
        if self._filter is None:
            nbprint('Loading word2vec filter...')
            if self.fast_filter:
                self._filter = FastWord2VecFilter(self.vocab, self.track_exclusion)
            else:
                self._filter = Word2VecFilter(self.vocab, self.track_exclusion)
            nbprint.clear_last()
        return self._filter