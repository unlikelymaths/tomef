import zipfile
import json
import tarfile
from os.path import join, isfile

import config
import data
from base import nbprint
from util import ProgressIterator

from importer.util import ClassInfo, DocumentInfo, ImporterBase
from importer.common import ImporterError, doc_progress_label

total_documents = 11000000

class TweetsODPImporter(ImporterBase):

    def parse_files(self, jsonfile):
        nbprint("Loading documents")
        for line in ProgressIterator(jsonfile):
                
            tweet = json.loads(line)
            text = tweet["full_text"]
            
            id = int(tweet["id_str"]) #id field is incorrect/rounded
            classname = self.id_to_classname[id]
            
            if (self.max_docs_per_cls is not None and 
                self.classinfo.classes.get(classname, (0,0))[1] >= self.max_docs_per_cls):
                continue
            else:
                class_id = self.classinfo.increase_class_count(classname)
                self.docinfo.add_document(text, class_id)
        
    def load_id_to_classname(self, folderpath, filename):
        nbprint("Extracting tsv")
        
        self.id_to_classname  = {}
        max_depth = self.info['data_info']['maxdepth']
        tarfilename = join(folderpath, filename + ".tar.bz2")
        
        with tarfile.open(tarfilename, "r:bz2") as tar:
            tsvfile = tar.extractfile(filename + ".tsv")
            for line in ProgressIterator(tsvfile):
                fields = line.decode().split()
                id = int(fields[0])
                classname = fields[3]
                
                classname = classname.strip("*")
                classhierarchy = classname.split("/")
                classhierarchy = classhierarchy[1:max_depth+1]
                classname = "/".join(classhierarchy)
            
                self.id_to_classname[id] = classname
                     
        
                    
    def add_data(self, filename):
        nbprint("Loading '{}'".format(filename)).push()
        folderpath = join(config.paths["rawdata"],"tweetsodp")
        jsonfilename = join(folderpath, filename + ".json")
        zipfilename = join(folderpath, filename + ".json.zip")
        
        self.load_id_to_classname(folderpath, filename)
        if isfile(jsonfilename):
            with open(jsonfilename,"r") as jsonfile:
                self.parse_files(jsonfile)
        else:
            with zipfile.ZipFile(zipfilename) as zip:
                with zip.open(filename + ".json") as jsonfile:
                    self.parse_files(jsonfile)
        nbprint.pop()
                                  
    def run(self):
        self.classinfo = ClassInfo()
        self.max_docs_per_cls = self.info['data_info'].get('max_docs_per_cls', None)
        with data.document_writer(self.info) as document_writer:
            self.docinfo = DocumentInfo(document_writer)
            self.add_data("ODPtweets-Mar17-29")
            self.add_data("ODPtweets-Apr12-24")
        
        # Save the classes
        classes = self.classinfo.make_class_list()
        data.save_classes(classes,self.info)
        
        # Print Meta Info
        self.docinfo.save_meta(self.info)
        self.classinfo.save_meta(self.info)
        