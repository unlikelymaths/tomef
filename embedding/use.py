import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

from embedding.embedding_model import PhraseembeddingModel

class USEModel(PhraseembeddingModel):
    def __del__(self):
        if self.model_loaded:
            self.session.close()

    def _load_model(self):
        tf.logging.set_verbosity(tf.logging.ERROR)
        module_url = self.info['embedding_info']['module_url']
        self.tf_embed_module = hub.Module(module_url)
        self.session = tf.Session()
        self.session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        
    def _embed(self, messages):
        return self.session.run(self.tf_embed_module(messages))
    
    def _vector_size(self):
        return self.embed(['Test String']).shape[1]