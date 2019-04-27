import config
import data
from base import nbprint
from util import iterate, import_cls

from importer.common import ImporterError

def import_data(info):
    # skip_existing
    if config.skip_existing:
        # Check documents file
        docs_exits = data.documents_exists(info)
        # Check classes file
        if info['data_info']['labels']:
            classes_exits = data.classes_exists(info)
        else:
            classes_exits = True # Not needed
        # Skip if both exist
        if docs_exits and classes_exits:
            nbprint('Skipping Importer (file(s) exists)')
            return
    
    # Import the corresponding module
    importer_cls = import_cls('importer', info['data_info']['mod'], info['data_info']['cls'])
    
    # Run the importer method
    try:
        importer_obj = importer_cls(info)
        importer_obj.run()
    except BaseException as err:
        data.clear_file(data.documents_filename(info))
        data.clear_file(data.classes_filename(info))
        if isinstance(err, ImporterError):
            nbprint(err)
            config.error_occured()
            return
        else:
            raise err
        
    nbprint('Importer: success')

def run_importer(info = None):
    nbprint('Importer').push()
    
    if info is None:
        iterate(["data"],[import_data], depth=0)
    else:
        import_data(info)
        
    nbprint.pop()