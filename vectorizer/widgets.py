import ipywidgets as widgets
from IPython.display import display

import config
import data
import widgetbase as wb
from base import nbprint

from vectorizer.helper import check_requirements

def vector_app():
    info = {}
    output_box = wb.DynHTML(display = False)
    nbbox = wb.nbbox(display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        if clear_nbbox:
            nbbox.clear()
        output_box.update(wb.info_table('data:short,token:long,vocab:short,vector:long', info))
      
    def on_run_button_clicked(b):
        nbbox.make_current()
        nbbox.clear()
        try:
            check_requirements(info)
            from vectorizer.main import run_vectorizer
            run_vectorizer(info)
        except:
            nbprint.print_traceback()
        update_output(False)
        
    data_selector = wb.get_data_selector(info, update_output)
    token_vocab_selector = wb.get_linked_token_vocab_selector(info, update_output)
    token_selector = wb.get_token_selector(info, update_output, 'C')
    vocab_selector = wb.get_vocab_selector(info, update_output, 'C')
    run_button = widgets.Button(description="Run All")
        
    def vector_changed():
        vector_bcp, vector_id = config.split(info['vector_version'])
        if vector_bcp == 'B':
            token_vocab_selector.layout.visibility = 'visible'
            token_selector.layout.visibility = 'hidden'
            vocab_selector.layout.visibility = 'hidden'
        elif vector_bcp == 'C':
            token_vocab_selector.layout.visibility = 'hidden'
            token_selector.layout.visibility = 'visible'
            vocab_selector.layout.visibility = 'visible'
        elif vector_bcp == 'P':
            token_vocab_selector.layout.visibility = 'hidden'
            token_selector.layout.visibility = 'hidden'
            vocab_selector.layout.visibility = 'hidden'
        update_output(False)
    vector_selector = wb.get_vector_selector(info, vector_changed, 'BCP')
    
    run_button.on_click(on_run_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 vector_selector,
                                 token_vocab_selector,
                                 token_selector,
                                 vocab_selector,
                                 run_button])
    
    display(settings_box)
    output_box.display()
    nbbox.display()
    
    vector_changed()

def bow_vector_picker(info):        
    output_box = wb.DynHTML(display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    nbbox = wb.nbbox(display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        if clear_nbbox:
            nbbox.clear()
        run_requirements_button.disabled = data.vocab_exists(info)
        output_box.update(wb.info_table('data:short,token:short,vocab:short,vector:long', info))
      
    def on_run_requirements_button_clicked(b):
        nbbox.make_current()
        nbbox.clear()
        try:
            check_requirements(info)
        except:
            nbprint.print_traceback()
        update_output(False)
        
    data_selector = wb.get_data_selector(info, update_output)
    token_vocab_selector = wb.get_linked_token_vocab_selector(info, update_output)
    count_vector_selector = wb.get_vector_selector(info, update_output, 'B')
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 token_vocab_selector,
                                 count_vector_selector,
                                 run_requirements_button])
    
    display(settings_box)
    output_box.display()   
    nbbox.display()
    
    update_output()
    
def cbow_vector_picker(info):        
    output_box = wb.DynHTML(display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    nbbox = wb.nbbox(display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        if clear_nbbox:
            nbbox.clear()
        run_requirements_button.disabled = data.vocab_exists(info)
        output_box.update(wb.info_table('data:short,token:short,vocab:short,vector:long', info))
      
    def on_run_requirements_button_clicked(b):
        nbbox.make_current()
        nbbox.clear()
        try:
            check_requirements(info)
        except:
            nbprint.print_traceback()
        update_output(False)
        
    data_selector = wb.get_data_selector(info, update_output)
    token_selector = wb.get_token_selector(info, update_output, 'C')
    vocab_selector = wb.get_vocab_selector(info, update_output, 'C')
    vector_selector = wb.get_vector_selector(info, update_output, 'C')
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 token_selector,
                                 vocab_selector,
                                 vector_selector,
                                 run_requirements_button])
    
    display(settings_box)
    output_box.display()   
    nbbox.display()
    
    update_output()
    
def phrase_vector_picker(info):        
    output_box = wb.DynHTML(display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    nbbox = wb.nbbox(display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        if clear_nbbox:
            nbbox.clear()
        run_requirements_button.disabled = data.documents_exists(info)
        output_box.update(wb.info_table('data:short,vector:long', info))
      
    def on_run_requirements_button_clicked(b):
        nbbox.make_current()
        nbbox.clear()
        try:
            check_requirements(info)
        except:
            nbprint.print_traceback()
        update_output(False)
        
    data_selector = wb.get_data_selector(info, update_output)
    vector_selector = wb.get_vector_selector(info, update_output, 'P')
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 vector_selector,
                                 run_requirements_button])
    
    display(settings_box)
    output_box.display()   
    nbbox.display()
    
    update_output()