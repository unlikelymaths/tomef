import ipywidgets as widgets
from IPython.display import display

from base import data, config
from interface import nbprint, nbbox
from interface.display import DynamicHTML
from interface.tables import info_table
from interface.selectors import (get_data_selector, 
    get_linked_token_vocab_selector,
    get_token_selector, get_vocab_selector,
    get_vector_selector)

from vectorizer.util import check_requirements

def vector_app():
    info = {}
    output_box = DynamicHTML(update_display = False)
    vector_nbbox = nbbox(update_display = False)
    
    def update_output():
        output_box.set(info_table('data:short,token:long,vocab:short,vector:long', info))
      
    def on_run_button_clicked(b):
        vector_nbbox.clear()
        with vector_nbbox:
            try:
                check_requirements(info)
                from vectorizer.main import run_vectorizer
                run_vectorizer(info)
            except:
                nbprint.print_traceback()
            update_output()
        
    data_selector = get_data_selector(info, update_output)
    token_vocab_selector = get_linked_token_vocab_selector(info, update_output)
    token_selector = get_token_selector(info, update_output, 'C')
    vocab_selector = get_vocab_selector(info, update_output, 'C')
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
        update_output()
    vector_selector = get_vector_selector(info, vector_changed, 'BCP')
    
    run_button.on_click(on_run_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 vector_selector,
                                 token_vocab_selector,
                                 token_selector,
                                 vocab_selector,
                                 run_button])
    
    display(settings_box)
    output_box.display()
    vector_nbbox.display()
    vector_changed()

def bow_vector_picker(info):        
    output_box = DynamicHTML(update_display = False)
    vector_nbbox = nbbox(update_display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    
    def update_output():
        run_requirements_button.disabled = data.vocab_exists(info)
        output_box.set(info_table('data:short,token:short,vocab:short,vector:long', info))
      
    def on_run_requirements_button_clicked(b):
        vector_nbbox.clear()
        with vector_nbbox:
            try:
                check_requirements(info)
            except:
                nbprint.print_traceback()
            update_output(False)
        
    data_selector = get_data_selector(info, update_output)
    token_vocab_selector = get_linked_token_vocab_selector(info, update_output)
    count_vector_selector = get_vector_selector(info, update_output, 'B')
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 token_vocab_selector,
                                 count_vector_selector,
                                 run_requirements_button])
    
    display(settings_box)
    output_box.display()   
    vector_nbbox.display()
    update_output()
    
def cbow_vector_picker(info):        
    output_box = DynamicHTML(update_display = False)
    vector_nbbox = nbbox(update_display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    
    def update_output():
        run_requirements_button.disabled = data.vocab_exists(info)
        output_box.set(info_table('data:short,token:short,vocab:short,vector:long', info))
      
    def on_run_requirements_button_clicked(b):
        vector_nbbox.clear()
        with vector_nbbox:
            try:
                check_requirements(info)
            except:
                nbprint.print_traceback()
            update_output(False)
        
    data_selector = get_data_selector(info, update_output)
    token_selector = get_token_selector(info, update_output, 'C')
    vocab_selector = get_vocab_selector(info, update_output, 'C')
    vector_selector = get_vector_selector(info, update_output, 'C')
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 token_selector,
                                 vocab_selector,
                                 vector_selector,
                                 run_requirements_button])
    
    display(settings_box)
    output_box.display()   
    vector_nbbox.display()
    update_output()
    
def phrase_vector_picker(info):
    output_box = DynamicHTML(update_display = False)
    vector_nbbox = nbbox(update_display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    
    def update_output():
        run_requirements_button.disabled = data.documents_exists(info)
        output_box.set(info_table('data:short,vector:long', info))
      
    def on_run_requirements_button_clicked(b):
        vector_nbbox.clear()
        with vector_nbbox:
            try:
                check_requirements(info)
            except:
                nbprint.print_traceback()
            update_output(False)
        
    data_selector = get_data_selector(info, update_output)
    vector_selector = get_vector_selector(info, update_output, 'P')
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 vector_selector,
                                 run_requirements_button])
    
    display(settings_box)
    output_box.display()   
    vector_nbbox.display()
    update_output()