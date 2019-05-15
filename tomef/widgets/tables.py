import traceback
import ipywidgets as widgets
from IPython.display import display, Markdown, Latex, HTML, DisplayHandle

import config
import data
import util

      
# Teble templates
_line_template = {}
_line_template['header']: '''<tr>
    <td class="tdalignedlabel">
        <b>{label}</b>
    </td>
    <td class="tdalignedvalue">
        {value}
    </td>
</tr>\n'''
_line_template['std']: '''<tr>
    <td class="tdalignedlabel">
        {label}
    </td>
    <td class="tdalignedvalue">
        {value}
    </td>
</tr>\n''',
_line_template['text']: '''<tr>
    <td class="tdalignedlabel">
        {label}
    </td>
    <td class="tdalignedvalue">
        <textarea rows="16" cols="100" readonly>{value}</textarea>
    </td>
</tr>\n''',
_line_template['text2']: '''<tr>
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