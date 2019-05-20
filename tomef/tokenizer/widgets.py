import ipywidgets as widgets
from IPython.display import display, HTML


from base import config, data
from interface import nbprint, nbbox, ProgressIterator
from interface.display import DynamicHTML
from interface.tables import info_table
from interface.selectors import (get_data_selector, 
    get_rawdocument_selector, get_token_selector)

from tokenizer.common import separator_token, get_tokenizer
from tokenizer.util import check_requirements

def token_app():
    info = {}
    output_box = DynamicHTML(update_display = False)
    token_nbbox = nbbox(update_display = False)
    
    def update_output():
        with token_nbbox:
            output_box.set(info_table('data:short,token:long', 
                info, exists = [('Exists','header',data.tokenized_document_exists(info))]))
      
    def on_run_button_clicked(b):
        token_nbbox.clear()
        with token_nbbox:
            try:
                check_requirements(info)
                from tokenizer.main import run_tokenizer
                run_tokenizer(info)
            except:
                nbprint.print_traceback()
        update_output()
    
    data_selector = get_data_selector(info, update_output)
    token_selector = get_token_selector(info, update_output, 'BC')
    run_button = widgets.Button(description="Run All")
    run_button.on_click(on_run_button_clicked)
    settings_box = widgets.VBox([data_selector,token_selector,run_button])
    
    display(settings_box)
    output_box.display()
    token_nbbox.display()
    update_output()
    
def token_picker(info, runvars, bcp='B'):
    output_box = DynamicHTML(update_display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    token_nbbox = nbbox()
    
    def document_table(replacement_text = None):
        header = ('Document', 'header')
        document_id = ('Id', 'std', info['document_id'])
        if replacement_text is not None:
            text = replacement_text
        else:
            try:
                text = runvars['document']['text']
            except:
                text = 'Not available'
        text = ('', 'text', text)
        return [header, document_id, text]
    
    def load_document():
        try:
            with data.document_reader(info) as documents:
                runvars['document'] = next(doc for doc in documents if doc["id"]==info["document_id"])
        except: pass
    
    def update_output():
        runvars['document'] = None
        if data.documents_exists(info):
            run_requirements_button.disabled = True
            output_box.set(info_table('data:short,token:long,custom:document', info, document=document_table('Loading...')))
            load_document()
        else:
            run_requirements_button.disabled = False
        output_box.set(info_table('data:short,token:long,custom:document', info, document=document_table()))
            
    def on_run_requirements_button_clicked(b):
        with token_nbbox:
            try:
                check_requirements(info)
            except:
                nbprint.print_traceback()
            update_output(False)
        
    data_selector = get_data_selector(info, update_output)
    document_selector = get_rawdocument_selector(info, update_output)
    token_selector = get_token_selector(info, update_output, bcp)
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 document_selector,
                                 token_selector,
                                 run_requirements_button])
    
    
    display(settings_box)
    output_box.display()
    update_output()
  
def tokenize_document_widget(info, runvars):
    output_box = DynamicHTML(update_display = False)
    run_requirements_button = widgets.Button(description="Run Requirements")
    token_nbbox = nbbox()
    
    def document_table(replacement_text = None):
        header = ('Document', 'header')
        document_id = ('Id', 'std', info['document_id'])
        if replacement_text is not None:
            text = replacement_text
        else:
            try:
                text = runvars['document']['text']
            except:
                text = ['Not available', 'Not available']
            if not isinstance(text, list):
                try:
                    text = [text,runvars['tokens']]
                except:
                    text = [text, 'Processing']
        text = ('', 'text2', text)
        return [header, document_id, text]
    
    def load_document():
        try:
            with data.document_reader(info) as documents:
                runvars['document'] = next(doc for doc in documents if doc["id"]==info["document_id"])
        except: pass
    
    def tokenize_document():
        try:
            token = get_tokenizer(info)
            runvars['tokens'] = token.tokenize(runvars['document']['text'])
            output_box.set(info_table('data:short,token:long,custom:document', info, document=document_table()))
        except:
            nbprint.print_traceback()
        
    
    def update_output():
        runvars['document'] = None
        runvars['tokens'] = None
        if data.documents_exists(info):
            run_requirements_button.disabled = True
            output_box.set(info_table('data:short,token:long,custom:document', info, document=document_table('Loading...')))
            load_document()
        else:
            run_requirements_button.disabled = False
        output_box.set(info_table('data:short,token:long,custom:document', info, document=document_table()))
        tokenize_document()
        output_box.set(info_table('data:short,token:long,custom:document', info, document=document_table()))
            
    def on_run_requirements_button_clicked(b):
        with token_nbbox:
            try:
                check_requirements(info)
            except:
                nbprint.print_traceback()
            update_output(False)
        
    data_selector = get_data_selector(info, update_output)
    document_selector = get_rawdocument_selector(info, update_output)
    token_selector = get_token_selector(info, update_output, 'BC')
    run_requirements_button.on_click(on_run_requirements_button_clicked)
    settings_box = widgets.VBox([data_selector,
                                 document_selector,
                                 token_selector,
                                 run_requirements_button])
    
    
    display(settings_box)
    output_box.display()
    update_output()

def get_attribute(obj, attribute):
    return_val = getattr(obj, attribute)
    if isinstance(return_val, list):
        return return_val.copy()
    return return_val

def list_to_string(value):
    if isinstance(value, list):
        return (separator_token + ' ').join(
            [str(entry) for entry in value])
    return value
    
def show_comparison(before, after, before_label, after_label):
    template = '''<table>
            <tr>
                <td>{}</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>
                    <textarea rows="20" cols="80" readonly>{}</textarea>
                </td>
                <td>
                    <textarea rows="20" cols="80" readonly>{}</textarea>
                </td>
            </tr>
        </table>'''
    display(HTML(template.format(before_label, after_label,
                                 list_to_string(before),list_to_string(after))))


def run_and_compare(tokenizer, func, before_attribute, after_attribute = None, before_label='Before', after_label='After'):
    before = get_attribute(tokenizer, before_attribute)
    func()
    after = get_attribute(tokenizer, after_attribute or before_attribute)
    show_comparison(before, after, before_label, after_label)