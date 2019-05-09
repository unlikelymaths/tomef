import ipywidgets as widgets
from IPython.display import display, HTML, Markdown, DisplayHandle

import config
import data
import util
from base import nbprint

# Display Objects

class StyledHTML(HTML):
    """A HTML wrapper that adds css classes."""
    
    style = '''<style>
        .tdalignedlabel {width: 150px;
            text-align: left !important; 
            vertical-align: top !important;
            }
        .tdalignedvalue {width: 250px;
            text-align: left !important; 
            vertical-align: top !important;
            }
    </style>'''
    
    def __init__(self, html_string, **kwargs):
        HTML.__init__(self, StyledHTML.style + html_string, **kwargs)

class DynHTML():
    """A output element for displaying HTML that can be updated."""
    
    def __init__(self, html_string = '', display = True):
        self.html_string = html_string
        self.handle = DisplayHandle()
    
    def display(self):
        self.handle.display(StyledHTML(self.html_string))
    
    def update(self, html_string):
        self.html_string = html_string
        self.handle.update(StyledHTML(self.html_string))
        
class DynMarkdown():
    """A output element for displaying Markdown that can be updated."""
    
    def __init__(self, md_string = '', display = True, append = False):
        self.md_string = md_string
        self.append = append
        self.handle = DisplayHandle()
        self.last_string = []
        if display:
            self.display()
    
    def display(self):
        self.handle.display(Markdown(self.md_string))
    
    def update(self, md_string):
        self.last_string.append(self.md_string)
        if len(self.last_string) > 10:
            self.last_string = self.last_string[-10:]
        if self.append:
            self.md_string += str(md_string) + '  \n'
        else:
            self.md_string = str(md_string) 
        self.handle.update(Markdown(self.md_string))
        
    def clear(self):
        self.md_string = ''
        self.handle.update(Markdown(self.md_string))
    
    def revert_one(self):
        try:
            self.md_string = self.last_string.pop()
        except:
            self.md_string = ''
        self.handle.update(Markdown(self.md_string))
        
# Table Generator

_line_template = {'header': '''<tr>
    <td class="tdalignedlabel">
        <b>{label}</b>
    </td>
    <td class="tdalignedvalue">
        {value}
    </td>
</tr>\n''',
'std': '''<tr>
    <td class="tdalignedlabel">
        {label}
    </td>
    <td class="tdalignedvalue">
        {value}
    </td>
</tr>\n''',
'text': '''<tr>
    <td class="tdalignedlabel">
        {label}
    </td>
    <td class="tdalignedvalue">
        <textarea rows="16" cols="100" readonly>{value}</textarea>
    </td>
</tr>\n''',
'text2': '''<tr>
    <td class="tdalignedlabel">
        {label}
    </td>
    <td class="tdalignedvalue">
        <table>
            <tr>
                <td>
                    <textarea rows="16" cols="50" readonly>{value[0]}</textarea>
                </td>
                <td>
                    <textarea rows="16" cols="50" readonly>{value[1]}</textarea>
                </td>
            </tr>
        </table>
    </td>
</tr>\n'''
}

def _settings_entry(info, except_keys = ['name', 'mod', 'cls', 'run']):
    settings_string = ', '.join(
        ['<b>{}</b>: {}'.format(key,value) 
         for key, value in info.items() 
         if key not in except_keys])
    return ('Settings','std',settings_string)

def _sub_table(table_data):
    html = ''
    for entry in table_data:
        if len(entry) == 2:
            entry = (entry[0],entry[1],'')
        html += _line_template[entry[1]].format(label=entry[0], value=entry[2])
    return html

def _exists_str(info, entry_detail, fct):
    exists_str = '<font color="red"><b>missing</b></font>'
    try:
        if fct(info):
            exists_str = '<font color="green"><b>exists</b></font>'
    except: pass
    if entry_detail == 'short':
        exists_str = ' (' + exists_str + ')'
    return exists_str

def _data_table(info, entry_detail):
    data_info = info.get('data_info',{})
    exists_str = _exists_str(info, entry_detail, data.documents_exists)
    if entry_detail == 'short':
        return _sub_table([('Data Name', 'header', data_info.get('name','') + exists_str)])
    elif entry_detail == 'long':
        return _sub_table([('Data', 'header', exists_str),
                            ('Data Name', 'std', data_info.get('name',''))])

def _token_table(info, entry_detail):
    token_version = info.get('token_version','')
    token_info = info.get('token_info',{})
    exists_str = _exists_str(info, entry_detail, data.tokenized_document_exists)
    if entry_detail == 'short':
        return _sub_table([('Token Version', 'header', token_version + exists_str)])
    elif entry_detail == 'long':
        return _sub_table([('Token', 'header', exists_str),
                            ('Token Version', 'std', token_version),
                            ('Class','std', '{}.{}'.format(token_info.get('mod','-'),token_info.get('cls','-'))),
                            _settings_entry(token_info)])

def _vocab_table(info, entry_detail):
    vocab_version = info.get('vocab_version','')
    vocab_info = info.get('vocab_info',{})
    exists_str = _exists_str(info, entry_detail, data.vocab_exists)
    if entry_detail == 'short':
        return _sub_table([('Vocab Version', 'header', vocab_version + exists_str)])
    elif entry_detail == 'long':
        return _sub_table([('Vocab', 'header', exists_str),
                            ('Vocab Version', 'std', vocab_version),
                            ('Minimum Documents', 'std', vocab_info.get('min_docs','')),
                            ('Minimum Count', 'std', vocab_info.get('min_count','')),
                            ('Minimum Word Length', 'std', vocab_info.get('min_word_length','')),
                            ('Maximum Word Length', 'std', vocab_info.get('max_word_length',''))
                          ])
    
def _vector_table(info, entry_detail):
    vector_version = info.get('vector_version','')
    vector_info = info.get('vector_info',{})
    exists_str = _exists_str(info, entry_detail, data.input_mat_exists)
    if entry_detail == 'short':
        return _sub_table([('Vector Version', 'header', vector_version + exists_str)])
    elif entry_detail == 'long':
        bcp, vector_id = config.split(vector_version)
        table_data = [('Vector', 'header', exists_str),
                      ('Version', 'std', vector_version)]
        if bcp == 'B':
            table_data += [('TF', 'std', vector_info.get('tf')),
                          ('IDF', 'std', vector_info.get('idf'))]
        elif bcp == 'C':
            vector_cbow_type = vector_info.get('type')
            table_data += [('Type', 'std', vector_cbow_type)]
            if vector_cbow_type == 'TfIdf':
                table_data += [('TF', 'std', vector_info.get('tf')),
                               ('IDF', 'std', vector_info.get('idf'))]
        elif bcp == 'P':
            embedding_info = info.get('embedding_info',{})
            table_data += [('Name', 'std', embedding_info.get('name')),
                           ('Model', 'std', embedding_info.get('model'))]
        return _sub_table(table_data)
    
def _model_table(info, entry_detail):
    model_name = info.get('model_name','')
    model_info = info.get('model_info',{})
    exists_str = 'W: {}, H: {}, c: {}'.format(_exists_str(info, entry_detail, data.w_mat_exists),
                                              _exists_str(info, entry_detail, data.h_mat_exists),
                                              _exists_str(info, entry_detail, data.c_vec_exists))
    if entry_detail == 'short':
        return _sub_table([('Model Name', 'header', model_info.get('name','') + exists_str)])
    elif entry_detail == 'long':
        return _sub_table([('Model', 'header', exists_str),
                            ('Model Name', 'std', model_info.get('name','')),
                            ('Class','std', '{}.{}'.format(model_info.get('mod','-'),model_info.get('cls','-'))),
                            _settings_entry(model_info)])
    
def info_table(formatting, info = {}, **kwargs):
    """Generates HTML code for a table showing the info based on the selection
    
    formatting is a string containing the following entries separated by commas:
    data, token, vocab, vector (each followed by ':short' or ':long')
    alternatively one may use
    custom:var
    where var is a table_data list of tuples in kwargs.
    """
    html = '\n<table>\n'
    entries = formatting.split(',')
    for entry in entries:
        entry_name = entry.split(':')[0]
        entry_detail = entry.split(':')[1]
        if entry_name == 'data':
            html += _data_table(info, entry_detail)
        elif entry_name == 'token':
            html += _token_table(info, entry_detail)
        elif entry_name == 'vocab':
            html += _vocab_table(info, entry_detail)
        elif entry_name == 'vector':
            html += _vector_table(info, entry_detail)
        elif entry_name == 'model':
            html += _model_table(info, entry_detail)
        elif entry_name == 'custom':
            html += _sub_table(kwargs.get(entry_detail,[]))
    html += '</table>\n'
    return html

# Selector and Checker Widgets
style = {'description_width': '150px',}

def set_layout(widget):
    widget.layout.width = '400px'

def get_rawdocument_selector(info, callback):    
    id_selector = widgets.BoundedIntText(
        value=0,step=1,min=0,max=1000000000,
        description='Document',
        style=style
    )
    set_layout(id_selector)
    
    try:
        id_selector.value = info.get('document_id', vocab_selector.value)
    except: pass
    
    def update_info(document_id):
        info['document_id'] = document_id
        
    def on_id_selector_change(change):
        document_id = change['new']
        update_info(document_id)
        callback()
    id_selector.observe(on_id_selector_change, names='value')    
    
    update_info(id_selector.value)
    return id_selector    
    
def get_data_selector(info, callback):
    data_selector = widgets.Dropdown(
        options=[(config.datasets[data_name]["name"], data_name) for data_name in config.datasets],
        description='Dataset',
        style=style
    )
    set_layout(data_selector)
    
    try:
        data_selector.value = info.get('data_name', data_selector.value)
    except: pass
   
    def update_info(data_name):
        info['data_name'] = data_name
        info['data_info'] = config.datasets[data_name]
            
    def on_data_selector_change(change):
        data_name = change['new']
        if data_name == None:
            return
        update_info(data_name)
        callback()
    data_selector.observe(on_data_selector_change, names='value')    
    
    update_info(data_selector.value)
    return data_selector

def get_token_selector(info, callback, bcps):
    token_selector = widgets.Dropdown(
        options=config.token_version_list(bcps),
        description='Tokenizer Version',
        style=style
    )
    set_layout(token_selector)
    
    try:
        token_selector.value = info.get('token_version', token_selector.value)
    except: pass
    
    def update_info(token_version):
        bcp, id = config.split(token_version)
        info['token_version'] = token_version
        if bcp == 'B':
            info['token_info'] = config.tokenizer['B'][id]
            info.pop('embedding_name', None)
            info.pop('embedding_info', None)
        elif bcp == 'C':
            info['token_info'] = config.embeddings['C'][id]['token_info']
            info['embedding_name'] = id
            info['embedding_info'] = config.embeddings['C'][id]
    
    def on_token_selector_change(change):
        token_version = change['new']
        if token_version == None:
            return
        update_info(token_version)
        callback()
    token_selector.observe(on_token_selector_change, names='value')   
    
    update_info(token_selector.value)
    return token_selector

def get_vocab_selector(info, callback, vocab_types, description = 'Vocab Version'):
    vocab_selector = widgets.Dropdown(
        options=config.vocab_version_list(vocab_types),
        description=description,
        style=style
    )
    set_layout(vocab_selector)
    
    try:
        vocab_selector.value = info.get('vocab_version', vocab_selector.value)
    except: pass
    
    def update_info(vocab_version):
        vocab_type, vocab_idx = config.split(vocab_version)
        info['vocab_version'] = vocab_version
        info['vocab_info'] = config.vocab[vocab_type][vocab_idx]
        
    def on_vocab_selector_change(change):
        vocab_version = change['new']
        if vocab_version == None:
            return
        update_info(vocab_version)
        callback()
    vocab_selector.observe(on_vocab_selector_change, names='value')  
    
    update_info(vocab_selector.value)
    return vocab_selector

def get_linked_token_vocab_selector(info, callback):
    def token_changed():
        bcp, id = config.split(token_selector.value)
        if bcp == 'B' and not vocab_selector_c.disabled:
            vocab_selector_b.disabled = False
            vocab_selector_c.disabled = True
            val = vocab_selector_b.value
            vocab_selector_b.value = None
            vocab_selector_b.value = val
        elif bcp == 'C' and not vocab_selector_b.disabled:
            vocab_selector_b.disabled = True
            vocab_selector_c.disabled = False
            val = vocab_selector_c.value
            vocab_selector_c.value = None
            vocab_selector_c.value = val
        callback()
    
    
    token_selector = get_token_selector(info, token_changed, 'BC')
    vocab_selector_b = get_vocab_selector(info, callback, 'B', 'Vocab Version BoW')
    vocab_selector_c = get_vocab_selector(info, callback, 'C', 'cBoW')
    
    token_changed()
    
    return widgets.VBox([token_selector,
                         vocab_selector_b,
                         vocab_selector_c])
    
def get_vector_selector(info, callback, bcps):
    vector_selector = widgets.Dropdown(
        options = config.vector_version_list(bcps),
        description = 'Vectorizer Version',
        disabled = False,
        style = style
    )
    set_layout(vector_selector)
    
    try:
        vector_selector.value = info.get('vector_version', vector_selector.value)
    except: pass
    
    def update_info(vector_version):
        bcp, id = config.split(vector_version)
        info['vector_version'] = vector_version
        if bcp == 'B' or bcp == 'C':
            info['vector_info'] = config.vectorizer[bcp][id]
        elif bcp == 'P':
            info['embedding_info'] = config.embeddings['P'][id]
        
    def on_vector_selector_change(change):
        vector_version = change['new']
        update_info(vector_version)
        callback()
    vector_selector.observe(on_vector_selector_change, names='value')    
    
    update_info(vector_selector.value)
    return vector_selector

def get_model_selector(info, callback):
    model_selector = widgets.Dropdown(
        options = [(config.models['list'][model_name]["name"], model_name) for model_name in config.models['list']],
        description = 'Model',
        disabled = False,
        style = style
    )
    set_layout(model_selector)
    
    try:
        model_selector.value = info.get('model_name', model_selector.value)
    except: pass
    
    def update_info(model_name):
        info['model_name'] = model_name
        info['model_info'] = config.models['list'][model_name]
        
    def on_model_selector_change(change):
        model_name = change['new']
        update_info(model_name)
        callback()
    model_selector.observe(on_model_selector_change, names='value')    
    
    update_info(model_selector.value)
    return model_selector

def get_num_topics_selector(info, callback, data_selector):
    def get_num_topics_list(data_name):
        try:
            return config.datasets[data_name]['num_topics']
        except:
            pass
        return []
    
    num_topics_selector = widgets.Dropdown(
        options = get_num_topics_list(data_selector.value),
        description = 'Topics',
        disabled = False,
        style = style
    )
    set_layout(num_topics_selector)
    
    try:
        num_topics_selector.value = info.get('num_topics', num_topics_selector.value)
    except: pass
    
    def update_info(num_topics):
        info['num_topics'] = num_topics
        
    def on_num_topics_selector_change(change):
        num_topics = change['new']
        update_info(num_topics)
        callback()
    num_topics_selector.observe(on_num_topics_selector_change, names='value')    
    
    def on_data_selector_change(change):
        try:
            data_name = change['new']
            num_topics_selector.options = get_num_topics_list(data_name)
            callback()
        except:
            npprint.print_traceback()
    data_selector.observe(on_data_selector_change, names='value')    
    
    update_info(num_topics_selector.value)
    return num_topics_selector

def get_h_mat_selector(info, callback, labeled_only = False):
    h_mat_selector = widgets.Dropdown(
        options = data.get_all_h_mat_infos(labeled_only),
        description = 'H Matrix',
        disabled = False,
        style = style
    )
    set_layout(h_mat_selector)
    
    def update_info(new_info):
        for key, item in new_info.items():
            info[key] = item
        
    def on_h_mat_selector_change(change):
        new_info = change['new']
        update_info(new_info)
        callback()
    h_mat_selector.observe(on_h_mat_selector_change, names='value')    
    
    update_info(h_mat_selector.value)
    return h_mat_selector
    
def get_c_vec_selector(info, callback, labeled_only = False):
    c_vec_selector = widgets.Dropdown(
        options = data.get_all_c_vec_infos(labeled_only),
        description = 'c Vector',
        disabled = False,
        style = style
    )
    set_layout(c_vec_selector)
    
    def update_info(new_info):
        for key, item in new_info.items():
            info[key] = item
        
    def on_c_vec_selector_change(change):
        new_info = change['new']
        update_info(new_info)
        callback()
    c_vec_selector.observe(on_c_vec_selector_change, names='value')    
    
    update_info(c_vec_selector.value)
    return c_vec_selector

def get_w_mat_selector(info, callback):
    w_mat_selector = widgets.Dropdown(
        options = data.get_all_w_mat_infos(),
        description = 'W Matrix',
        disabled = False,
        style = style
    )
    set_layout(w_mat_selector)
    
    def update_info(new_info):
        for key, item in new_info.items():
            info[key] = item
        
    def on_w_mat_selector_change(change):
        new_info = change['new']
        update_info(new_info)
        callback()
    w_mat_selector.observe(on_w_mat_selector_change, names='value')    
    
    update_info(w_mat_selector.value)
    return w_mat_selector

def get_topiclist_selector(info, callback):
    topiclist_selector = widgets.Dropdown(
        options = data.get_all_topiclist_infos(),
        description = 'Topiclist',
        disabled = False,
        style = style
    )
    set_layout(topiclist_selector)
    
    def update_info(new_info):
        info.clear()
        for key, item in new_info.items():
            info[key] = item
        
    def on_topiclist_selector_change(change):
        new_info = change['new']
        update_info(new_info)
        callback()
    topiclist_selector.observe(on_topiclist_selector_change, names='value')    
    
    update_info(topiclist_selector.value)
    return topiclist_selector
    

# NB Box

class NotebookBox():
    def __init__(self, mini = False, display = True):
        if mini:
            self.level = 2
        else:
            self.level = 0
        
        self.markdown_area = DynMarkdown(display = False, append = True)
        
        self.progress_widget = widgets.FloatProgress(
            value=0,min=0,max=1,step=0.01,
            description='',bar_style='info',orientation='horizontal',
            style=style)
        self.progress_widget.layout.visibility = 'hidden'
        
        if display:
            self.display()
        self.make_current()
            
    def make_current(self):
        nbprint.setelement(self.markdown_area)
        util._progress_widget = self.progress_widget
        nbprint.level = self.level
        
    def display(self):
        self.markdown_area.display()
        display(self.progress_widget)
        self.make_current()
        
    def clear(self):
        nbprint.clear()
        nbprint.level = self.level
        
def nbbox(**kwargs):
    try:
        get_ipython
        return NotebookBox(**kwargs)
    except:
        return None
    