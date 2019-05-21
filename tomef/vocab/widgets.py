import ipywidgets as widgets
from IPython.display import display
import random

from base import config, data
from interface import nbprint, nbbox, ProgressIterator
from interface.display import DynamicHTML
from interface.tables import info_table
from interface.selectors import (get_data_selector, 
    get_linked_token_vocab_selector)

from vocab.util import check_requirements, VocabItem

def vocab_app():
    info = {}
    output_box = DynamicHTML(update_display = False)
    vocab_nbbox = nbbox(update_display = False)
    
    def update_output(clear_nbbox = True):
        output_box.set(info_table('data:short,token:short,vocab:long', info))
      
    def on_run_button_clicked(b):
        vocab_nbbox.clear()
        with vocab_nbbox:
            try:
                check_requirements(info)
                from vocab.main import run_vocab
                run_vocab(info)
            except:
                nbprint.print_traceback()
            update_output(False)
        
    data_selector = get_data_selector(info, update_output)
    token_vocab_selector = get_linked_token_vocab_selector(info, update_output)
    run_button = widgets.Button(description="Run All")
    run_button.on_click(on_run_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 token_vocab_selector,
                                 run_button])
    
    display(settings_box)
    output_box.display()
    vocab_nbbox.display()

def vocab_picker(info):
    output_box = DynamicHTML(update_display = False)
    vocab_nbbox = nbbox(update_display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    
    def update_output(clear_nbbox = True):
        run_requirements_button.disabled = data.tokenized_document_exists(info)
        output_box.set(info_table('data:short,token:short,vocab:long', info))
      
    def on_run_requirements_button_clicked(b):
        vocab_nbbox.clear()
        with vocab_nbbox:
            try:
                check_requirements(info)
            except:
                nbbox.print_traceback()
            update_output(False)
        
    data_selector = get_data_selector(info, update_output)
    token_vocab_selector = get_linked_token_vocab_selector(info, update_output)
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,token_vocab_selector,run_requirements_button])
    
    display(settings_box)
    output_box.display()  
    vocab_nbbox.display()
    
    update_output()
    
def show_tokens(tokens, num_tokens):
    with nbbox():
        highest_tokens = tokens[:num_tokens]
        random_tokens = random.sample(tokens, num_tokens)
        format_str = '| {} | {} | {} | {} | {} | {} |'
        nbprint(format_str.format('Highest Token', 'Total', 'Documents','Random Token', 'Total', 'Documents'))
        nbprint(format_str.format('---', '---', '---', '---', '---', '---'))
        for i in range(num_tokens):
            nbprint(format_str.format(
                highest_tokens[i].token, highest_tokens[i].total, highest_tokens[i].document,
                random_tokens[i].token, random_tokens[i].total, random_tokens[i].document))