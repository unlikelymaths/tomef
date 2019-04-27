from util import import_cls

def get_vocab_builder(info):
    vocab_builder_cls = import_cls('vocab', info['vocab_info']['mod'], info['vocab_info']['cls'])
    return vocab_builder_cls(info)