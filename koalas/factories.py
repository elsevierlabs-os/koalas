from .wordframe import WordFrame
from .history import History, Event
import json
import io
import pandas as pd

def _make_meta(filename, columns, provenance=None):
    if provenance is not None:
        if isinstance(provenance, list):
            meta = {col: History([Event(argument=prov,
                operation='external source')]) for col, prov
                in zip(columns, provenance)}
        else:
            meta = {col: History([Event(argument=provenance,
                operation='external source')]) for col in columns}
    else:
        meta = {col: History([Event(argument=filename, operation='from file')])
                for col in columns}
    return meta

def read_csv(filename, provenance=None, *args, **kwargs):
    '''Read the contents of a CSV file into a WordFrame. Provenance info
    can be passed as a dictionary or as a list of dictionaries for each column.
    '''
    kwargs2 = {'keep_default_na': False}
    kwargs2.update(kwargs)
    data = pd.read_csv(filename, *args, **kwargs2)
    meta = _make_meta(filename, data.columns.values, provenance)
    return WordFrame(data, metadata=meta)

def read_json(filename, provenance=None):
    '''Read the contents of a JSON file into a WordFrame. Recognizes saved
    metadata and attaches it to the WordFrame. As a fallback provenance info
    can be passed as a dictionary or as a list of dictionaries for each column.
    '''
    with open(filename) as f:
        x = json.load(f)
    if 'meta' in x:
        meta = {k: History(v) for k, v in x['meta'].items()}
    else:
        meta = _make_meta(filename, x['data'].keys(), provenance)
    if 'extra' in x:
        return WordFrame(x['data'], metadata=meta), x['extra']
    else:
        return WordFrame(x['data'], metadata=meta)

def read_excel(filename, *args, provenance=None, **kwargs):
    '''Read the contents of a JSON file into a WordFrame. Provenance info
    can be passed as a dictionary or as a list of dictionaries for each column.
    This function requires the package `xlrd` to be installed.
    '''
    data = pd.read_excel(filename, *args, **kwargs)
    meta = _make_meta(filename, data.columns.values, provenance)
    return WordFrame(data, metadata=meta)

def read_graph(endpointURL, query, username='', password=''):
    '''Queries a SPARQL endpoint at `endpointURL` with `query`.
    '''
    from SPARQLWrapper import SPARQLWrapper, CSV, BASIC
    SPARQLEndpoint = SPARQLWrapper(endpointURL, returnFormat=CSV)
    if username and password:
        SPARQLEndpoint.setHTTPAuth(BASIC)
        SPARQLEndpoint.setCredentials(username, password)
    SPARQLEndpoint.setQuery(query)
    response = SPARQLEndpoint.query().convert()
    data = pd.read_csv(io.BytesIO(response))
    meta = {col: History([Event(argument={'endpointURL': endpointURL,
            'query': query}, operation='from SPARQL query')])
            for col in data.columns.values}
    return WordFrame(data, metadata=meta)
