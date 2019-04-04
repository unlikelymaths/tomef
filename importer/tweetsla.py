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

class TweetsLAImporter(ImporterBase):
    
    def get_archives(self, folder):
        # List all files
        try:
            files = listdir(folder)
        except FileNotFoundError:
            raise ImporterError(info, 'Directory "{}" does not exist'.format(folder))
            
        # Keep only .zip files
        archives = [file for file in files if file.split(".")[-1] == "zip"]
        return archives
         
    def parse_file(self, jsonfile):
        for line in ProgressIterator(jsonfile, 'Parsing tweets'):
            tweet = json.loads(line)
            if 'extended_tweet' in tweet:
                text = tweet['extended_tweet']['full_text']
            elif 'text' in tweet:
                text = tweet['text']
            else:
                continue
            self.docinfo.add_document(text)
        
    def import_archive(self):
        # Iterate all files in archive
        with zipfile.ZipFile(self.archivepath) as zip:
            filenames = [info.filename for info in zip.infolist()]
            for filename in filenames: 
                nbprint(filename)
                with zip.open(filename) as jsonfile:
                    self.parse_file(jsonfile)
                    
    def run(self):
        # Open Writer
        with data.document_writer(self.info) as document_writer:
            self.docinfo = DocumentInfo(document_writer)
            
            # Iterate all archives
            folder = join(config.paths["rawdata"],"tweetsla")  
            archives = self.get_archives(folder)
            for idx, archive in enumerate(archives):
                nbprint('{}/{}: {}'.format(idx + 1, len(archives),archive)).push()
                self.archivepath = join(folder,archive)
                self.import_archive()
                nbprint.pop()
            
            # Print Meta Info
            self.docinfo.save_meta(self.info)