from util import print_progress, clear_progress
from dataimport.util import make_class, make_document, make_dataset
import config
import data
from os.path import join
from os import listdir
#import xml.etree.ElementTree as etree
import lxml.etree as etree

import math
def import_dblp(data_name, info):
    documents = []
    classinfos = {}
    
    filename = join(config.paths["rawdata"],"dblp/dblp-2018-11-01.xml")
    tags = {}
    #xmlp = etree.XMLParser(encoding="ISO-8859-1")
    #xmlp = etree.XMLParser(recover=True)
    i = 0
    max = 10000000
    depth = 0
    for event, elem in etree.iterparse(filename, events=('start', 'end'),recover=True):
        i = i+1
        
        if i % math.floor(max/100) == 0:
            print(i/max)
            
        if i > max:
            break;
        
        if depth == 1:
            tags[elem.tag] = 0
            elem.clear()
            
        if event == "start":
            depth += 1
        elif event == "end":
            depth -= 1
        
        
        
    for tag in tags:
        print(tag)
        
        
