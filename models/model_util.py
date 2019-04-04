import data
from base import nbprint

from vectorizer.main import run_vectorizer

def check_requirements(info):
    # Check if documents file exists
    if not data.input_mat_exists(info):
        # Run Importer
        nbprint('Input mat missing.')
        run_vectorizer(info)
        # Check if it was successfull
        if not data.input_mat_exists(info):
            return False
    return True