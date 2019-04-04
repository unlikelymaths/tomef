from util import import_cls


def get_model(info):
    model_cls = import_cls('models', info['model_info']['mod'], info['model_info']['cls'])
    return model_cls(info['model_info'])