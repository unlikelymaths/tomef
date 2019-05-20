from base.util import import_cls

separator_token = ';'
separator_token_replacement = ','
number_token = '[NUM]'
url_token = '[URL]'
emote_token = '[EMOTE]'

def split_tokens(token_str):
    return token_str.split(separator_token)
    
def join_tokens(tokens):
    return separator_token.join(tokens)

def get_tokenizer(info):
    tokenizer_cls = import_cls('tokenizer', info['token_info']['mod'], info['token_info']['cls'])
    return tokenizer_cls(info)