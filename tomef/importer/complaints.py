import csv
from os.path import join

from base import config, data
from interface import ProgressIterator

from importer.util import ClassInfo, DocumentInfo, ImporterBase
from importer.common import ImporterError, doc_progress_label

# Table Fields:
# 00 date_received
# 01 product
# 02 sub_product
# 03 issue
# 04 sub_issue
# 05 consumer_complaint_narrative
# 06 company_public_response
# 07 company
# 08 state
# 09 zipcode
# 10 tags
# 11 consumer_consent_provided 
# 12 submitted_via
# 13 date_sent_to_company
# 14 company_response_to_consumer
# 15 timely_response
# 16 consumer_disputed?
# 17 complaint_id

class ComplaintsImporter(ImporterBase):
           
    def load_classes(self, file):
        self.valid_classes = ClassInfo()
        min_length = self.info['data_info']['min_length']
        cr = csv.reader(file)
        next(cr)
        for row in ProgressIterator(cr):
            classname = row[2]
            text = row[5]
            
            if len(text) >= min_length:
                self.valid_classes.increase_class_count(classname)
        min_class_size = self.info['data_info']['min_class_size']
        self.valid_classes = [c['info'] 
                              for c in self.valid_classes.make_class_list() 
                              if c['count'] > min_class_size]
        
    def load_data(self, file):
        min_length = self.info['data_info']['min_length']
        cr = csv.reader(file)
        next(cr)
        for row in ProgressIterator(cr):
            classname = row[2]
            text = row[5]
            
            if len(text) >= min_length and classname in self.valid_classes:
                class_id = self.classinfo.increase_class_count(classname)
                self.docinfo.add_document(text, class_id)
            
            
    def run(self):
        self.classinfo = ClassInfo()
        filename = join(config.paths["rawdata"],"complaints/consumer_complaints.csv")
        
        with open(filename) as file:
            self.load_classes(file)
        
        with data.document_writer(self.info) as document_writer:
            self.docinfo = DocumentInfo(document_writer)
            with open(filename) as file:
                self.load_data(file)
            
        # Save the classes
        classes = self.classinfo.make_class_list()
        data.save_classes(classes,self.info)
        
        # Print Meta Info
        self.docinfo.save_meta(self.info)
        self.classinfo.save_meta(self.info)
        