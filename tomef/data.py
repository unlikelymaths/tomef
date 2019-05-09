import config
from os.path import join, isfile, isdir
from os import listdir, remove
import re
import json
import numpy as np
from scipy.io import savemat
from scipy import sparse
from distiller.common import TopicEntry

something_blue = 42

###############################################################################
# General
###############################################################################

class JsonArrayWriter():
    def __init__(self,filename):
        self.filename = filename
        self.entries = 0

    def __enter__(self):
        self.file = open(self.filename, "w", encoding="utf-8")
        self.file.write("[\n\t")
        return self
        
    def __exit__(self, type, value, traceback):
        self.file.write("\n]")
        self.file.close()
    
    def write(self,data):
        if self.entries:
            self.file.write(",\n\t")
        self.entries += 1
        jsonstr = json.dumps(data)
        self.file.write(jsonstr)
        
class JsonArrayIterator:
    def __init__(self, file):
        self.file = file
        self.length = None
    
    def __len__(self):
        if self.length is None:
            self.length = 0
            pos = self.file.tell()
            self.file.seek(0)
            for line in self.file:
                if not (line.startswith("[") or line.startswith("]")):
                    self.length += 1
            self.file.seek(pos)
        return self.length
        
    def __iter__(self):
        self.file.seek(0)
        return self

    def __next__(self):
        line = self.file.readline()
        while line.startswith("[") or line.startswith("]"):
            line = self.file.readline()
        line = line.rstrip("\n").rstrip(",")
        try:
            data = json.loads(line)
        except json.decoder.JSONDecodeError:
            raise StopIteration
        return data
        
class JsonArrayReader():
    def __init__(self,filename):
        self.filename = filename
        self.entries = 0

    def __enter__(self):
        self.file = open(self.filename, "r", encoding="utf-8")
        self.iterator = JsonArrayIterator(self.file)
        return self.iterator
        
    def __exit__(self, type, value, traceback):
        self.file.close()

def _load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)
        
def _save_json(data,filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def first_array_in(npz_filename):
    npz_file = np.load(npz_filename)
    return npz_file[npz_file.files[0]] #pick the first array in the file
    
###############################################################################
# Removing
###############################################################################

def clear_file(filename):
    if isfile(filename):
        remove(filename)

###############################################################################
# Embedding
###############################################################################

def embedding_filename(info):
    return join(config.paths["embedding"], info['embedding_info']['filename'])
 
def embedding_file_exists(info):
    return isfile(embedding_filename(info))
    
def embedding_dir_exists(info):
    return isdir(embedding_filename(info))
    
def embedding_meta_filename(meta, info):
    return join(config.paths["embedding"], '{}.{}.json'.format(
        info['embedding_name'], meta))
    
def embedding_meta_exists(meta, info):
    return isfile(embedding_meta_filename(meta, info))

def save_embedding_meta(vocab, meta, info):
    _save_json(vocab,embedding_meta_filename(meta, info))
        
def load_embedding_meta(meta, info):
    return _load_json(embedding_meta_filename(meta, info))
    
###############################################################################
# Importer
###############################################################################

# documents

def documents_filename(info):
    return join(config.paths["imported"], "{}_documents.json"
        .format(info["data_name"]))

def documents_exists(info):
    return isfile(documents_filename(info))

class document_writer(JsonArrayWriter):
    def __init__(self, info):
        self.info = info
        super().__init__(filename = documents_filename(info))

class document_reader(JsonArrayReader):
    def __init__(self, info):
        self.info = info
        super().__init__(filename = documents_filename(info))
        
# classes
        
def classes_filename(info):
    return join(config.paths["imported"], "{}_classes.json"
        .format(info["data_name"]))

def classes_exists(info):
    return isfile(classes_filename(info))

def save_classes(classes, info):
    _save_json(classes,classes_filename(info))
        
def load_classes(info):
    return _load_json(classes_filename(info))

# document meta

def document_meta_filename(info):
    return join(config.paths["imported"], "{}_documents_meta.json"
        .format(info["data_name"]))

def save_document_meta(document_meta, info):
    _save_json(document_meta,document_meta_filename(info))
        
def load_document_meta(info):
    return _load_json(document_meta_filename(info))

# class meta

def class_meta_filename(info):
    return join(config.paths["imported"], "{}_classes_meta.json"
        .format(info["data_name"]))

def save_class_meta(class_meta, info):
    _save_json(class_meta,class_meta_filename(info))
        
def load_class_meta(info):
    return _load_json(class_meta_filename(info))


###############################################################################
# Wiki
###############################################################################

def wiki_dict_filename():
    return join(config.paths["wiki"], "wikidump_{}_wordids.txt.bz2"
        .format(config.im["numbers"]))
        
def wiki_corpus_filename():
    return join(config.paths["wiki"], "wikidump_{}_bow.mm"
        .format(config.im["numbers"]))

###############################################################################
# Tokenizer
###############################################################################

# documents

def tokenized_document_filename(info):
    return join(config.paths["tokenized"], "{}_t{}_documents.json"
        .format(info["data_name"], info["token_version"]))

def tokenized_document_exists(info):
    return isfile(tokenized_document_filename(info))

class tokenized_document_writer(JsonArrayWriter):
    def __init__(self, info):
        super().__init__(filename = tokenized_document_filename(info))

class tokenized_document_reader(JsonArrayReader):
    def __init__(self, info):
        super().__init__(filename = tokenized_document_filename(info))

# excluded
    
def excluded_tokens_filename(info):
    return join(config.paths["tokenized"], "{}_t{}_excluded.txt"
        .format(info["data_name"], info["token_version"]))

def save_excluded_tokens(tokens, info):
    with open(excluded_tokens_filename(info), "w") as file:
        for token in tokens:
            file.write("{:4d}: {}\n".format(token[1],token[0]))
            
###############################################################################
# Vocab
###############################################################################

# vocabulary

def vocab_filename(info):
    return join(config.paths["vocab"], "{}_t{}_v{}_vocab.json"
        .format(info["data_name"], info["token_version"], info["vocab_version"]))

def vocab_exists(info):
    return isfile(vocab_filename(info))

def save_vocab(vocab, info):
    _save_json(vocab,vocab_filename(info))
        
def load_vocab(info):
    return _load_json(vocab_filename(info))

def load_vocab_dict(info):
    return {entry['token']: entry for entry in load_vocab(info)}

def load_vocab_list(info):
    return [entry['token'] for entry in load_vocab(info)]
    
###############################################################################
# Vectorizer
###############################################################################

def data_token_vocab_vector_base(info):
    bcp = config.split(info['vector_version'])[0]
    if bcp == 'B' or bcp == 'C':
        return '{}_Tok{}_Voc{}_Vec{}'.format(
            info['data_name'], info['token_version'], info['vocab_version'], info['vector_version'])
    elif bcp == 'P':
        return '{}_Vec{}'.format(
            info['data_name'], info['vector_version'])

# mat_ids

def mat_ids_filename(info):
    return join(config.paths["vectorized"], "{}_Tok{}_Voc{}_ids.json"
        .format(info["data_name"], info["token_version"], info["vocab_version"]))

def save_mat_ids(mat_ids, info):
    _save_json(mat_ids,mat_ids_filename(info))
        
def load_mat_ids(info):
    return _load_json(mat_ids_filename(info))

# input mat

def input_mat_filename(info):
    return join(config.paths["vectorized"], data_token_vocab_vector_base(info) + '_mat.npz')
        
def input_mat_exists(info):
    return isfile(input_mat_filename(info))
       
def save_sparse_input_mat(input_mat, info):     
    sparse.save_npz(input_mat_filename(info), input_mat)
    
def save_dense_input_mat(input_mat, info):   
    np.savez_compressed(input_mat_filename(info), input_mat)

def load_input_mat(info):
    bcp = config.split(info["vector_version"])[0]
    if bcp == 'B':
        return sparse.load_npz(input_mat_filename(info))
    elif bcp == 'C' or bcp == 'P':
        return first_array_in(input_mat_filename(info))
        
###############################################################################
# Models
###############################################################################

# W

def w_mat_filename(info):
    return join(config.paths["models"],data_token_vocab_vector_base(info) + '_{}_Top{}_w.npz'
        .format(info['model_name'],info['num_topics']))

def w_mat_exists(info):
    return isfile(w_mat_filename(info))

def save_w_mat(w_mat, info):
    np.savez_compressed(w_mat_filename(info), w_mat)
    
def load_w_mat(info):
    return first_array_in(w_mat_filename(info))

def get_all_w_mat_infos():
    w_mat_infos = []
    pattern = '([^_]+)_Tok([^_]+)_Voc([^_]+)_Vec([^_]+)_([^_]+)_Top([^_]+)_w.npz'
    prog = re.compile(pattern)
    for fn in listdir(config.paths["models"]):
        m = prog.match(fn)
        if m:
            w_mat_infos.append({
                    "data_name": m.group(1),
                    "token_version": m.group(2),
                    "vocab_version": m.group(3),
                    "vector_version": m.group(4),
                    "model_name": m.group(5),
                    "num_topics": int(m.group(6)),
                })
    return w_mat_infos

# H

def h_mat_filename(info):
    return join(config.paths["models"],data_token_vocab_vector_base(info) + '_{}_Top{}_h.npz'
        .format(info['model_name'],info["num_topics"]))

def h_mat_exists(info):
    return isfile(h_mat_filename(info))

def save_h_mat(topic_doc_mat, info):
    np.savez_compressed(h_mat_filename(info), topic_doc_mat)
    
def load_h_mat(info):
    return first_array_in(h_mat_filename(info))

def get_all_h_mat_infos(labeled_only):
    h_mat_infos = []
    pattern1 = '([^_]+)_Tok([^_]+)_Voc([^_]+)_Vec([^_]+)_([^_]+)_Top([^_]+)_h.npz'
    pattern2 = '([^_]+)_Vec([^_]+)_([^_]+)_Top([^_]+)_h.npz'
    prog1 = re.compile(pattern1)
    prog2 = re.compile(pattern2)
    for fn in listdir(config.paths["models"]):
        m1 = prog1.match(fn)
        m2 = prog2.match(fn)
        if m1:
            if labeled_only and config.datasets[m1.group(1)]['labels'] == False:
                continue
            h_mat_infos.append({
                    "data_name": m1.group(1),
                    "token_version": m1.group(2),
                    "vocab_version": m1.group(3),
                    "vector_version": m1.group(4),
                    "model_name": m1.group(5),
                    "num_topics": int(m1.group(6)),
                })
        elif m2:
            if labeled_only and config.datasets[m2.group(1)]['labels'] == False:
                continue
            h_mat_infos.append({
                    "data_name": m2.group(1),
                    "vector_version": m2.group(2),
                    "model_name": m2.group(3),
                    "num_topics": m2.group(4),
                })
    return h_mat_infos

# c

def c_vec_filename(info):
    return join(config.paths["models"],data_token_vocab_vector_base(info) + '_{}_Top{}_c.npz'
        .format(info['model_name'],info["num_topics"]))

def c_vec_exists(info):
    return isfile(c_vec_filename(info))

def save_c_vec(c_vec, info):
    np.savez_compressed(c_vec_filename(info), c_vec)
    
def load_c_vec(info):
    return first_array_in(c_vec_filename(info))

def get_all_c_vec_infos(labeled_only):
    c_vec_infos = []
    pattern1 = '([^_]+)_Tok([^_]+)_Voc([^_]+)_Vec([^_]+)_([^_]+)_Top([^_]+)_c.npz'
    pattern2 = '([^_]+)_Vec([^_]+)_([^_]+)_Top([^_]+)_c.npz'
    prog1 = re.compile(pattern1)
    prog2 = re.compile(pattern2)
    for fn in listdir(config.paths["models"]):
        m1 = prog1.match(fn)
        m2 = prog2.match(fn)
        if m1:
            if labeled_only and config.datasets[m1.group(1)]['labels'] == False:
                continue
            c_vec_infos.append({
                    "data_name": m1.group(1),
                    "token_version": m1.group(2),
                    "vocab_version": m1.group(3),
                    "vector_version": m1.group(4),
                    "model_name": m1.group(5),
                    "num_topics": int(m1.group(6)),
                })
        elif m2:
            if labeled_only and config.datasets[m2.group(1)]['labels'] == False:
                continue
            c_vec_infos.append({
                    "data_name": m2.group(1),
                    "vector_version": m2.group(2),
                    "model_name": m2.group(3),
                    "num_topics": m2.group(4),
                })
    return c_vec_infos

# Meta

def model_meta_filename(info):
    return join(config.paths["models"],data_token_vocab_vector_base(info) + '_{}_Top{}_meta.json'
        .format(info['model_name'],info['num_topics']))

def model_meta_exists(info):
    return isfile(w_mat_filename(info))

def save_model_meta(model_meta, info):
    _save_json(model_meta,model_meta_filename(info))
    
def load_model_meta(info):
    return _load_json(model_meta_filename(info))


###############################################################################
# Topics
###############################################################################

def topiclist_filename(info):
    if 'second_info' in info:
        second_info = info['second_info']
        return join(config.paths["topics"],data_token_vocab_vector_base(info) + '_{}_Top{}_{}(Tok{}_Voc{}_Vec{}).json'
            .format(info['model_name'],info['num_topics'],info['distiller_name'],
                    second_info['token_version'],second_info['vocab_version'],second_info['vector_version']))
    else:
        return join(config.paths["topics"],data_token_vocab_vector_base(info) + '_{}_Top{}_{}.json'
            .format(info['model_name'],info['num_topics'],info['distiller_name']))

def topiclist_exists(info):
    return isfile(topiclist_filename(info))

def save_topiclist(topiclist, info):
    _save_json(topiclist,topiclist_filename(info))
        
def load_topiclist(info):
    topiclist_raw = _load_json(topiclist_filename(info))
    return [[TopicEntry(*entry) for entry in topic] for topic in topiclist_raw]

def get_all_topiclist_infos():
    topiclist_infos = []
    pattern1 = '([^_]+)_Tok([^_]+)_Voc([^_]+)_Vec([^_]+)_([^_]+)_Top([^_]+)_([^_]+)(?:\(Tok([^_]+)_Voc([^_]+)_Vec([^_]+)\))?.json'
    pattern2 = '([^_]+)_Vec([^_]+)_([^_]+)_Top([^_]+)_([^_]+)(?:\(Tok([^_]+)_Voc([^_]+)_Vec([^_]+)\))?.json'
    prog1 = re.compile(pattern1)
    prog2 = re.compile(pattern2)
    for fn in listdir(config.paths["topics"]):
        m1 = prog1.match(fn)
        m2 = prog2.match(fn)
        if m1:
            info = {
                "data_name": m1.group(1),
                "token_version": m1.group(2),
                "vocab_version": m1.group(3),
                "vector_version": m1.group(4),
                "model_name": m1.group(5),
                "num_topics": m1.group(6),
                "distiller_name": m1.group(7),
            }
            if (len(m1.groups()) >= 10 and 
                m1.group(8) is not None and
                m1.group(9) is not None and
                m1.group(10) is not None):
                info['second_info'] = {
                    "token_version": m1.group(8),
                    "vocab_version": m1.group(9),
                    "vector_version": m1.group(10),
                }
            topiclist_infos.append(info)
        elif m2:
            info = {
                "data_name": m2.group(1),
                "vector_version": m2.group(2),
                "model_name": m2.group(3),
                "num_topics": m2.group(4),
                "distiller_name": m2.group(5),
            }
            if (len(m2.groups()) >= 8 and 
                m2.group(6) is not None and
                m2.group(7) is not None and
                m2.group(8) is not None):
                info['second_info'] = {
                    "token_version": m2.group(6),
                    "vocab_version": m2.group(7),
                    "vector_version": m2.group(8),
                }
            topiclist_infos.append(info)
    return topiclist_infos

###############################################################################
# Metrics
###############################################################################

# Clustering Metrics

def metric_data_filename(file):
    return join(config.paths["results"],"metrics/{}.json".format(file))

def metric_data_exists(file):
    return isfile(metric_data_filename(file))

def save_metric_data(metric_data, file):
    _save_json(metric_data, metric_data_filename(file))
    
def load_metric_data(file):
    if metric_data_exists(file):
        return _load_json(metric_data_filename(file))
    return []