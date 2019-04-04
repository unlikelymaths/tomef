import data

class ModelBase:
    def __init__(self, info):
        self.info = info
        self.input_mat = None
        self.current_output = None
        self.meta = None
    
    def output_of(self, info):
        self.current_output = self._output_of(info) or []
        return self.current_output
        
    def run(self, info):
        self.input_mat = data.load_input_mat(info)
        self._run(info)
            
    def output_exists(self, info):
        exists = True
        if 'W' in self.current_output:
            exists = exists and data.w_mat_exists(info)
        if 'H' in self.current_output:
            exists = exists and data.h_mat_exists(info)
        if 'c' in self.current_output:
            exists = exists and data.c_vec_exists(info)
        return exists
        
        
    def save(self, info):
        if 'W' in self.current_output:
            data.save_w_mat(self.W, info)
            self.W = None
        if 'H' in self.current_output:
            data.save_h_mat(self.H, info)
            self.H = None
        if 'c' in self.current_output:
            data.save_c_vec(self.c, info)
            self.c = None
        if self.meta is not None:
            data.save_model_meta(self.meta, info)