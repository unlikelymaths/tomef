from base import data
from interface import nbprint

from importer.main import run_importer

def check_requirements(info):
    # Check if documents file exists
    if not data.documents_exists(info):
        # Run importer
        nbprint('Documents missing.')
        run_importer(info)
        # Check if it was successfull
        return data.documents_exists(info)
    return True
        
def iterate_tokens(tokens, func):
    i = 0
    while i < len(tokens):
        result = func(tokens[i])
        if isinstance(result, str):
            if len(result) == 0:
                del tokens[i]
            else:
                tokens[i] = result
                i += 1
        elif result is None:
            del tokens[i]
        elif isinstance(result, list):
            if len(result) == 0:
                del tokens[i]
            else:
                tokens[i] = result[0]
                i += 1
                for token in result[1:]:
                    tokens.insert(i,token)
                    i += 1
                    
class TokenizerBase():
    def __init__(self, info):
        self.info = info