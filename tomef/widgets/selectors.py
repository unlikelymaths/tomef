import traceback
import ipywidgets as widgets
from IPython.display import display, Markdown, Latex, HTML, DisplayHandle
from widgets.display import style

import config
import data
import util




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
    