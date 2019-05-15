from widgets.printer import print_progress, clear_progress


class ProgressIterator:
    def __init__(self, sequence, prefix = "", print_every = 100, length = None):
        self.prefix = prefix
        self.print_every = print_every
        self.sequence = sequence
        self.length = length
        self.pseudo = False
        
    def __del__(self):
        clear_progress()
        
    def __iter__(self):
        if self.length is None:
            try:
                self.length = len(self.sequence)
            except:
                self.pseudo = True
                self.direction = 1
                self.current = 0
        self.iter = enumerate(iter(self.sequence))
        return self

    def __next__(self):
        idx, object = next(self.iter)
        if idx%self.print_every == 0:
            if self.pseudo:
                print_progress(self.current/100, self.prefix)
                if self.current >= 100:
                    self.direction = -1
                elif self.current <= 0:
                    self.direction = 1
                self.current += self.direction
            else:
                print_progress(idx/self.length, self.prefix)
        return object    
        
class EnumerateProgressIterator:
    def __init__(self, sequence, prefix = "", print_every = 100, length = None):
        self.prefix = prefix
        self.print_every = print_every
        self.sequence = sequence
        self.length = length
        self.pseudo = False
        
    def __iter__(self):
        if self.length is None:
            try:
                self.length = len(self.sequence)
            except:
                self.pseudo = True
                self.direction = 1
                self.current = 0
        self.iter = enumerate(iter(self.sequence))
        return self

    def __next__(self):
        try:
            idx, object = next(self.iter)
        except StopIteration:
            clear_progress()
            raise StopIteration
        if idx%self.print_every == 0:
            if self.pseudo:
                print_progress(self.current/100, self.prefix)
                if self.current >= 100:
                    self.direction = -self.direction
                elif self.current <= 0:
                    self.direction = -self.direction
                self.current += self.direction
            else:
                print_progress(idx/self.length, self.prefix)
        return idx, object    