import matplotlib.pyplot as plt
from IPython import get_ipython
from scipy import sparse
import numpy as np

from interface import nbprint

def sort_matrix(matrix):
    new_matrix = np.reshape(matrix[:,0], (-1,1))
    matrix = np.delete(matrix, [0], 1)
    running_avg = new_matrix
    
    while matrix.shape[1] > 0:
        similarities = np.sum(np.square(running_avg - matrix),0)
        min_idx = np.argmin(similarities)
        column = np.reshape(matrix[:,min_idx], (-1,1))
        old_weigth = 0.8
        running_avg = old_weigth * running_avg + (1 - old_weigth) * column
        new_matrix = np.hstack((new_matrix,column))
        matrix = np.delete(matrix, [min_idx], 1)
        
    return new_matrix
    

def plot_matrix(matrix):
    ipython = get_ipython()
    ipython.magic("matplotlib inline")
    ipython.magic("config InlineBackend.figure_format = 'svg'")
    fig=plt.figure(figsize=(15, 15))
    num_words,num_docs = matrix.shape
    try:
        matrix = matrix.todense()
    except: pass
    matrix = sort_matrix(matrix)
    im = plt.imshow(matrix, extent=[0, num_docs, num_words, 0])
    plt.colorbar(im,fraction=0.015, pad=0.04)
    plt.show()