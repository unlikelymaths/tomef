
class EmbeddingError(Exception):
    def __init__(self, info, message, **kwargs):
        name = info["embedding_info"]["name"]
        model = info["embedding_info"]["model"]
        embedding_name = info["embedding_name"]
        infostring =  'Can\'t load embedding "{}" of model "{}": '
        infostring += str(message) + ' '
        infostring += 'See embedding/embedding_index.doc.ipynb for install instructions or set "run": false in config.embeddings["B"/"C"]["{}"].'
        infostring = infostring.format(name,model,embedding_name) 
        super().__init__(infostring, **kwargs)