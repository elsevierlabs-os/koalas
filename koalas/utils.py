import os
import pkg_resources
import pandas as pd
import numpy as np

def _resolve_filename(filename, modulefile):
    dirname = os.path.dirname(os.path.abspath( modulefile ))
    filepath = os.path.join(dirname, filename)
    return filepath

def _isnan(value):
    test = pd.isna(value)
    if isinstance(test, np.ndarray):
        return False
    else:
        return test
