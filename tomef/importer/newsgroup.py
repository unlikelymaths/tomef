from os.path import join
from sklearn.datasets import fetch_20newsgroups

from base import config, data
from widgets import nbprint, ProgressIterator

from importer.util import ClassInfo, DocumentInfo, ImporterBase
from importer.common import doc_progress_label

class NewsgroupImporter(ImporterBase):
        
    def load_documents(self):
        text_class_pairs = zip(self.rawdata.data, self.rawdata.target)
        for text, class_idx in ProgressIterator(text_class_pairs, 
                                                doc_progress_label,
                                                length = len(self.rawdata.data)):
            classname = self.rawdata.target_names[class_idx]
            class_id = self.classinfo.increase_class_count(classname)
            self.docinfo.add_document(text, class_id)
            
    def run(self):
        # Load data with sklearn
        nbprint('Loading raw files')
        self.rawdata = fetch_20newsgroups(
            data_home = join(config.paths['rawdata'],'sklearn'),
            remove = tuple(self.info['data_info']['remove']),
            subset = 'all')
        
        with data.document_writer(self.info) as document_writer:
            # Initialize info classes
            self.classinfo = ClassInfo()
            self.docinfo = DocumentInfo(document_writer)
            
            # Load documents and store class information in classinfo
            self.load_documents()
            
        # Print Meta Information
        self.docinfo.save_meta(self.info)
        self.classinfo.save_meta(self.info)
        
        # Save classinfo
        classes = self.classinfo.make_class_list()
        data.save_classes(classes,self.info)
        