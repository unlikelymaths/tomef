import nltk

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
nltk_stopwords = {
    'english': set(nltk.corpus.stopwords.words('english'))
    }