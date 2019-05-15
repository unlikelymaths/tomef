from ipywidgets.widgets import FloatProgress
from widgets.display import DynamicMarkdown, style

_dynamic_text_widget = None
_progress_widget = None
_last_prefix_length = 0

class MarkdownPrinter():
    """A printer class that optionally prints to _dynamic_text_widget.
    
    If no _dynamic_text_widget is set a call to print will result in a standard
    print. Otherwise it will call the push function of the _dynamic_text_widget.
    The clear and pop methods are only supported on _dynamic_text_widget and will
    remove all output (clear) or the last printed string (clear_last). The 
    has_markdown property can be used to check if the output will go to a 
    _dynamic_text_widget.
    """
    
    @property
    def markdown(self):
        return _dynamic_text_widget
        
    @property
    def has_markdown(self):
        return (_dynamic_text_widget is not None)
    
    def print(self, text):
        if self.has_markdown:
            text = str(text).replace('\n','<br>\n')
            self.markdown.push(text)
        else:
            print(text)
        return self
    __call__ = print
    
    def clear(self):
        if self.has_markdown:
            self.markdown.clear()
            
    def clear_last(self):
        if self.has_markdown:
            self.markdown.pop()
            
    def print_traceback(self):
        return self.print(traceback.format_exc())


class NotebookPrinter(MarkdownPrinter):
    """A printer class extending MarkdownPrinter with indentation functionality
    
    If no markdown element is set a call to print will result in a standard
    print. Otherwise it will call the push function of the markdown element.
    The clear and pop methods are only supported on markdown elements and will
    remove all output (clear) or the last printed string (clear_last). The 
    has_markdown property can be used to check if the output will go to a 
    markdown element.
    """
    
    def __init__(self):
        super().__init__()
        self.level = 0
            
    def push(self):
        self.level += 1
        return self
        
    def pop(self):
        self.level = max((self.level - 1, 0))
        return self
        
    def print(self, text):
        text = str(text)
        if self.has_markdown:
            if self.level > 0:
                text = '  '*(self.level-1) + '- ' + text
        else:
            text = '  '*self.level + text
        return super().print(text)
    __call__ = print
notebook_printer = NotebookPrinter()

def print_progress(progress, prefix = ""):
    global _last_prefix_length, _progress_widget
    if _progress_widget is None:
        _last_prefix_length = len(prefix)
        progress = max(min(1,progress),0)
        print("\r{0}[{1:50s}] {2:.1f}%"
            .format(prefix,'#' * int(progress * 50), progress*100), end="", flush=True)
    else:
        _progress_widget.layout.visibility = 'visible'
        _progress_widget.description = prefix
        _progress_widget.value = progress


def clear_progress():
    global _last_prefix_length, _progress_widget
    if _progress_widget is None:
        print("\r{}".format(" "*(_last_prefix_length + 60)), end="", flush=True)
        print("\r", end="", flush=True)
    else:
        _progress_widget.layout.visibility = 'hidden'
        _progress_widget.value = 0


class NotebookBox():
    """Provides a markdown area and a progress widget"""
    
    def __enter__(self):
        global _dynamic_text_widget, _progress_widget
        # Create and display markdown element and float progress widget
        self.dynamic_markdown = DynamicMarkdown()
        self.progress_widget = FloatProgress(
            value=0,min=0,max=1,step=0.01,
            description='',bar_style='info',orientation='horizontal',
            style=style)
        self.progress_widget.layout.visibility = 'hidden'
        display(self.progress_widget)
        
        # Make them current
        _dynamic_text_widget = self.dynamic_markdown
        _progress_widget = self.progress_widget

        # Reset Level
        notebook_printer.level = 0
        
    def __exit__(self, type, value, traceback):
        global _dynamic_text_widget, _progress_widget
        # Unregister widgets
        _dynamic_text_widget = None
        _progress_widget = None
        
        # Close widgets
        self.progress_widget.close()
        
        # Reset Level
        notebook_printer.level = 0