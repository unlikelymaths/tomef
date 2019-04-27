import ipywidgets as widgets
from IPython.display import display

import config
import data
import widgetbase as wb
from base import nbprint

from vocab.vocab_util import check_requirements

def vocab_app():
    info = {}
    output_box = wb.DynHTML(display = False)
    nbbox = wb.nbbox(mini = True, display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        if clear_nbbox:
            nbbox.clear()
        output_box.update(wb.info_table('data:short,token:short,vocab:long', info))
      
    def on_run_button_clicked(b):
        nbbox.make_current()
        nbbox.clear()
        try:
            check_requirements(info)
            from vocab.main import run_vocab
            run_vocab(info)
        except:
            nbprint.print_traceback()
        update_output(False)
        
    data_selector = wb.get_data_selector(info, update_output)
    token_vocab_selector = wb.get_linked_token_vocab_selector(info, update_output)
    run_button = widgets.Button(description="Run All")
    run_button.on_click(on_run_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 token_vocab_selector,
                                 run_button])
    
    display(settings_box)
    output_box.display()
    nbbox.display()

def vocab_picker(info):
    if info is None:
        return
        
    output_box = wb.DynHTML(display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    nbbox = wb.nbbox(display = False)
    
    def update_output(clear_nbbox = True):
        nbbox.make_current()
        if clear_nbbox:
            nbbox.clear()
        run_requirements_button.disabled = data.tokenized_document_exists(info)
        output_box.update(wb.info_table('data:short,token:short,vocab:long', info))
      
    def on_run_requirements_button_clicked(b):
        nbbox.make_current()
        nbprint.clear()
        try:
            check_requirements(info)
        except:
            nbbox.print_traceback()
        update_output(False)
        
    data_selector = wb.get_data_selector(info, update_output)
    token_selector = wb.get_token_selector(info, update_output, 'B')
    count_vocab_selector = wb.get_vocab_selector(info, update_output, 'B')
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,token_selector,count_vocab_selector,run_requirements_button])
    
    display(settings_box)
    output_box.display()  
    nbbox.display()
    
    update_output()