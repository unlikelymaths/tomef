from sklearn.decomposition import NMF as NMFSklearn
from sklearn.cluster import KMeans as KMeansSklearn
import numpy as np

import config
import data
from base import nbprint
from models.modelbase import ModelBase
from util import ProgressIterator


class NMF(ModelBase):
    
    def _output_of(self, info):
        if config.split(info['vector_version'])[0] == 'B':
            return ['W','H']
    
    def _run(self, info):
        model = NMFSklearn(info["num_topics"], init='nndsvd')
        self.W = model.fit_transform(self.input_mat)
        self.H = model.components_
        
class ShiftNMF(ModelBase):
        
    def _output_of(self, info):
        if config.split(info['vector_version'])[0] in ['C','P']:
            return ['H']
        return None
    
    def _run(self, info):
        min_value = np.max(np.amin(self.input_mat),0)
        nonnegative_mat = self.input_mat - min_value
        model = NMFSklearn(info["num_topics"], init='nndsvd')
        model.fit_transform(nonnegative_mat)
        self.H = model.components_
        
class SemiNMF(ModelBase):
    
    def _output_of(self, info):
        if config.split(info['vector_version'])[0] in ['C','P']:
            return ['H']
        return None
    
    def plus(self, mat):
        return np.maximum(mat, 0)
    def minus(self, mat):
        return -np.minimum(mat, 0)
    
    def _run(self, info):
        # Maximum number of iterations
        self.max_iter = info['model_info'].get('max_iter', 200)      
        # If the mean of the differences between two iterates of H falls below this threshold, the algorithm stops
        self.theshold = info['model_info'].get('eps', 1e-4)   
        
        # Check if kmeans exists
        kmeans_info = info.copy()
        kmeans_info['model_name'] = 'kmeans'
        if data.c_vec_exists(kmeans_info):
            nbprint('Loading k-means for initial H')
            c = data.load_c_vec(kmeans_info)
        else:
            nbprint('Running k-means for initial H')
            model = KMeansSklearn(n_clusters=info["num_topics"], 
                                  init='k-means++', 
                                  random_state=42,
                                  verbose=0)
            c = model.fit_predict(self.input_mat.transpose())
        
        # Construct H from c
        self.H = np.full((info["num_topics"],self.input_mat.shape[1]), 0.2)
        for doc, topic in enumerate(c):
            self.H[topic, doc] += 1
        
        # Iterate updates
        nbprint('Running updates')
        for iteration in ProgressIterator(range(self.max_iter), print_every = 1):
            # Update W
            HHT = self.H @ self.H.T
            try:
                HHTinv = np.linalg.inv(HHT)
            except LinAlgError:
                HHTinv = np.linalg.pinv(HHT)
            W = self.input_mat @ self.H.T @ HHTinv
            
            # Update H
            XTW = self.input_mat.T @ W
            WTW = W.T @ W
            frac = ((self.plus(XTW)  + self.H.T @ self.minus(WTW)) / 
                    (self.minus(XTW) + self.H.T @ self.plus(WTW)))
            Hpre = self.H.copy()
            self.H = (self.H.T * np.sqrt(frac)).T
            
            mean_h_change = np.mean(np.abs(self.H - Hpre))
            if mean_h_change < self.theshold:
                nbprint('Converged after {} iterations. (Threshold = {})'.format(iteration+1, self.theshold))
                return
        nbprint('Did not converge after {} iterations with last change {} for threshold {}'.format(self.max_iter, mean_h_change, self.theshold))