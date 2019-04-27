from sklearn.cluster import KMeans as KMeansSklearn
import skfuzzy as fuzz
import numpy as np

import config
from base import nbprint
from models.modelbase import ModelBase


class KMeans(ModelBase):
    
    def _output_of(self, info):
        return ['c']
    
    def _run(self, info):
        nbprint('Running k-means')
        model = KMeansSklearn(n_clusters=info["num_topics"], 
                              init='k-means++', 
                              random_state=42,
                              verbose=0)
        self.c = model.fit_predict(self.input_mat.transpose())
        
        
class CMeans(ModelBase):
    
    def _output_of(self, info):
        return ['H']
    
    def _run(self, info):
        nbprint('Running c-means')
        cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
            self.input_mat, info["num_topics"], 1.1, error=0.0005, maxiter=100, init=None)
        self.H = u