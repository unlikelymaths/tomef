import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import KeyedVectors
from operator import itemgetter
from difflib import get_close_matches
from os.path import isfile

import data
from util import ProgressIterator

from embedding.embedding_model import WordembeddingModel
from embedding.common import EmbeddingError

exists_token = "###WORD_EXISTS###"

class Word2vecModel(WordembeddingModel):
    def _load_model(self):
        embedding_filename = data.embedding_filename(self.info)
        if not isfile(embedding_filename):
            raise EmbeddingError(self.info, 'File "{}" does not exist.'.format(embedding_filename))
        self.model_data = KeyedVectors.load_word2vec_format(
            embedding_filename, binary=True)
    
    def _load_vocab(self):
        return [str(token) for token in self.model_data.vocab]

    def _load_filter(self):
        self.lookup = {}
        vocab = self.vocab()
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
        
    def _get_embeddings(self):
        return self.model_data.wv
    
    def _vector_size(self):
        return self.model_data.wv.vector_size
    
    def _filter(self, all_tokens):
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
            else:
                #short_word = all_tokens[idx].lower().split("'")[0]
                #if short_word in current_lookup:
                #    tokens.append(short_word)
                #else:
                try:
                    self.excluded[all_tokens[idx]] += 1
                except:
                    self.excluded[all_tokens[idx]] = 1

            idx += max(valid,1)
        
        return tokens
        
        