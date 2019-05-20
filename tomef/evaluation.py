#!/usr/bin/env python
# coding: utf-8

# # Evaluation
# 
# This is the main evaluation script.
# See [Introduction](./docs/intro.ipynb) for an overview.
# 
# ## [Initialize](docs/details.ipynb#Initialize), [Tools](tools/tools.py.ipynb) and [Configuration](./docs/config.ipynb)
# 
# Execute this cell first. Runs Tools (command line use) and loads [config.json](./config.json).
# Run again if you have changed the configuration.

# In[ ]:


try:
    get_ipython().run_line_magic('reload_ext', 'autoreload')
    get_ipython().run_line_magic('autoreload', '2')
except NameError: 
    pass

from tools.tools import run_tools
run_tools()

from base import config
from interface import nbbox
config.load_config()


# ## [Importer](./importer/importer.ipynb)
# Imports datasets into standard format.

# In[ ]:


if config.importer["run"]:
    with nbbox():
        from importer.main import run_importer 
        run_importer()


# ## [Tokenizer](./tokenizer/tokenizer.ipynb)
# 
# Extracts tokens from raw text. Uses [Embeddings](./embedding/embedding.ipynb).

# In[ ]:


if config.tokenizer["run"]:
    with nbbox():
        from tokenizer.main import run_tokenizer
        run_tokenizer()


# ## [Vocab](./vocab/vocab.ipynb)
# Forms vocabulary from tokens.

# In[ ]:


if config.vocab["run"]:
    with nbbox():
        from vocab.main import run_vocab
        run_vocab()


# ## [Vectorizer](./vectorizer/vectorizer.ipynb)
# Creates a vector representation of each document. Uses [Embeddings](./embedding/embedding.ipynb).

# In[ ]:


if config.vectorizer["run"]:
    with nbbox():
        from vectorizer.main import run_vectorizer
        run_vectorizer()


# ## [Models](./models/models.ipynb)
# Creates (soft) clustering the corpus.

# In[ ]:


if config.models["run"]:
    with nbbox():
        from models.main import run_models
        run_models()


# ## [Model Metrics](./metrics/metrics.ipynb)
# Evaluates the results form the Models module.

# In[ ]:


if config.metrics["run"]:
    with nbbox():
        from metrics.main import run_model_metrics
        run_model_metrics()


# ## [Distiller](./distiller/distiller.ipynb)
# Extracts topics from the previous data.

# In[ ]:


if config.distiller["run"]:
    with nbbox():
        from distiller.main import run_distiller
        run_distiller()


# ## [Topic Metrics](./metrics/metrics.ipynb)
# Evaluates the topics.

# In[ ]:


if config.metrics["run"]:
    with nbbox():
        from metrics.main import run_topic_metrics
        run_topic_metrics()

