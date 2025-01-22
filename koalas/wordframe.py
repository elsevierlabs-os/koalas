import pandas as pd
import numpy as np
import json
from copy import deepcopy
from .history import History
from .merge_operations import match, concat


class WordFrame(pd.DataFrame):

    _metadata = ['meta']

    def __init__(self, data, copy=False, metadata=None, **kwargs):
        meta = getattr(data, 'meta', None)
        if isinstance(data, pd.DataFrame):
            super(WordFrame, self).__init__(data, copy=copy, **kwargs)
            if meta is not None:
                self.meta = deepcopy(meta)
        elif isinstance(data, WordList):
            name = getattr(data, 'name', 'unnamed')
            super(WordFrame, self).__init__({name: data}, copy=copy, **kwargs)
            self.meta = ({name: deepcopy(meta)}
                         if meta is not None else {name: History()})
        else:
            super(WordFrame, self).__init__(data, **kwargs)

        if metadata is not None:
            self.meta = metadata
        self.meta = getattr(self, 'meta', {col: History() for col in self.columns.values})
        self._accessors = {'str': _AccessorChannelThrough(self, 'str'),
                          'cat': _AccessorChannelThrough(self, 'cat'),
                          'dt': _AccessorChannelThrough(self, 'dt'),
                          'script': _AccessorChannelThrough(self, 'script')}

    def __finalize__(self, other, second=None, **kwargs):
        # print('finalize called on WordFrame')
        try:
            meta = other.meta.copy()
            if second is not None:
                meta.update(second.meta)
            self.meta = {k: v for k, v in meta.items() if k in self.columns.values}
            self.meta['last modified'] = other.meta['last modified']
        except:
            pass
            # print('has no meta')
        return self

    def __getitem__(self, key):
        # try:
        #     print('filtered by %s' % key.meta)
        # except:
        #     pass
        item = super().__getitem__(key)
        if isinstance(item, WordList):
            item.__finalize__(self, rename=False)
        return item

    def __setitem__(self, key, value):
        self.meta[key] = getattr(value, 'meta', History())
        self.meta['last modified'] = key
        super().__setitem__(key, value)

    def __getattr__(self, key):
        if key in self._accessors:
            return self._accessors[key]
        elif key in channel_through_methods:
            return self._channel_through_wrapper(key)
        else:
            return super().__getattr__(key)

    @property
    def _constructor(self):
        return WordFrame

    @property
    def _constructor_sliced(self):
        return WordList

    def rename(self, *args, **kwargs):
        '''Overrides the Pandas DataFrame method to consider metadata.
        '''
        try:
            for oldName, newName in kwargs.get('columns', {}).items():
                self.meta[newName] = self.meta[oldName]
                del self.meta[oldName]
        except:
            pass
        return super().rename(*args, **kwargs)

    def merge(self, second, *args, **kwargs):
        '''Overrides the Pandas DataFrame method to consider metadata.
        '''
        result = super().merge(second, *args, **kwargs)
        return result.__finalize__(self, second)

    def concat(self, wordframes, *args, **kwargs):
        '''Overrides the Pandas DataFrame method to consider metadata.
        '''
        wordframes.insert(0, self)
        result = concat(wordframes, *args, **kwargs)
        return result

    def apply_by_row(self, *args, to=None, **kwargs):
        to = to or self.meta.get('last modified', None)
        result = (super().apply(*args, axis=1, **kwargs)
                         # .__finalize__(self, context=('applied by row', '')
                 )
        return self.assign(**{to: result})

    def agg_by_col(self, func):
        result = super().aggregate(func)
        return result

    def apply(self, *args, on=None, to=None, **kwargs):
        '''Overrides the Pandas DataFrame method. In contrast to Pandas the
        `apply` method is called on a column (wordlist) in line with the
        behaviour of other methods in Koalas. Accordingly can take an `on` and
        a `to` argument.
        '''
        return self._channel_through_wrapper('apply')(*args, on=on, to=to, **kwargs)

    def astype(self, *args, on=None, to=None, **kwargs):
        '''Overrides the Pandas DataFrame method. In contrast to Pandas the
        `astype` method is called on a column (wordlist) in line with the
        behaviour of other methods in Koalas. Accordingly can take an `on` and
        a `to` argument.
        '''
        return self._channel_through_wrapper('astype')(*args, on=on, to=to, **kwargs)

    def deduplicate(self, on=None, steps=None):
        '''Groups on (a) specific column(s) and returns the first row of each
        group. The parameter `on` takes a column name as string or a list of
        column names. To influence which row is returned, sort the wordframe
        before.
        '''
        on = on or self.meta.get('last modified', None)
        if steps is None:
            result = self.groupby(on).head(1)
        else:
            temp_col = 'deduplicate temp column'
            last_modified = self.meta.get('last modified', None)
            wf = self.copy(deep=True)
            wf[temp_col] = wf[on].copy()
            step_parameters = [s[1] if type(s) is tuple else () for s in steps]
            step_repeats = [s[2] if( type(s) is tuple and len(s) > 2) else 1 for s in steps]
            steps = [s[0] if type(s) is tuple else s for s in steps]
            for step, step_parameter, step_repeat in zip(steps, step_parameters, step_repeats):
                for i in range(step_repeat):
                    if step.startswith('str.'):
                        colObj = wf[temp_col].str
                        step = step.replace('str.', '')
                    else:
                        colObj = wf[temp_col]
                    wf[temp_col] = getattr(colObj, step)(*step_parameter)
                    wf = (wf.groupby(temp_col)
                            .head(1)
                         )
            if last_modified is not None:
                wf.meta['last modified'] = last_modified
            result = wf.drop(columns=temp_col)
        return result

    def filter(self, on=None, where=''):
        '''Filters the rows of the wordframe on the column specified with `on`,
        with the condition given to `where`. So `wf.filter(on='x',
        where='=="y"')` is equivalent to `wf[wf['x'] == 'y']`. The advantage
        is in method chaining where the syntax `[lambda wf: wf['x'] == 'y']` can
        be avoided.
        '''
        on = on or self.meta.get('last modified', None)
        condition = "self['%s']"%on + where
        result = self[pd.eval(condition, engine='python')]
        return result

    def match_to(self, query, steps=None, on=None, left_on=None, right_on=None,
              left_all=True, right_all=False, left_suff=None, right_suff=None,
              left_drop_matched=True, right_drop_matched=False):
        '''Match to another wordframe `query` on the column given by `on`
        (defaults to the column last used). As `steps` a list of matching steps
        can be given, any WordList method is valid. If the columns to be
        compared differ between the
        two wordframes use `left_on` and `right_on`. To return all rows,
        including the ones that did not match, set `left_all` or `right_all` to
        `True`, respectively. To remove rows that matched so they are not
        matched in the next matching step set `left_drop_matched` and/or
        `right_drop_matched` to `True`.
        '''
        # per default take the last modified column to match on
        if on is None and left_on is None:
            left_on = self.meta['last modified']

        result = match(self, query, steps, on, left_on, right_on,
                  left_all, right_all, left_suff, right_suff,
                  left_drop_matched, right_drop_matched)

        return result

    def match_to_self(self, steps=None, on=None, all=False, drop_matched=False):
        '''Match a wordframe to itself to identify duplicates or similar terms.
        Matches of a term to itself are filtered out. By default only matched
        terms are returned, set `all` to `False` to change this behaviour.
        '''
        # per default take the last modified column to match on
        on = on or self.meta.get('last modified', None)
        base = self.copy(deep=True)
        base['temp UID'] = np.arange(0, len(self))
        copy_cols = ['%s_copy'%col for col in base.columns.values]
        result = (match(base, base, steps, on, right_suff='copy', left_all=all,
                  left_drop_matched=drop_matched, right_drop_matched=False)
                  .filter(on='temp UID', where='!= self["temp UID_copy"]')
                  # .groupby(['temp UID', 'temp UID_copy'], as_index=False)
                  # .nth(0)
                  .sort_values(['temp UID_copy', 'temp UID'])
                  # .drop(columns=copy_cols)
                  .drop(columns=['temp UID', 'temp UID_copy'])
                 )
        return result

    def to_json(self, filename, additional=None):
        '''Saves the wordframe to a JSON file including all metadata.
        '''
        data = super().to_json()
        meta = json.dumps(self.meta)
        if additional is None:
            content = '{"data": %s, "meta": %s}' % (data, meta)
        else:
            extra = json.dumps(additional)
            content = '{"data": %s, "meta": %s, "extra": %s}' % (data, meta, extra)
        with open(filename, 'w') as f:
            f.write(content)

    def stack_list(self, on=None, to=None):
        '''Works on a column containing a list in each row. Each entry of the
        list is placed in a new row, with the contents of the other columns
        repeated.
        '''
        on = on or self.meta.get('last modified', None)
        to = to or on
        result = (WordList(self[on]
                           .apply(lambda x: pd.Series(x))
                           .stack()
                           .reset_index(level=1, drop=True)
                          ).__finalize__(self[on], context=('stacked lists', ''))
                           .to_frame(to)
                           .join(self, how='left', rsuffix='_')
                  )
        if to in self.columns:
            result = result.drop(columns=(to + '_'))
            if to != on:
                result = (self.assign(**{on: False})
                              .append(result.assign(**{on: True}))
                              .sort_index())
        return WordFrame(result).__finalize__(self)

    def _channel_through_wrapper(self, method):
        def channel_through(*args, on=None, to=None, **kwargs):
            on = on or self.meta.get('last modified', None) or self.columns.values[-1]
            to = to or on
            return self.assign(**{to: lambda wf: getattr(wf[on], method)(*args, **kwargs)})
        return channel_through

class _AccessorChannelThrough:
    'Helper class to channel through request for string methods to wordlist'

    def __init__(self, parent, accessor):
        self.parent = parent
        self.accessor = accessor

    def __getattr__(self, key):
        def channel_through(*args, on=None, to=None, **kwargs):
            parent = self.parent
            on = on or parent.meta.get('last modified', None) or parent.columns.values[-1]
            to = to or on
            return self.parent.assign(**{to: lambda wf:
                getattr(getattr(wf[on], self.accessor), key)(*args, **kwargs)
                .__finalize__(wf[on], context=(key, args if args else ''))})
        return channel_through

# put at the bottom to avoid circular dependency
from .wordlist import WordList
from itertools import chain

list_methods = [m for m in chain(pd.Series.__dict__, WordList.__dict__) if not m.startswith('_')]
frame_methods = [m for m in chain(pd.DataFrame.__dict__, WordFrame.__dict__)]
channel_through_methods = (set(list_methods) - set(frame_methods) - set(['str', 'cat', 'dt', 'script', 'name'])) | set(['replace_', 'apply', 'filter'])
