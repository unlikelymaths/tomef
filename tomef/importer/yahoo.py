import math
from os import listdir
from os.path import join
import lxml.etree as etree

import config
import data
from base import nbprint
from util import ProgressIterator

from importer.util import ClassInfo, DocumentInfo, ImporterBase
from importer.common import ImporterError, doc_progress_label

class Document():
    def __init__(self):
        self.content = {}
        #["subject","content","bestanswer","cat","maincat","subcat"]
        self.required = ["subject","maincat"]
        
    def complete(self):
        return len(self.required) ==  0
    
    def add_elem(self, elem):
        if elem.tag == 'maincat':
            if elem.text in ['Società e culture', 'Asia Pacific']:
                return
        if elem.tag in self.required:
            self.required.remove(elem.tag)
            self.content[elem.tag] = elem.text

            
class YahooImporter(ImporterBase):
    
    def load_documents(self):
        nbprint('Loading xml file')
        
        self.documents = []
        filename = join(config.paths["rawdata"],"yahooL5/manner.xml")
        #i, max = 0, 100000
        current_doc = None
        
        for event, elem in etree.iterparse(filename, events=('start', 'end'),recover=True):
            #i = i+1
            #if i % math.floor(max/10) == 0:
            #    print(i/max)
            #if i > max:
            #    break;
            
            if elem.tag == "document":
                if event == "start":
                    current_doc = Document()    
                elif event == "end":
                    if current_doc.complete():
                        self.documents.append(current_doc)
                    current_doc = None
            elif event == "end" and not current_doc is None:
                current_doc.add_elem(elem)
                
    def save_documents(self):
        nbprint('Saving documents')
        
        self.classinfo = ClassInfo() 
        
        # Open Writer
        with data.document_writer(self.info) as document_writer:
            self.docinfo = DocumentInfo(document_writer)
            for doc in self.documents:
                text = doc.content['subject']
                class_id = self.classinfo.increase_class_count(doc.content['maincat'])
                self.docinfo.add_document(text, class_id)
            
        
                
    def run(self):
        self.load_documents()
        self.save_documents()
        
        # Save the classes
        classes = self.classinfo.make_class_list()
        data.save_classes(classes,self.info)
        
        # Print Meta Info
        self.docinfo.save_meta(self.info)
        self.classinfo.save_meta(self.info)
        