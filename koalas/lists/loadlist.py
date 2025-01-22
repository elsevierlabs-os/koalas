import os
import json
import ast
from ..factories import read_csv, read_json, _make_meta
from ..utils import _resolve_filename

def load(listname, substitutions=False, full_dataset=False):
    '''Loads a reference wordlist specified by `listname`. To get a wordlist
    with the terms as index and a substitution term as value set `substitutions`
    to `True`. This can be used with the `replace_words` method. Setting
    `full_dataset` to `True` returns a wordframe instead, including additional
    data columns if present.
    '''
    filename = _resolve_filename(listname, __file__) + '.json'
    wordframe, extra = read_json(filename)
    if full_dataset:
        return wordframe
    termColumn = extra['term column']
    if substitutions:
        substitutionColumn = extra['substitution column']
        wordlist = wordframe.set_index(termColumn)[substitutionColumn]
    else:
        wordlist = wordframe[termColumn]
    return wordlist

def save(wordframe, listname, provenance, termColumn, substitutionColumn=None):
    '''Add a new reference wordlist to koalas. Given a wordframe, provenance
    information and name for the list a JSON file is saved in the folder `lists`
    within the koalas package.
    '''
    filename = _resolve_filename(listname, __file__) + '.json'
    extra = {'name': listname, 'term column': termColumn,
             'substitution column': substitutionColumn}
    wordframe.meta = _make_meta(listname, wordframe.columns.values, provenance)
    wordframe.to_json(filename, additional=extra)

def info(listname):
    '''Returns a string with information about the reference wordlist given
    with `listname`. Setting `listname` to `'all'` returns information on all
    available lists.
    '''
    if listname == 'all':
        path = _resolve_filename('', __file__)
        filenames = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json')]
    else:
        filenames = [_resolve_filename(listname, __file__) + '.json']

    output = []
    for filename in filenames:
        wordframe, extra = read_json(filename)
        description = '- **%s:**' % extra['name']
        termColumn = extra['term column']
        arg = wordframe.meta[termColumn][0]['argument']
        provenance = ast.literal_eval(arg)
        for entry in provenance.items():
            description += '\n  - *%s*: %s' % entry
        output.append(description)

    return '\n'.join(output)
