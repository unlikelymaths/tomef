from util import import_cls

from embedding.embedding_model import EmbeddingModel

def get_model(info):
    mod_name = info['embedding_info']['mod']
    cls_name = info['embedding_info']['cls']
    model_cls = import_cls('embedding', mod_name, cls_name)
    if EmbeddingModel.current_model_is_same(model_cls, info):
        return EmbeddingModel.current_model()
    return model_cls(info)
    
def clear():
    EmbeddingModel.clear()