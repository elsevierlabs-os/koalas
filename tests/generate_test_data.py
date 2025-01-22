import koalas as kl


# for test_wordframe
wordframe = kl.read_csv(f'data/sample.csv')
wordframe.astype(bool, on='frequency')

methods = {
'astype': ([bool], {'on': 'frequency'}),
'deduplicate': ([], {'on': 'frequency'})
}

for method, (args, kwargs) in methods.items():
    getattr(wordframe, method)(*args, **kwargs).to_frame().to_csv(f'data/test_wordframe/{method}.csv', index=False)

r = wordframe.apply(list, on='term', to='list')
r.dropna().stack_list(on='list').to_csv('data/test_wordframe/stack_list_same_column.csv', index=False)
r.dropna().stack_list(on='list', to='term').to_csv('data/test_wordframe/stack_list_different_column.csv', index=False)


# for test_factories
wordframe = kl.read_csv(f'data/sample.csv')
wordframe.to_json('data/test_factories/sample.json')
wordframe.to_excel('data/test_factories/sample.xlsx')

# for test_wordlist

wordlist = kl.read_csv(f'data/sample.csv')['term']
methods = {
'apply': [lambda term: term in ['Gord Renwick']],
'remove_words': [kl.lists.load('stopwords AnAgram')],
'remove_first_word': [],
'remove_last_word': [],
'replace_substrings': [{'13': 'thirteen', 'Mr.': 'Mister'}],
'remove_punctuation': [],
'remove_whitespace': [],
'remove_qualifiers': [],
'replace_typographic_forms': [],
'replace_accented_characters': [],
'replace_greek_characters': [],
'replace_words': [kl.lists.load('medical terms', substitutions=True)],
'word_isin': [kl.lists.load('common words Google')],
'term_isin': [kl.lists.load('common words Google')],
'word_number': [],
'pos_tag': [],
'stem': [],
'lemmatize': [],
'sort_words': [],
'natural_word_order': [],
'normalize': []
}


for method, args in methods.items():
    getattr(wordlist, method)(*args).to_frame().to_csv(f'data/test_wordlist/{method}.csv', index=False)
