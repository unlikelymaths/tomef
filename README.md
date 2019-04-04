# Evaluation

This is an evaluation framework for (mostly nonprobabilistic) topic models.
It is written in Python and uses a Jupyter Lab Interface.
Using the latter is recommended, but not neccessary if you only want to run the basic scripts.
If you are unfamiliar with Jupyter Lab, see https://jupyterlab.readthedocs.io/en/stable/ for an introduction.


## Installation

1. Clone repository

2. Requirements  
This software requires Python 3 ( https://www.python.org/ ). It was tested with version 3.6, but other versions might also work. Additionally you will need Node.js ( https://nodejs.org/ )
  - Instructions with pip and virtualenv  
    Within the root folder of this framework execute the following commands:
    - setup a virtual environment with `virtualenv env`
    - activate the environment with  
      Windows: `.\env\Scripts\activate`  
      Linux: `source env/bin/activate`  
    - install requirements with `pip install -r requirements.txt`
    - make shure you execute all following commands in you virtual environment

3. Jupyter Widgets  
To enable Jupyer Widgets run  
`jupyter labextension install @jupyter-widgets/jupyterlab-manager`

NOT 4. HTML Viewing (optional)  
NOT To show html files within jupyter run  
NOT `jupyter labextension install @mflevine/jupyterlab_html`

python -m markdown_kernel.install

5. Saving .html and .py (optional)  
Notebooks can be automatically converted to html files for viewing them outside of juypter lab and to py files for using their definitions elsewhere. 
To enable this add the following code<sup>1</sup> to your `~/.jupyter/jupyter_notebook_config.py`. If it doesn't exist run  
`jupyter notebook --generate-config`  
Note that this will affect all notebooks you run.

```python
import os
from subprocess import check_call

def post_save(model, os_path, contents_manager):
    """post-save hook for converting notebooks to .html files and .py scripts"""
    if model['type'] != 'notebook':
        return # only do this for notebooks
    d, fname = os.path.split(os_path)
    html_out, py_out = True, True
    if fname.endswith('.app.ipynb') or fname.endswith('.doc.ipynb'):
        py_out = False
    if py_out:
        check_call(['jupyter', 'nbconvert', '--to', 'script', fname], cwd=d)
    if html_out:
        check_call(['jupyter', 'nbconvert', '--to', 'html',   fname], cwd=d)

c.FileContentsManager.post_save_hook = post_save
```

6. Preserve Links (optional)  
In order to preserve links when converting notebooks to html files add the following to your `~/.jupyter/jupyter_nbconvert_config.py`. If it doesn't exists run  
`jupyter nbconvert --generate-config`  
This also affects all other notebooks.

```python
c.HTMLExporter.preprocessors = ['init.CustomPreprocessor']
```


## Running

1. Start jupyter lab with  
`jupyter lab`  
Your browser should open the jupyter lab page.
Otherwise copy the link given in the command line.

2. The `evaluation.ipynb` notebook is the recommended place to start.

3. Check `importer/datasets.doc.ipynb` for instructions to install datasets.

4. Check `embedding/embedding_index.doc.ipynb` for instructions to install embedding models.


## Special Features (Bugs and TODOs)
- embedding_filter needs to support removing `'s` or `'nt` like `it's` -> `it`
- In util: iterate: modelinput: check for `_required_model_outputs` to break early (e.g. if W in `_required_model_outputs` don't run cBoW or Phrase)
- Vectorizer App: Selection of Token/Vocab is buggy. Needs better interaction
- requirements.txt probably contains unused modules
- Add more filer options to vocab
- Add a feature for the case that one wishes to use the same versions for B and C vocabs
- When saving, save to a temporary file first and rename the file afterwards to prevent corrupt files when something goes wrong

## Footnotes
1. Taken from  
   https://www.svds.com/jupyter-notebook-best-practices-for-data-science/<br>
   modified from  
   https://github.com/ipython/ipython/issues/8009