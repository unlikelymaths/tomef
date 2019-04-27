import ipywidgets as widgets
from IPython.display import display

import config
import data
import widgetbase as wb
from base import nbprint

from vectorizer.helper import check_requirements

def w_mat_picker(info):        
    output_box = wb.DynHTML(display = False)
    nbbox = wb.nbbox(display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        nbbox.clear()
        output_box.update(wb.info_table('data:short,token:short,vocab:short,vector:short,model:short', info))
      
    w_mat_selector = wb.get_w_mat_selector(info, update_output)
    display(w_mat_selector)
    output_box.display()   
    nbbox.display()
    
    update_output()
    
def h_mat_and_bow_picker(info):
    output_box = wb.DynHTML(display = False)
    nbbox = wb.nbbox(display = False)
    second_info = {}
    info['second_info'] = second_info 
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        if clear_nbbox:
            nbbox.clear()
        output_box.update(wb.info_table('data:short,token:short,vocab:short,vector:short,model:short', info))
      
    h_mat_selector = wb.get_h_mat_selector(info, update_output)
    data_selector = wb.get_data_selector(second_info, update_output)
    token_vocab_selector = wb.get_linked_token_vocab_selector(second_info, update_output)
    count_vector_selector = wb.get_vector_selector(second_info, update_output, 'B')
    settings_box = widgets.VBox([h_mat_selector,
                                 data_selector,
                                 token_vocab_selector,
                                 count_vector_selector])
    display(settings_box)
    output_box.display()   
    nbbox.display()
    
    update_output()
    