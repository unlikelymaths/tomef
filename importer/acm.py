import zipfile
import json
from os.path import join
from os import listdir

import config
import data
from base import nbprint
from util import ProgressIterator

    
from importer.util import DocumentInfo, ImporterBase
from importer.common import ImporterError, doc_progress_label

class ACMImporter(ImporterBase):
    
    def import_archive(self):
        # Iterate all files in archive
        with zipfile.ZipFile(self.archivepath) as zip:
            filenames = [info.filename for info in zip.infolist()]
            for filename in ProgressIterator(filenames): 
                if filename.endswith('.txt'):
                    with zip.open(filename, 'r') as txtfile:
                        text = txtfile.read().decode('utf-8')
                        self.docinfo.add_document(text)
                    
    def run(self):
        # Open Writer
        with data.document_writer(self.info) as document_writer:
            self.docinfo = DocumentInfo(document_writer)
            
            # Open archive
            self.archivepath = join(config.paths['rawdata'],'acm/abstract.zip')  
            self.import_archive()
            
            # Print Meta Info
            self.docinfo.save_meta(self.info)