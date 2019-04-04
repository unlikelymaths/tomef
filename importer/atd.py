from os.path import join
from os import listdir

import config
import data
from util import ProgressIterator
from base import nbprint

from importer.util import DocumentInfo, ImporterBase
from importer.common import ImporterError, doc_progress_label


class ATDImporter(ImporterBase):
    
    def run(self):
        folder = join(config.paths["rawdata"],"atd")
        
        # List txt files
        try:
            files = listdir(folder)
        except FileNotFoundError:
            raise ImporterError(info, 'Directory "{}" does not exist'.format(folder))
            
        # Keep only .txt files
        files = [file for file in files if file.split(".")[-1] == "txt"]
        
        # Check if files exist
        if len(files) == 0:
            raise ImporterError(info, 'There are no valid files in the folder.')
        
        # Add files one by one
        with data.document_writer(self.info) as document_writer:
            docinfo = DocumentInfo(document_writer)
            for filename in ProgressIterator(files, doc_progress_label):
                if filename.split(".")[-1] != "txt":
                    continue
                with open(join(folder,filename),"r", encoding="utf8") as file:
                    text = file.read()
                    docinfo.add_document(text)
            # Print Meta Information
            docinfo.save_meta(self.info)