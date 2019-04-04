import numpy as np
from sklearn.decomposition import NMF as NMFSklearn
from sklearn.preprocessing import normalize
from scipy.sparse.linalg import eigs, LinearOperator, ArpackNoConvergence

import config
import data
from base import nbprint
from util import ProgressIterator

from embedding.main import get_model

from models.modelbase import ModelBase


class WeNMFpl(ModelBase):
    
    def _output_of(self, info):
        if config.split(info['vector_version'])[0] == 'B' and config.split(info['token_version'])[0] == 'C':
            return ['W','H']
    
    def _pre_algorithm(self):
        # Load the embeddings
        embedding_model = get_model(self.info)
        embeddings = embedding_model.get_embeddings()
        vector_size = embedding_model.vector_size()
        
        # Load the vocab
        vocab = data.load_vocab_list(self.info)
        
        # construct V
        v_shape = (vector_size, len(vocab))
        self.v_mat = np.zeros(v_shape)
        for idx, token in enumerate(vocab):
            try:
                self.v_mat[:,idx] = embeddings[token]
            except:
                pass
        
        # compute norm of VTV
        nbprint('Computing norm of VTV')
        op = LinearOperator((len(vocab),len(vocab)), 
                            matvec = lambda x: self.v_mat.transpose() @ (self.v_mat @ x))
        w,v = eigs(op,
                   k = 1,
                   which = 'LM',
                   maxiter = 100)
        self.lambda_v = np.real(w[0])
        
        # Initialize W and H from NMF
        nbprint('Initial NMF')
        nmf_model = NMFSklearn(self.num_topics, init='nndsvd')
        self.W = np.maximum(nmf_model.fit_transform(self.input_mat), self.eps)
        self.H = np.maximum(nmf_model.components_, self.eps)
    
    def _check_error(self):
        if self.log_error or self.print_error:
            VX = self.v_mat @ self.input_mat
            VW = self.v_mat @ self.W
            err = np.linalg.norm(VX - VW @ self.H) / np.linalg.norm(VX)
            if self.print_error:
                nbprint('Error: {}'.format(err))
            if self.log_error:
                self.errors.append(err)
        
    
    def _wenmf(self):
        self.errors = []
        
        self.Wp1 = self.W.copy()
        self.Wp2 = self.W.copy()
        self.Hp1 = self.H.copy()
        self.Hp2 = self.H.copy()
        
        self._check_error()
        for iteration in ProgressIterator(range(self.max_iter), print_every = 1):
            W_hat = self.Wp1 + self.omega * (self.Wp1 - self.Wp2)
            H_hat = self.Hp1 + self.omega * (self.Hp1 - self.Hp2)
            
            for r in range(self.num_topics):
                idx = [i for i in range(self.num_topics) if i!=r]
                g = -2 * (self.v_mat.T @ (self.v_mat @ 
                            ((self.input_mat @ self.H[None,r,:].T) - 
                             (self.W[:,idx] @ (self.H[idx,:] @ self.H[None,r,:].T) - 
                              W_hat[:,r,None] @ (self.H[None,r,:] @ self.H[None,r,:].T)))))
                L = 2 * np.abs(self.H[None,r,:] @ self.H[None,r,:].T) * self.lambda_v
                self.W[:,r,None] = np.maximum(W_hat[:,r,None] - g / L, self.eps)
            mean_w_change = np.mean(np.abs((self.W - self.Wp1) / self.Wp1))
            
            for r in range(self.num_topics):
                tmp = ((self.v_mat @ self.W[:,r,None]).T @ self.v_mat)
                g = -2 * (tmp @ self.input_mat - 
                          ((tmp @ self.W) @ self.H - (tmp @ self.W[:,r,None]) @ self.H[None,r,:]) -
                          (tmp @ self.W[:,r,None]) @ H_hat[None,r,:])
                L = 2 * np.sum(np.square(self.v_mat @ self.W[:,r,None]))
                self.H[None,r,:] = np.maximum(H_hat[None,r,:] - g / L, self.eps)
            mean_h_change = np.mean(np.abs((self.H - self.Hp1) / self.Hp1))
            
            self.Wp2 = self.Wp1
            self.Hp2 = self.Hp1
            self.Wp1 = self.W
            self.Hp1 = self.H
            
            self._check_error()
            
            nbprint('mean_w_change={}, mean_h_change={} (threshold = {})'.format(mean_w_change, mean_h_change, self.threshold))        
            if iteration + 1 >= self.min_iter and mean_w_change < self.threshold and mean_h_change < self.threshold:
                nbprint('Converged after {} iterations. (threshold = {})'.format(iteration+1,self.threshold))
                break
            
        #self.H = self.Ht.T
    
    def _run(self, info):
        self.info = info
        
        # Settings
        self.num_topics = self.info["num_topics"]
        # Minimum number of iterations
        self.min_iter = info['model_info'].get('min_iter', 1)    
        # Maximum number of iterations
        self.max_iter = info['model_info'].get('max_iter', 20)      
        
        self.omega = 0.5
        
        
        # Mimum value of W and H entries, small positive value for stability
        self.eps = info['model_info'].get('eps', 1e-16)   
        # How often does W get updated each iteration
        self.W_update_num = info['model_info'].get('W_update_num', 2) 
        # How often does H get updated each iteration
        self.H_update_num = info['model_info'].get('H_update_num', 1)   
        # If the mean of the relative differences between two iterates falls below this threshold, the algorithm stops
        self.threshold = info['model_info'].get('threshold', 1e-3)      
        # If all c values are below c_threshold in one iteration, the iterations stop (original NMF)
        self.c_threshold = info['model_info'].get('c_threshold', 1e-8)   
        # Kernel elements used for nullspace updates
        self.num_kernel = info['model_info'].get('num_kernel', 20)   
        # Compute and log error after each iteration
        self.log_error = info['model_info'].get('log_error', False)     
        # Compute and print error after each iteration
        self.print_error = info['model_info'].get('print_error', False)     
        
        self._pre_algorithm()
        nbprint('WeNMFpl')
        self._wenmf()
        
        self.meta = {
            'errors': self.errors
        }