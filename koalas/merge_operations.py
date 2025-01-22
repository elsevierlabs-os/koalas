import pandas as pd
import numpy as np
import re
from pandas.api.types import CategoricalDtype


def WordFrame(*args, **kwargs):
    from .wordframe import WordFrame
    return WordFrame(*args, **kwargs)

def concat(wordframes, *args, **kwargs):
    result = pd.concat(wordframes, *args, sort=True, **kwargs)
    meta = {}
    for wordframe in wordframes:
        if hasattr(wordframe, 'meta'):
            meta.update(wordframe.meta)
    result.meta = meta
    return result

def match(base, query, steps=None, on=None, left_on=None, right_on=None,
          left_all=False, right_all=False, left_suff=None, right_suff=None,
          left_drop_matched=True, right_drop_matched=False):
    '''This function takes two wordframes, base and query, adds several
       derived columns as defined in comparison and tries to match them.
    '''
    # use the default AnAGram sequence as default
    if steps is None:
        steps = ['exact', 'normalize', 'sort_words', 'lemmatize']
         # * 1) unprocessed
         # * 2) normalise the string
         #     (lowercase characters, remove accents, replace xml entities with their characters, and non-word characters with space)
         # * 3) remove stopwords
         # * 4) rearrange the words alphabetically
         # * 5) substitution of certain words or phrases(liver => hepatic)
         # * 6) stemming
         # * 7) substitution of certain words followed by stemming

    # splice out parameters from the step list
    step_parameters = [s[1] if type(s) is tuple else () for s in steps]
    step_repeats = [s[2] if( type(s) is tuple and len(s) > 2) else 1 for s in steps]
    steps = [s[0] if type(s) is tuple else s for s in steps]

    # assign chosen suffixes or backups in case column names clash
    baseSuffix = '_' + getattr(base, 'name', 'base')
    querySuffix = '_' + getattr(query, 'name', 'query')
    generalBaseSuffix = ('_' + left_suff) if left_suff else ''
    generalQuerySuffix = ('_' + right_suff) if right_suff else ''

    # copy input to avoid changing the original dataframes and cast to WordFrame
    base = WordFrame(base.copy(deep=True)).add_suffix(generalBaseSuffix)
    query = WordFrame(query.copy(deep=True)).add_suffix(generalQuerySuffix)

    # prepend column names with digit for later ordering
    baseColNumbers = np.arange(len(base.columns))
    newBaseCols = {n: '{:03}_{}'.format(i, n) for i, n in zip(baseColNumbers, base.columns)}
    base.rename(columns=newBaseCols, inplace=True)
    queryColNumbers = np.arange(len(query.columns)) + len(base.columns)
    newQueryCols = {n: '{:03}_{}'.format(i, n) for i, n in zip(queryColNumbers, query.columns)}
    query.rename(columns=newQueryCols, inplace=True)

    # assign a temporary identifier for the matching
    base['base temp UID'] = np.arange(0, len(base))
    query['query temp UID'] = np.arange(0, len(query))
    origColsBase = list(base.columns.values)
    origColsQuery = list(query.columns.values)

    # create list of columns to work on
    if on is not None:
        left_on = newBaseCols[on + generalBaseSuffix]
        right_on = newQueryCols[on + generalQuerySuffix]
    else:
        left_on = newBaseCols[left_on + generalBaseSuffix]
        right_on =  newQueryCols[right_on + generalQuerySuffix]
    targetCols = ['merge_' for step in steps]
    # leftCols = [(left_on, base[left_on].columns[0])] + targetCols
    # rightCols = [(right_on, query[right_on].columns[0])] + targetCols
    leftCols = [left_on] + targetCols
    rightCols = [right_on] + targetCols

    # The central matching loop
    found = []
    step_labels = []
    for step, step_parameter, step_repeat, leftCol, rightCol, targetCol in zip(
      steps, step_parameters, step_repeats, leftCols, rightCols, targetCols):
        for i in range(step_repeat):
            step_label = step + ('(%s)'%(i+1) if step_repeat > 1 else '')
            step_labels.append(step_label)
            if step.startswith('left '):
                side = 'left'
                method = step.replace('left ', '')
            elif step.startswith('right '):
                side = 'right'
                method = step.replace('right ', '')
            else:
                side = ''
                method = step

            accessor = re.match(r'(.*?)\.', method)
            if accessor:
                accessor_name = accessor.groups(0)[0]
                baseObj = getattr(base[leftCol], accessor_name)
                queryObj = getattr(query[rightCol], accessor_name)
                method = method.replace(accessor[0], '')
            else:
                baseObj = base[leftCol]
                queryObj = query[rightCol]

            base[targetCol] = baseObj if side == 'right' else getattr(baseObj,
                                                       method)(*step_parameter)
            query[targetCol] = queryObj if side == 'left' else getattr(queryObj,
                                                       method)(*step_parameter)
            baseCols = origColsBase + [targetCol]
            queryCols = origColsQuery + [targetCol]
            query[queryCols]
            matched = (base[baseCols].merge(query[queryCols],
                                            on=targetCol, how='inner',
                                            suffixes=(baseSuffix, querySuffix))
                                     .rename(columns={targetCol: 'matched_string'})
                                     .assign(matched_how=step_label)
                                     # .filter('matched_string', where='.notna()')
                      )
            found.append(matched)
            if left_drop_matched:
                query = query[~query['query temp UID'].isin(matched['query temp UID'])]
            if right_drop_matched:
                base = base[~base['base temp UID'].isin(matched['base temp UID'])]

    #add the non-matched terms
    if not (left_suff or right_suff):
        origColsBase = [col for col in origColsBase if col not in origColsQuery]
        origColsQuery = [col for col in origColsQuery if col not in origColsBase]
    if left_all:
        for matched in found:
            base = base[~base['base temp UID'].isin(matched['base temp UID'])]
        base_not_matched = base[origColsBase]
        base_not_matched['matched_how'] = 'not matched'
    else:
        base_not_matched = None
    if right_all:
        for matched in found:
            query = query[~query['query temp UID'].isin(matched['query temp UID'])]
        query_not_matched = query[origColsQuery]
        query_not_matched['matched_how'] = 'not matched'
    else:
        query_not_matched = None

    # Reverse dict to get original col names, add suffix if name conflict
    oldColNames = {v: (k + baseSuffix if k in newQueryCols else k)
                   for k, v in newBaseCols.items()}
    oldColNames.update({v: (k + querySuffix if k in newBaseCols else k)
                   for k, v in newQueryCols.items()})

    # make matched_how column categorical, sort order like steps
    step_labels.append('not matched')
    matched_how_cats = CategoricalDtype(categories=step_labels, ordered=True)

    # concatenate all the matches, pick the best match between each pair of
    # labels, append non-matched labels and sort into original order
    result = (concat(found)
              .groupby(['base temp UID', 'query temp UID'], as_index=False)
              .nth(0)
              .concat([base_not_matched, query_not_matched])
              .assign(matched_how=lambda x: x['matched_how'].astype(matched_how_cats))
              .sort_values(['base temp UID', 'query temp UID'])
              .drop(columns=['base temp UID', 'query temp UID'])
              .rename(columns=oldColNames)
             )

    return result
