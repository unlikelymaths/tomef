from gensim.models.ldamodel import LdaModel
#from gensim.models.ldamulticore import LdaMulticore as LdaModel
from gensim.matutils import Sparse2Corpus
import numpy as np

import config
import data
from base import nbprint
from models.modelbase import ModelBase


class LDA(ModelBase):
    
    def _output_of(self, info):
        return ['W','H']
    
    def _run(self, info):
        nbprint('Running LDA')
        vocab = data.load_vocab(info)
        id2word = {e['id']: e['token'] for e in vocab}
        corpus = Sparse2Corpus(self.input_mat)
        lda = LdaModel(corpus, id2word=id2word, num_topics=info["num_topics"])
        self.W = lda.get_topics().T
        self.H = np.zeros((info["num_topics"],self.input_mat.shape[1]))
        for idx,doc in enumerate(corpus):
            weights = lda[doc]
            for topic, value in weights:
                self.H[topic,idx] = value
        