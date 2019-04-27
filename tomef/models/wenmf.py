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


class WeNMF(ModelBase):
    
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
        
        # find elements in the nullspace of VTV
        if self.null is not None:
            nbprint('Finding {} elements in ker(VTV)'.format(self.num_kernel))
            self.kernelvectors = []
            for i in ProgressIterator(range(2 * self.num_kernel), print_every = 1):
                op = LinearOperator((len(vocab),len(vocab)), 
                                    matvec = lambda x: self.v_mat.transpose() @ (self.v_mat @ x))
                try:
                    w,v = eigs(op,
                               k = 1,
                               which = 'SM',
                               maxiter = 100)
                    w = np.real(w[0])
                    v = np.real(v[:,0])
                    if w < 1e-10:
                        v = v / np.sqrt(np.sum(np.square(v)))
                        self.kernelvectors.append(v)
                        if len(self.kernelvectors) >= self.num_kernel:
                            break
                except ArpackNoConvergence:
                    nbprint('eigs did not converge')
            self.v_sums =  [np.sum(v) for v in self.kernelvectors]
        
        # Initialize W and H from NMF
        nbprint('Initial NMF')
        nmf_model = NMFSklearn(self.num_topics, init='nndsvd')
        self.W = np.maximum(nmf_model.fit_transform(self.input_mat), self.eps)
        self.H = np.maximum(nmf_model.components_, self.eps)
        
    
    def _iter_w_update(self, r, wr):
        if self.null is None:
            return wr
        elif self.null == 'original':
            hr = self.Ht[:,r,None].T
            hr_normsqare = np.sum(np.square(hr))
            xhrt = self.input_mat @ hr.T
            whhrt = self.W @ (self.Ht.T @ hr.T) - self.W[:,r,None] * hr_normsqare
            for iteration in range(2):
                max_c = 0
                for n in self.kernelvectors:
                    wrhrhrt = wr[:,None] * hr_normsqare
                    sum_all = xhrt - whhrt - wrhrhrt
                    c = np.sum(n * sum_all) / hr_normsqare
                    max_c = max(c,max_c)
                    #nbprint('c={} (r={}, hr_normsqare={})'.format(c,r,hr_normsqare))
                    wr = wr + c*n
                if max_c <= self.c_threshold:
                    break
            #nbprint('last_c={}, iter={}, wr={}'.format(c, iteration, wr[:10]))
            return wr
        elif self.null == 'orthogonal':
            idcs = [i for i in range(self.W.shape[1]) if i != r]
            wnor = self.W[:,idcs]
            for iteration in range(10):
                max_c = 0
                for n in self.kernelvectors:
                    wnor_dot_n = np.sum(wnor * n[:,None], 0)
                    wnor_dor_wr = np.sum(wnor * wr[:,None], 0)
                    c = -np.sum(wnor_dot_n * wnor_dor_wr) / np.sum(np.square(wnor_dot_n))
                    max_c = max(c,max_c)
                    #nbprint('c={} (r={}) {}'.format(c,r, (wnor_dot_n * wnor_dor_wr).shape))
                    wr = wr + c*n
                    wr = wr / np.sqrt(np.sum(np.square(wr)))
                if max_c <= self.c_threshold:
                    break
            #nbprint('last_c={}, iter={}, wr={}'.formiiiiiiiat(c, iteration, wr[:10]))
            return wr
        elif self.null == 'mean':
            wr = wr / np.sqrt(np.sum(np.square(wr)))
            for iteration in range(10):
                max_c = 0
                for idx, n in enumerate(self.kernelvectors):
                    c = (1 - np.sum(wr)) / self.v_sums[idx]
                    max_c = max(c,max_c)
                    wr = wr + c*n
                if max_c <= self.c_threshold:
                    break
            #nbprint('last_c={}, iter={}, wr={}'.format(c, iteration, wr[:10]))
            return wr
            
        
    
    def _wenmf(self):
        self.errors = []
        self.Ht = normalize(self.H, axis = 0).T
    
        for iteration in ProgressIterator(range(self.max_iter), print_every = 1):
            HHT = np.dot(self.Ht.T,self.Ht)
            W_old = np.copy(self.W)
            for w in range(self.W_update_num):
                for r in range(self.num_topics):
                    hr = self.Ht[:,r]
                    idx = [i for i in range(self.num_topics) if i!=r]
                    wr = 1/HHT[r,r] * (self.input_mat @ hr - self.W[:,idx] @ HHT[idx,r])
                    wr = self._iter_w_update(r,wr)
                    wr = np.maximum(wr, self.eps).T
                    self.W[:,r] = wr
            mean_w_change = np.mean(np.abs((self.W - W_old) / W_old))
            
            VTVW = np.dot(self.v_mat.T, np.dot(self.v_mat,self.W))
            WTVTVW = np.dot(self.W.T, VTVW)
            Ht_old = np.copy(self.Ht)
            for h in range(self.H_update_num):
                for r in range(self.num_topics):
                    VTVwr = VTVW[:,r]
                    idx = [i for i in range(self.num_topics) if i!=r]
                    hr = 1/WTVTVW[r,r] * (VTVwr.T @ self.input_mat).T - self.Ht[:,idx] @ WTVTVW[idx,r]
                    hr = np.maximum(hr,self.eps)
                    self.Ht[:,r] = hr
            mean_h_change = np.mean(np.abs((self.Ht - Ht_old) / Ht_old))
            
            if self.log_error or self.print_error:
                VX = self.v_mat @ self.input_mat
                VW = self.v_mat @ self.W
                err = np.linalg.norm(VX - VW @ self.Ht.T) / np.linalg.norm(VX)
                if self.print_error:
                    nbprint('Error: {}'.format(err))
                if self.log_error:
                    self.errors.append(err)
            nbprint('mean_w_change={}, mean_h_change={} ({})'.format(mean_w_change, mean_h_change, self.threshold))        
            if iteration + 1 >= self.min_iter and mean_w_change < self.threshold and mean_h_change < self.threshold:
                nbprint('Converged after {} iterations. (threshold = {})'.format(iteration+1,self.threshold))
                break
        self.H = self.Ht.T
    
    def _run(self, info):
        self.info = info
        
        # Settings
        self.num_topics = self.info["num_topics"]
        # ALgorithm for optimizing over the nullspace
        self.null = self.info["model_info"].get('null', None)
        # Minimum number of iterations
        self.min_iter = info['model_info'].get('min_iter', 15)    
        # Maximum number of iterations
        self.max_iter = info['model_info'].get('max_iter', 100)      
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
        nbprint('WeNMFN')
        self._wenmf()
        
        self.meta = {
            'errors': self.errors
        }