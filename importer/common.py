
doc_progress_label = 'Importing Documents'

class ImporterError(Exception):
    def __init__(self, info, message, **kwargs):
        data_name = info.get('data_name', 'NOT SPECIFIED')
        infostring =  'Can\'t import dataset "{}": '
        infostring += str(message) + ' '
        infostring += 'See importer/datasets.doc.ipynb for install instructions or set "run": false in config.datasets["{}"].'
        infostring = infostring.format(data_name,data_name) 
        super().__init__(infostring, **kwargs)