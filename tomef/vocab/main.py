from base import data, config, util, iterator
from interface import nbprint, nbbox, ProgressIterator

from vocab.common import get_vocab_builder
from vocab.util import check_requirements

def check_tokens(info):
    # Check if Tokens exist
    if not check_requirements(info):
        nbprint('Skipping Vocab (requirements not satisfied)')
        raise BreakIteration()
    
def build_vocab(info):
    # Check if vocab exists
    if config.skip_existing and data.vocab_exists(info):
        nbprint('Skipping Vocab (file exists)')
        return
    
    # Build vocab
    current_vocab_builder = get_vocab_builder(info)
    with util.ModuleTimer('vocab', info):
        current_vocab_builder.build_vocab()
    vocab = current_vocab_builder.get_vocab()
    
    # Save Vocab
    data.save_vocab(vocab, info)

def run_vocab(info = None):
    nbprint('Vocab').push()
    
    if info is None:
        iterator.iterate(["data", "token", "vocab"], [check_tokens, build_vocab])
    else:
        check_tokens(info)
        build_vocab(info)
    
    nbprint.pop()