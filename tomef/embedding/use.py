from collections import namedtuple
import os
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

import config
from embedding.embedding_model import PhraseembeddingModel

USEModelData = namedtuple('USEModelData', ['module', 'session'])

class USEModel(PhraseembeddingModel):
    def __del__(self):
        if self.model is not None:
            self.model.session.close()

    def _load_model(self):
        os.environ['TFHUB_CACHE_DIR'] = config.paths['embedding']
        tf.logging.set_verbosity(tf.logging.ERROR)
        module_url = self.info['embedding_info']['module_url']
        module = hub.Module(module_url)
        session = tf.Session()
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        return USEModelData(module, session)
        
    def _load_vector_size(self):
        return self.embedding_function(['Test String']).shape[0]
    
    def _load_embedding_function(self):
        module = self.model.module
        session = self.model.session
        def embedding_function(texts):
            return session.run(module(texts)).T
        return embedding_function
    