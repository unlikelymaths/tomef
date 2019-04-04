from IPython.display import display, Markdown, Latex, HTML
import traceback

class NotebookPrinter():
    markdown_prefix = ['\n## ',
                       '\n#### ', 
                       '\n']
    
    def __init__(self, default_level = 0):
        self._element = None
        self.default_level = default_level
        self.reset()
    
    def reset(self):
        self.level = self.default_level
        
    def push(self):
        self.level += 1
        return self
        
    def pop(self):
        self.level -= 1
        return self
        
    def setelement(self, element):
        self._element = element
        self.reset()
    
    def print(self, string, prefix = True):
        string = str(string)
        if self._element is None:
            if prefix:
                string = '  '*self.level + string
            print(string)
        else:
            if prefix:
                if self.level < len(NotebookPrinter.markdown_prefix):
                    string = NotebookPrinter.markdown_prefix[self.level] + string
                else:
                    diff = self.level - len(NotebookPrinter.markdown_prefix)
                    string = '  '*diff + '- ' + string
            self._element.update(string)
        return self
    
    __call__ = print
    
    def clear(self):
        self.reset()
        if self._element is None:
            pass
        else:
            self._element.clear()
            
    def clear_last(self):
        if self._element is None:
            pass
        else:
            self._element.revert_one()
            
    def print_traceback(self):
        self.print(traceback.format_exc().replace('\n','<br>\n'), prefix = False)

nbprint = NotebookPrinter()
    
def nbdict(dictionary):
    string = ""
    for key, value in dictionary.items():
        string += '**{}**  \n > {}  \n\n'.format(key, value)
    display(Markdown(string))