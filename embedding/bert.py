import torch
import numpy as np
import pytorch_pretrained_bert
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler

from embedding.embedding_model import PhraseembeddingModel

MODEL_NAME = 'bert-base-multilingual-cased'
CACHE_DIR = './data/embedding'
BATCH_SIZE = 64
DEVICE = torch.device('cpu')
layer_indexes = [0]

class InputFeatures(object):
    """A single set of features of data."""
    def __init__(self, unique_id, tokens, input_ids, input_mask, input_type_ids):
        self.unique_id = unique_id
        self.tokens = tokens
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.input_type_ids = input_type_ids

class BertModel(PhraseembeddingModel):
    def __del__(self):
        self.model = None

    def _load_model(self):
        # Load pre-trained model tokenizer (vocabulary)
        self.tokenizer = pytorch_pretrained_bert.BertTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
        # Get Model   
        self.model = pytorch_pretrained_bert.BertModel.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
        self.model.to(DEVICE)
        self.model.eval()
        
    def tokenize(self, texts):
        tokenized_texts = []
        max_length = 0
        for text in texts:
            tokens = ['[CLS]'] + self.tokenizer.tokenize(text) + ['[SEP]']
            tokenized_texts.append(tokens)
            max_length = max(max_length, len(tokens))
        return tokenized_texts, max_length
    
    def get_features(self, texts):
        tokenized_texts, max_length = self.tokenize(texts)
        
        max_length = 64
        
        features = []
        for id, tokens in enumerate(tokenized_texts):
            if len(tokens) > 512:
                tokens = tokens[:512]
            input_ids = self.tokenizer.convert_tokens_to_ids(tokens)
            input_type_ids = [0] * len(input_ids)
            input_mask = [1] * len(input_ids)
            
            # Zero-pad up to the sequence length.
            while len(input_ids) < max_length:
                input_ids.append(0)
                input_type_ids.append(0)
                input_mask.append(0)
            
            input_ids = input_ids[:max_length]
            input_type_ids = input_type_ids[:max_length]
            input_mask = input_mask[:max_length]
            
            features.append(
                InputFeatures(
                    unique_id=id,
                    tokens=tokens,
                    input_ids=input_ids,
                    input_mask=input_mask,
                    input_type_ids=input_type_ids))
        return features
    
    def make_dataloader(self, features):
        all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
        all_example_index = torch.arange(all_input_ids.size(0), dtype=torch.long)
        eval_data = TensorDataset(all_input_ids, all_input_mask, all_example_index)
        eval_sampler = SequentialSampler(eval_data)
        eval_dataloader = DataLoader(eval_data, sampler=eval_sampler, batch_size=BATCH_SIZE)
        return eval_dataloader
    
    def extract_matrix(self, features, eval_dataloader):
        mat = None
        for input_ids, input_mask, example_indices in eval_dataloader:
            input_ids = input_ids.to(DEVICE)
            input_mask = input_mask.to(DEVICE)
        
            all_encoder_layers, _ = self.model(input_ids, token_type_ids=None, attention_mask=input_mask)
        
            for b, example_index in enumerate(example_indices):
                feature = features[example_index.item()]
                unique_id = int(feature.unique_id)
                
                last_layer = all_encoder_layers[-1].detach().cpu().numpy()[b]
                vector = last_layer[0]
                
                if mat is None:
                    mat = np.zeros((vector.shape[0], len(features)))
                
                mat[:,unique_id] = vector
            #print('{}/{}'.format(unique_id, len(features)))
        return mat
    
    def _embed(self, messages):
        # Transform texts into features
        #print('Extracting Features')
        features = self.get_features(messages)
        # Make Dataloader
        #print('Making Dataloader')
        eval_dataloader = self.make_dataloader(features)
        # Get Matrix
        #print('Making Matrix')
        mat = self.extract_matrix(features, eval_dataloader)
        return mat.T
    
    def _vector_size(self):
        return self.embed(['Test String']).shape[1]