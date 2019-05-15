from os.path import join
from os import listdir

from base import config, data
from widgets import ProgressIterator

from importer.util import ClassInfo, DocumentInfo, ImporterBase
from importer.common import ImporterError, doc_progress_label


class ClassicImporter(ImporterBase):
    
    def load_file(self, filename):
        filename = join(self.folder,filename)
        with open(filename,"r", encoding="utf8") as file:
            text = file.read()
        return text
        
    def load_documents(self):
        for filename in ProgressIterator(self.files, doc_progress_label):
            classname = filename.split(".")[0]
            class_id = self.classinfo.increase_class_count(classname)
            text = self.load_file(filename)
            self.docinfo.add_document(text, class_id)
    
    def run(self):
        # Get all files in the classic4 directory
        self.folder = join(config.paths["rawdata"],"classic4")
        try:
            self.files = listdir(self.folder)
        except FileNotFoundError:
            raise ImporterError(info, 'Directory "{}" does not exist'.format(self.folder))
            
        
        # Remove .gitignore file from list
        self.files = [file for file in self.files if file != '.gitignore']
        
        # Keep only files that start with a classname
        self.classnames = ['cacm','cisi','cran','med']
        self.files = [file for file in self.files if '.' in file and file.split('.')[0] in self.classnames]
        
        # Check if files exits
        if len(self.files) == 0:
            raise ImporterError(info, 'There are no valid files in the folder.')
        
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
    