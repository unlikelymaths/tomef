from IPython.display import Markdown, HTML, DisplayHandle

style = {'description_width': '150px',}

class StyledHTML(HTML):
    """A HTML wrapper that adds css classes."""
    
    style = '''<style>
        .tdalignedlabel {width: 150px;
            text-align: left !important; 
            vertical-align: top !important;
            }
        .tdalignedvalue {width: 250px;
            text-align: left !important; 
            vertical-align: top !important;
            }
    </style>'''
    
    def __init__(self, html_string, **kwargs):
        HTML.__init__(self, StyledHTML.style + html_string, **kwargs)


class DynamicHTML():
    """A output element for displaying HTML that can be updated."""
    
    def __init__(self, html_string = '', update_display = True):
        self.handle = None
        self.set(html_string, update_display)
    
    def display(self):
        if self.handle is None:
            self.handle = DisplayHandle()
            self.handle.display(StyledHTML(self.html_string))
        else:
            self.handle.update(StyledHTML(self.html_string))
    
    def set(self, html_string, update_display = True):
        self.html_string = html_string
        if update_display:
            self.display()


class DynamicMarkdown():
    """A output element for displaying Markdown that can be updated."""
    
    def __init__(self, content = None, update_display = True, handle = None):
        self.handle = handle
        self.set(content, update_display)
    
    def display(self):
        if self.handle is None:
            self.handle = DisplayHandle()
            self.handle.display(Markdown(self.markdown))
        else:
            self.handle.update(Markdown(self.markdown))
            
    def set(self, content, update_display = True):
        if content is None:
            self.contentlist = []
            self.markdown = ''
        else:
            self.contentlist = [content]
            self.markdown = content
        if update_display:
            self.display()
        
    def push(self, content, update_display = True):
        self.contentlist.append(content)
        self.markdown = self.join((self.markdown,content))
        if update_display:
            self.display()
        
    def pop(self, update_display = True):
        self.contentlist = self.contentlist[:-1]
        self.markdown = self.join(self.contentlist)
        if update_display:
            self.display()
        
    def clear(self, update_display = True):
        self.set(None, update_display)
    
    def join(self, markdonlist):
        return '\n'.join(markdonlist)

