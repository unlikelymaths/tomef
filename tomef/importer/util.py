from scipy.stats import skew
from numpy import std

from base import data
from widgets import nbprint

class ImporterBase():
    def __init__(self, info):
        self.info = info

class ClassInfo():
    
    def __init__(self):
        self.classes = {}
        
    def increase_class_count(self, classname, count=1):
        idx = None
        if classname in self.classes:
            idx, old_count = self.classes[classname]
            self.classes[classname] = (idx, old_count + count)
        else:
            idx = len(self.classes)
            self.classes[classname] = (idx,count)
        return idx
            
    def make_class_list(self):
        class_list = []
        for classname,classinfo in self.classes.items():
            class_dict = {'class_id': classinfo[0],
                          'info': classname,
                          'count': classinfo[1]}
            class_list.append(class_dict)
        return class_list
    
    def save_meta(self, info):
        class_counts = [classinfo[1] for classname,classinfo in self.classes.items()]
            
        class_meta = {
            'num_classes':         len(self.classes),
            'min_docs_per_class':  min(class_counts),
            'max_docs_per_class':  max(class_counts),
            'mean_docs_per_class': sum(class_counts) / len(self.classes),
            'standard_deviation':  std(class_counts),
            'skewness':            skew(class_counts),
        }
        
        nbprint('Number of classes: {}'.format(class_meta['num_classes']))
        nbprint('Smallest class:    {}'.format(class_meta['min_docs_per_class']))
        nbprint('Largest class:     {}'.format(class_meta['max_docs_per_class']))
        nbprint('Class size mean: {:.1f}'.format(class_meta['mean_docs_per_class']))
        nbprint('Class size standard deviation: {:.1f}'.format(class_meta['standard_deviation']))
        nbprint('Class size skewness: {:.3f}'.format(class_meta['skewness']))
        
        data.save_class_meta(class_meta, info)
        
        
class DocumentInfo():
    def __init__(self, document_writer):
        self.document_writer = document_writer
        self.num_documents = 0
        self.num_words = 0
        self.num_characters = 0
        
    def add_document(self, text, class_id = None, id = None):
        if id is None:
            id = self.num_documents
        
        self.num_documents += 1
        self.num_words += len(text.split(' '))
        self.num_characters += len(text)
        
        doc_dict = {"id": id,
            "text": text, 
            "class_id": class_id
            }
        self.document_writer.write(doc_dict)
        
    def save_meta(self, info):
        document_meta = {
            'num_documents':  self.num_documents,
            'avg_words':      self.num_words / self.num_documents,
            'avg_characters': self.num_characters / self.num_documents,
        }
        
        nbprint('Number of documents: {}'.format(document_meta['num_documents']))
        nbprint('Average words per document: {:.1f}'.format(document_meta['avg_words']))
        nbprint('Average characters per document: {:.1f}'.format(document_meta['avg_characters']))
        
        data.save_document_meta(document_meta, info)