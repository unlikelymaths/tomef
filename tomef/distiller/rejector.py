import random

class Rejector:
    def __init__(self, reject_probabiliy = 1, seed=42):
        self.reject_probabiliy= reject_probabiliy
        random.seed(seed)
        self.state = random.getstate()
        
    def reject(self):
        random.setstate(self.state)
        number = random.random()
        self.state = random.getstate()
        return number < self.reject_probabiliy     
    
    def allow(self):
        return not self.reject()