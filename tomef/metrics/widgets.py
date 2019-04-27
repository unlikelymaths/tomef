import ipywidgets as widgets
from IPython.display import display

import config
import data
import widgetbase as wb
from base import nbprint

def h_mat_picker(info):        
    output_box = wb.DynHTML(display = False)
    nbbox = wb.nbbox(display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        nbbox.clear()
        output_box.update(wb.info_table('data:short,token:short,vocab:short,vector:short,model:short', info))
      
    h_mat_selector = wb.get_h_mat_selector(info, update_output, labeled_only = True)
    display(h_mat_selector)
    output_box.display()   
    nbbox.display()
    
    update_output()
    
def topiclist_picker(info):        
    output_box = wb.DynHTML(display = False)
    nbbox = wb.nbbox(display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        nbbox.clear()
        output_box.update(wb.info_table('data:short,token:short,vocab:short,vector:short,model:short', info))
      
    topiclist_selector = wb.get_topiclist_selector(info, update_output)
    display(topiclist_selector)
    output_box.display()   
    nbbox.display()
    
    update_output()