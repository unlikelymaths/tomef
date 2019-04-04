# Wiki

Info | wiki
------|-------
Source | https://dumps.wikimedia.org/enwiki/
Documents | x
Classes | x

### Description

#### Step 1
Download Wiki Dump file
File: enwiki-YYYYMMDD-pages-articles.xml.bz2

#### Step 2
Set wiki_raw, wiki_dictionary and wiki_corpus in config.json.
Run make_wikicorpus.py in code.
This takes a very long time and creates large files.

#### Reference
https://radimrehurek.com/gensim/wiki.html
https://radimrehurek.com/gensim/scripts/make_wikicorpus.html