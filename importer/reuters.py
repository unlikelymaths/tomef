import re
from os.path import join
from nltk.data import path as nltk_path
from nltk.corpus import reuters

import config, data
from base import nbprint
from util import ProgressIterator

from importer.util import ClassInfo, DocumentInfo, ImporterBase
from importer.common import ImporterError, doc_progress_label

class ReutersImporter(ImporterBase):
    
    def count_docs_per_class(self):
        counts = {}
        for file in reuters.fileids():
            categories = reuters.categories(file)
            if len(categories) == 1:
                classname = categories[0]
                try:
                    counts[classname] += 1
                except KeyError:
                    counts[classname] = 1
        return counts
    
    def filter_classes(self,counts):
        newcounts = {}
        for key,val in counts.items():
            if val >= self.info['data_info']["min_docs_per_class"]:
                newcounts[key] = val
        return newcounts
        
    def load_valid_classes(self):
        counts = self.count_docs_per_class()
        counts = self.filter_classes(counts)
        self.valid_classes = list(counts)
        
    def load_documents(self):        
        for file in ProgressIterator(reuters.fileids(), doc_progress_label):
            categories = reuters.categories(file)
            if len(categories) > 1:
                continue
            classname = categories[0]
            if not classname in self.valid_classes:
                continue
            class_id = self.classinfo.increase_class_count(classname)
            
            text = " ".join(reuters.words(file))
            text = re.sub("(\d+) \. (\d+)", r"\1.\2", text)
            text = re.sub("(\d+) \, (\d+)", r"\1,\2", text)
            text = re.sub(" \.", ".", text)
            text = re.sub(" \.", ".", text)
            text = re.sub(" \,", ",", text)
            text = re.sub(" \)", ")", text)
            text = re.sub("\( ", "(", text)
            text = re.sub(" \\' ", "'", text)
            
            self.docinfo.add_document(text, class_id)
    
    def run(self):
        # Set the NLTK path (http://www.nltk.org/_modules/nltk/data.html)
        nltk_path.append(join(config.paths["rawdata"],"nltk"))
        
        try:
            # Check which classes are valid depending on min_docs_per_class
            nbprint('Loading classes')
            self.load_valid_classes()
        
            # Load the documents
            with data.document_writer(self.info) as document_writer:
                # Initialize info classes
                self.classinfo = ClassInfo()
                self.docinfo = DocumentInfo(document_writer)
                
                # Load documents and store class information in classinfo
                self.load_documents()
                
            # Print Meta Information
            self.docinfo.save_meta(self.info)
            self.classinfo.save_meta(self.info)
            
        except (LookupError, FileNotFoundError):
            raise ImporterError(info, 'Directory "{}" does not contain the required corpus.'.format(nltk_path))
            
        # Save the classes
        classes = self.classinfo.make_class_list()
        data.save_classes(classes,self.info)
        