import pandas as pd
import numpy as np
import nltk
import urllib
from copy import deepcopy
import unicodedata as uc
from .wordframe import WordFrame
from .ophistory import OpHistory
from .history import History, Event
from .utils import _isnan
from . import lists


class WordList(OpHistory, pd.Series):

    def __init__(self, *args, **kwargs):
        super(WordList, self).__init__(*args, **kwargs)
        self._metadata.append('meta')
        self.meta = History()

    def __finalize__(self, other, rename=True, context=None, **kwargs):
        # print('WordList.finalize called')
        for key in self._metadata:
            if key == 'name' and not rename:
                continue
            setattr(self, key, getattr(other, key, None))
        # print(context)
        meta = getattr(other, 'meta', None)
        if meta:
            self.meta = deepcopy(meta.get(self.name, None)
                        if isinstance(other, WordFrame) else meta)
        else:
            self.meta = History()
        if meta and context is not None:
            self.meta.append(Event(operation=context[0], argument=context[1]))
        return self

    @property
    def _constructor(self):
        return WordList

    @property
    def _constructor_sliced(self):
        return WordList

    @property
    def _constructor_expanddim(self):
        return WordFrame

    # def __array_wrap__(self, result, context=None):
    #     print(context)
    #     result = super(WordList, self).__array_wrap__(result, context)
    #     result.meta['history'].append({'operation': str(context[0]),
    #                                    'on': time.time(),
    #                                    'by': getpass.getuser()
    #                                   })
    #     return result

    def apply(self, function, convert_dtype=True, args=(), **kwargs):
        '''Overrides original implementation of `apply` to take into account
        NaNs. For this the callable supplied in `apply` is wrapped in a function
        testing for NaN and is only called on non-NaN values. This results in
        a performance penalty but solves the problem that most functions
        outside of Pandas are not NaN-aware.
        '''
        def NAN_aware_function(x):
            if _isnan(x):
                return np.nan
            else:
                return function(x, *args, **kwargs)
        result = super().apply(NAN_aware_function, convert_dtype=convert_dtype)
        return result.__finalize__(self, context=('applied', function))

    def filter(self, where=''):
        '''Filters the rows of the wordlist with the condition given to `where`.
        So `wl.filter(where='=="y"')` is equivalent to `wf[wf == 'y']`. The
        advantage is in method chaining where the syntax `[lambda wf: wf == 'y']`
        can be avoided.
        '''
        condition = "self" + where
        result = self[pd.eval(condition, engine='python')]
        return result

    def remove_words(self, wordlist):
        '''Remove any words in the string that matches an exact entry in
        `wordlist`.
        '''
        wordarray = np.array(wordlist)
        result = (self.str.split()
                      .apply(lambda x: [w for w in x if w not in wordarray])
                      .str.join(' '))
        return result.__finalize__(self, context=('removed words', wordlist))

    def remove_first_word(self):
        '''Removes the first word in the string. If there is only one word NaN
        is returned.
        '''
        result = (self.str.split()
                      .apply(lambda x: np.nan if len(x) == 1 else x[1:])
                      .str.join(' '))
        return result.__finalize__(self, context=('removed first word', ''))

    def remove_last_word(self):
        '''Removes the last word in the string. If there is only one word NaN
        is returned.
        '''
        result = (self.str.split()
                      .apply(lambda x: np.nan if len(x) == 1 else x[:-1])
                      .str.join(' '))
        return result.__finalize__(self, context=('removed first word', ''))

    def replace_substrings(self, stringlist, repl=''):
        '''Replaces any substring in the string that matches an exact entry in
        `stringlist`. By default it is replaced with an empty string
        (i.e. removed). Passing a dictionary you can give replacements by row.
        '''
        if type(stringlist) is list:
            result = self.str.replace(pattern, repl=repl)
        else:
            if isinstance(stringlist, WordFrame):
                mappingdict = dict(zip(stringlist.index, stringlist.iloc[:,0]))
            elif isinstance(stringlist, WordList):
                mappingdict = dict(zip(stringlist.index, stringlist.values))
            else:
                mappingdict = stringlist
            pattern = r'|'.join(stringlist.keys())
            replace = lambda x: mappingdict.get(x.group(0), '?')
            result = self.str.replace(pattern, replace)
        return result.__finalize__(self,
                                   context=('replaced substrings', stringlist))

    def resolve_medical_terms(self):
        # medical_terms = lists.load('medical terms', substitutions=True)
        medical_affixes = lists.load('medical affixes', full_dataset=True)

        prefixes = '|'.join(medical_affixes.loc[medical_affixes['prefix'], 'regex'])
        suffixes = '|'.join(medical_affixes.loc[medical_affixes['suffix'], 'regex'])
        # terms = '|'.join(medical_terms.index.values)

        # pattern = r'[^|\W](?P<term>%s)|(?P<prefix>%s)?(?P<rest>[\w]+)(?P<suffix>%s)?[$|\W]'%(terms, prefixes, suffixes)
        pattern = r'(?P<prefix>%s)?(?P<rest>[\w]+)(?P<suffix>%s)?[$|\W]'%(prefixes, suffixes)

        result = (self
        # .str.split(' ')
                      .str.replace(pattern, lambda x: (' ' +
                                medical_affixes['Meaning'].get(x.group('prefix'), x.group('prefix') or '') + ' ' +
                                (x.group('rest') or '') + ' ' +
                                medical_affixes['Meaning'].get(x.group('suffix'), x.group('suffix') or '')  + ' '
                                  ))
                      # .str.join(' ')
                      .str.replace(r'\s+', r' ')
                      .str.strip(' ')
                )
        return result.__finalize__(self, context=('resolved medical terms', ''))

    def remove_punctuation(self, replace_with_whitespace=False):
        '''Removes any punctuation from the string, including some non-ASCII.
        '''
        pattern = r'[_\.,;:!?\*‐\-–—#<>\(\)\[\]„“”‘’\'\"/\\\|%\^~`$=\+{}\*\@\&′″、]'
        replacement = ' ' if replace_with_whitespace else ''
        result = (self.str.split(pattern)
                      .str.join(replacement))
        return result.__finalize__(self, context=('removed punctuation', ''))

    def remove_whitespace(self):
        '''Replaces any whitespace in the input string with a single space.
        '''
        result = (self.str.replace(r'\s+', repl=' ')
                      .str.replace(r'(^\s)|(\s$)', repl='')
                 )
        return result.__finalize__(self, context=('removed whitespace', ''))

    def remove_qualifiers(self):
        '''Removes 'qualifiers' that are enclosed in parentheses,
         e.g. (biology), from the string including adjacent extra whitespace.
         '''
        pattern = r'\s*?\(.*?\)\s*?'
        result = (self.str.split(pattern)
                          .str.join(' '))
        return result.__finalize__(self, context=('removed qualifier', ''))

    def remove_control_characters(self):
        '''Removes control characters.
        '''
        newline_characters = r'[\n\r]'
        pattern = r'[\x00-\x08\x0B-\x1F\x7F]'
        result = (self.str.replace(newline_characters, '\n')
                      .str.replace(pattern, '')
                 )
        return result.__finalize__(self,
                                   context=('removed control characters', ''))

    def replace_non_ascii(self, replacement=''):
        '''Replaces non-ASCII characters with the character in `replacement`.
        '''
        pattern = r'[^\x00-\x7F]'
        replace = lambda x: accented_chars.get(x.group(0), replacement)
        result = self.str.replace(pattern, replace)
        return result.__finalize__(self,
                                   context=('replaced non ASCII characters', ''))

    def replace_url_encoded_characters(self):
        pattern = r'(\%[\da-fA-F]{2})+'
        replace = lambda x: urllib.parse.unquote(x.group(0))
        result = self.str.replace(pattern, replace)
        return result.__finalize__(self,
                                   context=('replaced URL encoded characters', ''))

    def replace_typographic_forms(self):
        '''Replaces curly single and double quotes with straight ones, and
        different dashes and minus with a simple hyphen.
        '''
        typographics = {'−': '-', '–': '-', '—': '-', '“': '"', '”': '"', '‘': "'", '’': "'"}
        result = self.replace_substrings(typographics)
        return result.__finalize__(self,
                                   context=('replaced typographic forms', ''))

    def normalize_unicode(self):
        '''Replace unicode characters by their canonical form.
        '''
        normalize = lambda x: uc.normalize('NFKC', x)
        result = self.apply(normalize)
        return result.__finalize__(self, context=('normalize unicode', ''))

    def remove_accents(self):
        '''Remove accents from letters by decomposing their canonical unicode glyph.
        '''
        normalize = lambda x: ''.join(c for c in uc.normalize('NFD', x)
                                            if not uc.combining(c))
        result = self.apply(normalize).str.replace('ı', 'i')
        return result.__finalize__(self, context=('remove accents', ''))

    def replace_accented_characters(self, remove_others=False, replacement='?'):
        '''Replaces accented, non-ASCII characters with an ASCII equivalent as
        defined in the list `accented characters`.
        '''
        pattern = r'[^\x00-\x7F]'
        accented_chars = lists.load('accented characters', substitutions=True)
        replace = (lambda x: accented_chars.get(x.group(0), replacement)
                    if remove_others else
                   lambda x: accented_chars.get(x.group(0), x.group(0))
                   )
        result = self.str.replace(pattern, replace)
        return result.__finalize__(self,
                                   context=('replaced special characters', ''))

    def replace_greek_characters(self):
        '''Replaces greek characters with their name in Latin script using the
        list `greek characters`.
        '''
        pattern = r'[µ\u0391-\u03C9]'
        greek_chars = lists.load('greek characters', substitutions=True)
        replace = lambda x: greek_chars.get(x.group(0), '?')
        result = self.str.replace(pattern, replace)
        return result.__finalize__(self, context=
                                            ('replaced greek characters', ''))

    def replace_words(self, wordmapping):
        '''Replaces words with another word defined in a dictionary (or a
        WordList with words to be replaced in the index) passed into
        `wordmapping`.
        '''
        if isinstance(wordmapping, WordFrame):
            mappingdict = dict(zip(wordmapping.index, wordmapping.iloc[:,0]))
        elif isinstance(wordmapping, WordList):
            mappingdict = dict(zip(wordmapping.index, wordmapping.values))
        else:
            mappingdict = wordmapping
        result = (self.str.split()
                      .apply(lambda x: [mappingdict.get(w, w) for w in x])
                      .str.join(' ')
                 )
        return result.__finalize__(self, context=('replaced words with',
                    wordmapping))

    def word_isin(self, wordlist, agg='any'):
        '''Returns `True` if any word or all words in the string match(es) an
        entry in `wordlist`, depending on the parameter `agg`.
        '''
        wordarray = np.array(wordlist)
        aggFunc = all if agg == 'all' else (sum if agg == 'sum' else any)
        result = (self.str.split()
                      .apply(lambda x:
                               aggFunc([word in wordarray for word in x]))
                 )
        description = 'all words are in'if agg == 'all' else 'any word is in'
        return result.__finalize__(self, context=(description, wordlist))

    def term_isin(self, termlist):
        '''Returns True if the entire string matches an
        entry in `termlist`.
        '''
        termarray = np.array(termlist)
        result = super().isin(termarray)
        return result.__finalize__(self, context=('term is in', termlist))

    def word_number(self):
        '''Returns the number of words in the string.
        '''
        result = self.str.split().str.len()
        return result.__finalize__(self, context=('word number', ''))

    def pos_tag(self, pos_tag_function=None):
        '''Returns a list of POS tags corresponding to each word in the string.
        Uses the NLTK pos tagger by default but another one can be passed
        into the method through the `pos_tag_function` parameter.
        '''
        pos_tag_function = pos_tag_function or nltk.pos_tag
        result = (self.str.split()
                      .apply(pos_tag_function)
                      .apply(lambda x: [i[1] for i in x]))
        return result.__finalize__(self, context=('POS tagged', ''))

    def tokenize(self, tokenize_function=None):
        '''Returns a list of tokens for the string. Uses by default the
        NLTK TreebankWordTokenizer but another one can be passed
        into the method through the `tokenize_function` parameter.
        '''
        tokenize_function = tokenize_function or nltk.TreebankWordTokenizer().tokenize
        result = self.apply(tokenize_function)
        return result.__finalize__(self, context=('lemmatized', ''))

    def stem(self, stem_function=None):
        '''Returns the stem of each word in the string.
        Uses by default the NLTK SnowballStemmer but another one can be passed
        into the method through the `stem_function` parameter.
        '''
        stem_function = stem_function or nltk.SnowballStemmer('english').stem
        result = (self.str.split()
                      .apply(lambda x: [stem_function(word) for word in x])
                      .str.join(' '))
        return result.__finalize__(self, context=('lemmatized', ''))

    def lemmatize(self, lemmatize_function=None):
        '''Returns the lemma of each word in the string.
        Uses by default the NLTK WordNetLemmatizer but another one can be passed
        into the method through the `lemmatize_function` parameter.
        '''
        lemmatize_function = (lemmatize_function
                              or nltk.WordNetLemmatizer().lemmatize)
        result = (self.str.split()
                      .apply(lambda x: [lemmatize_function(word) for word in x])
                      .str.join(' '))
        return result.__finalize__(self, context=('lemmatized', ''))

    def melt_list(self, column):
        self[column].apply(lambda x: pd.Series(x)).stack()

    def explode(self):
        array_size = int(self.str.len().sum())
        out_index = np.empty(array_size, dtype=object)
        out_values = np.empty(array_size, dtype=object)

        in_index = self.index
        in_values = self.values
        counter = 0

        for i in range(len(self)):
            index = in_index[i]
            values = in_values[i] if not _isnan(in_values[i]) else []
            for value in values:
                out_values[counter] = value
                out_index[counter] = index
                counter += 1

        return WordList(out_values, index=out_index)

    def exact(self):
        '''Returns an exact copy of the string. This is the identity method
        for convenient use as a matching step.
        '''
        result = self.copy()
        return result

    def extract_acronym(self):
        '''Returns an acronym if found and otherwise NaN. This method looks for
        acronyms in parentheses that follow their expanded term, e.g.
        "United States of America (USA)".
        '''
        acronym_pattern = r'(?P<head>^|.*\W)(?P<expansion>(\w)(?:.*?\W(\w).*?\W(?:(\w).*?\W)?|(\w).*?\W(\w).*?\W)(?:(\w).*?)?(?:(\w).*?)?)\((?P<acronym>(?:\3\W?\4\W?\5?\W?\8?\W?\9?|\3\6\W?\7?\W?\8?\W?\9?)\W?s?)\)(?P<tail>[^,;.].*)?'

        def original_acronym(row):
            if _isnan(row['acronym']):
                return np.nan
            else:
                row = row.fillna('')
                original = row['original']
                lower = original.lower()
                startHead = lower.find(row['head'])
                endHead = startHead + len(row['head'])
                startAcronym = lower.find(row['acronym'])
                endAcronym = startAcronym + len(row['acronym'])
                startTail = lower.find(row['tail'])
                endTail = startTail + len(row['tail'])
                return original[startHead:endHead] + original[startAcronym:endAcronym] + original[startTail:endTail]

        acronyms = (WordFrame(self.str.lower()
                      .str.extract(acronym_pattern))
                      .assign(original=self)
                      .apply_by_row(original_acronym, to='acronym')
                      .str.replace(r"^([A-Z]*)'?s$", r'\1', on='acronym')
                    )

        result = acronyms['acronym']

        return result.__finalize__(self, context=('Acronym extracted', ''))

    def sort_words(self, descending=False):
        '''Returns the string with words arranged alphabetically.
        '''
        result = (self.str.split()
                      .apply(lambda words: sorted(words, reverse=descending))
                      .str.join(' '))
        return result.__finalize__(self, context=('words sorted', ''))

    def natural_word_order(self):
        '''Returns the string split on commas and reverses the order of tokens.
        '''
        result = (self[self.notna()].str.split(r'\s?,\s?')
                      .apply(lambda x: list(reversed(
                                            [w for w in x if w != ' '])))
                      .str.join(' '))
        return result.__finalize__(self, context=('natural word order', ''))

    def normalize(self):
        '''Convenience function that calls after another the following methods:
        `str.lower`, `replace_special_characters`, `remove_punctuation`,
        `replace_greek_characters`, `replace_words(british_to_american)`,
        `remove_whitespace`.
        '''
        british_to_american = lists.load('British English', substitutions=True)
        result = (self.str.lower()
                      .replace_accented_characters()
                      .remove_punctuation()
                      .replace_greek_characters()
                      .replace_words(british_to_american)
                      .remove_whitespace()
                  )
        return result.__finalize__(self, context=('normalized', ''))
