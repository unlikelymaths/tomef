from base import config, util
from interface import nbprint


class BreakIteration(Exception):
    pass


def check_model_output(info, original_callback):
    global _required_model_outputs
    output = info['model'].output_of(info)
    if _required_model_outputs is None:
        if len(output) == 0:
            raise BreakIteration()
    else:
        for required_output in _required_model_outputs:
            if required_output not in output:
                raise BreakIteration()
                
    if original_callback is not None:
        original_callback(info)


def _call_next(what, callbacks, print_string, new_data, info, print_iterates):
    if print_string and print_iterates == True:
        nbprint(print_string)
    if print_iterates == True:
        nbprint.push()
    new_info = {**info, **new_data}
    if callbacks[0] is not None:
        callbacks[0](new_info)
    if len(what) > 1:
        try:
            _select_iterate(what[1:], callbacks[1:], new_info, print_iterates)
        except BreakIteration:
            if print_iterates == True:
                nbprint('skipping')
    if print_iterates == True:
        nbprint.pop()


def _iterate_data(what, callbacks, info, print_iterates):
    for data_name, data_info in config.datasets.items():
        if data_info['run']:
            new_data = {'data_name': data_name, 
                'data_info': data_info}
            _call_next(what, callbacks, 
                data_info['name'], 
                new_data, info, print_iterates)


def _iterate_token(what, callbacks, info, print_iterates, detail):
    for token_version in config.token_version_list(detail):
        bcp, id = config.split(token_version)
        if bcp == 'B':
            token_info = config.tokenizer['B'][id]
            if token_info['run']:
                new_data = {'token_version': token_version, 
                            'token_info': token_info}
                _call_next(what, callbacks, 'Token {}'.format(token_version), 
                    new_data, info, print_iterates)
        elif bcp == 'C':
            embedding_info = config.embeddings['C'][id]
            if embedding_info['run']:  
                new_data = {'token_version': token_version, 
                            'token_info': embedding_info['token_info'],
                            'embedding_name': id,
                            'embedding_info': embedding_info}
                _call_next(what, callbacks, 
                    'Token {}'.format(token_version), 
                    new_data, info, print_iterates)


def _iterate_vocab(what, callbacks, info, print_iterates):
    if 'token_version' not in info:
        nbprint('WARNING: Cannot iterate "vocab" without knowing token version')
        return
    token_bcp = config.split(info['token_version'])[0]
    for vocab_version in config.vocab_version_list(token_bcp):
        bcp, id = config.split(vocab_version)
        vocab_info = config.vocab[bcp][id]
        if vocab_info['run']:
            new_data = {'vocab_version': vocab_version, 
                'vocab_info': vocab_info}
            _call_next(what, callbacks, 
                'Vocab {}'.format(new_data['vocab_version']), 
                new_data, info, print_iterates)


def _iterate_vector(what, callbacks, info, print_iterates, detail):
    for vector_version in config.vector_version_list(detail):
        bcp, id = config.split(vector_version)
        if bcp == 'B' or bcp == 'C':
            vector_info = config.vectorizer[bcp][id]
            if vector_info['run']:
                new_data = {'vector_version': vector_version, 
                            'vector_info': vector_info}
                _call_next(what, callbacks, 
                    'Vector {}'.format(new_data['vector_version']), 
                    new_data, info, print_iterates)
        elif bcp == 'P':
            embedding_info = config.embeddings['P'][id]
            if embedding_info['run']:
                new_data = {'vector_version': vector_version, 
                    'embedding_info': embedding_info}
                _call_next(what, callbacks, 
                    'Vector {}'.format(new_data['vector_version']), 
                    new_data, info, print_iterates)


def _iterate_models(what, callbacks, info, print_iterates, detail):
    global _required_model_outputs
    if detail is not None:
        detail = detail.split(',')
    _required_model_outputs = detail
    for model_name, model_info in config.models['list'].items():
        if model_info['run']:
            model = import_cls('models', 
                model_info['mod'], model_info['cls'])(model_info)
            new_data = {'model_name': model_name,
                        'model_info': model_info,
                        'model': model}
            _call_next(what, callbacks, 
                'Model {}'.format(model_info['name']), 
                new_data, info, print_iterates)


def _iterate_modelinputs(what, callbacks, info, print_iterates):
    if 'model_info' not in info:
        nbprint('WARNING: Cannot iterate "modelinputs" without knowing model')
        return
    vector_bcps = info['model_info'].get('vector', 'BCP')
    callbacks[0] = lambda i : check_model_output(i, callbacks[0])
    if 'B' in vector_bcps:
        token_bcps = info['model_info'].get('token', 'BC')
        what_b = what.copy()
        what_b[1:1] = ['data', 
            'token:{}'.format(token_bcps), 'vocab', 'vector:B']
        callbacks_b = [None] * (len(what_b) - len(callbacks)) + callbacks
        _call_next(what_b, callbacks_b, 
            'Model Input BoW', 
            {}, info, print_iterates)
    if 'C' in vector_bcps:
        what_c = what.copy()
        what_c[1:1] = ['data', 
            'token:C', 'vocab', 'vector:C']
        callbacks_c = [None] * (len(what_c) - len(callbacks)) + callbacks
        _call_next(what_c, callbacks_c, 
            'Model Input cBoW', 
            {}, info, print_iterates)
    if 'P' in vector_bcps:
        what_p = what.copy()
        what_p[1:1] = ['data', 'vector:P']
        callbacks_p = [None] * (len(what_p) - len(callbacks)) + callbacks
        _call_next(what_p, callbacks_p, 
            'Model Input Phrase', 
            {}, info, print_iterates)


def _iterate_num_topics(what, callbacks, info, print_iterates):
    if 'data_info' not in info:
        nbprint('WARNING: Cannot iterate "num_topics" without knowing data')
        return
    for num_topics in info['data_info']['num_topics']:
        num_topics = util.convert_num_topics(info, num_topics)
        new_data = {'num_topics': num_topics}
        _call_next(what, callbacks, 
            'Topics {}'.format(num_topics), 
            new_data, info, print_iterates)


def _iterate_distiller(what, callbacks, info, print_iterates):
    for distiller_name, distiller_info in config.distiller['list'].items():
        if distiller_info['run']:
            distiller = import_cls('distiller', 
                distiller_info['mod'], distiller_info['cls'])(distiller_info)
            new_data = {'distiller_name': distiller_name,
                        'distiller_info': distiller_info,
                        'distiller': distiller}
            _call_next(what, callbacks, 
                'Distiller {}'.format(distiller_info['name']), 
                new_data, info, print_iterates)


def _iterate_distillerinputs(what, callbacks, info, print_iterates):
    model_out = info['distiller_info']['model_out']
    original_callback = callbacks[0]
    for model_out_entry in model_out:
        what_version = what.copy()
        what_version[1:1] = ['models:{}'.format(model_out_entry),
            'modelinputs','num_topics']
        callbacks_version = ([None] * (len(what_version) - len(callbacks)) + 
            callbacks)
        _call_next(what_version, callbacks_version, 
            'Model Input BoW', 
            {}, info, print_iterates)


def _select_iterate(what, callbacks, info = {}, print_iterates = True):
    try:
        category, detail = what[0].split(':')
    except ValueError:
        category, detail = what[0], None
        
    if category == 'data':
        _iterate_data(what, callbacks, info, print_iterates)
    elif category == 'token':
        _iterate_token(what, callbacks, info, print_iterates, detail or 'BC')
    elif category == 'vocab':
        _iterate_vocab(what, callbacks, info, print_iterates)
    elif category == 'vector':
        _iterate_vector(what, callbacks, info, print_iterates, detail or 'BCP')
    elif category == 'models':
        _iterate_models(what, callbacks, info, print_iterates, detail)
    elif category == 'modelinputs':
        _iterate_modelinputs(what, callbacks, info, print_iterates)
    elif category == 'num_topics':
        _iterate_num_topics(what, callbacks, info, print_iterates)
    elif category == 'distiller':
        _iterate_distiller(what, callbacks, info, print_iterates)
    elif category == 'distillerinputs':
        _iterate_distillerinputs(what, callbacks, info, print_iterates)
    else:
        nbprint('WARNING: Cannot iterate "{}"'.format(what[0]))


def iterate(what, callbacks, info = {}, print_iterates = True):
    if not isinstance(what, list):
        what = [what,]
    if not isinstance(callbacks, list):
        callbacks = [callbacks,]
    callbacks = [None] * (len(what) - len(callbacks)) + callbacks
    _select_iterate(what, callbacks, info, print_iterates)