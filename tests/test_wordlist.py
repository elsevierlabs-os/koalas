import unittest
import koalas as kl

def load_sample():
    return kl.read_csv(f'tests/data/sample.csv')['term']

def load_result(name):
    return kl.read_csv(f'tests/data/test_wordlist/{name}.csv')['term']


class TestWordList(unittest.TestCase):

    def test_apply(self):
        wordlist = load_sample()
        result = wordlist.apply(lambda term: term in ['Gord Renwick'])
        expected_result = load_result('apply')
        self.assertTrue(result.equals(expected_result))

    def test_remove_words(self):
        wordlist = load_sample()
        stopwords = kl.lists.load('stopwords AnAgram')
        result = wordlist.remove_words(stopwords)
        expected_result = load_result('remove_words')
        self.assertTrue(result.equals(expected_result))

    def test_remove_first_word(self):
        wordlist = load_sample()
        result = wordlist.remove_first_word()
        expected_result = load_result('remove_first_word')
        self.assertTrue(result.equals(expected_result))

    def test_remove_last_word(self):
        wordlist = load_sample()
        result = wordlist.remove_last_word()
        expected_result = load_result('remove_last_word')
        self.assertTrue(result.equals(expected_result))

    def test_replace_substrings(self):
        wordlist = load_sample()
        replacements = {'13': 'thirteen', 'Mr.': 'Mister'}
        result = wordlist.replace_substrings(replacements)
        expected_result = load_result('replace_substrings')
        self.assertTrue(result.equals(expected_result))

    def test_remove_punctuation(self):
        wordlist = load_sample()
        result = wordlist.remove_punctuation()
        expected_result = load_result('remove_punctuation')
        self.assertTrue(result.equals(expected_result))

    def test_remove_qualifiers(self):
        wordlist = load_sample()
        result = wordlist.remove_qualifiers()
        expected_result = load_result('remove_qualifiers')
        self.assertTrue(result.equals(expected_result))

    def test_replace_typographic_forms(self):
        wordlist = load_sample()
        result = wordlist.replace_typographic_forms()
        expected_result = load_result('replace_typographic_forms')
        self.assertTrue(result.equals(expected_result))

    def test_replace_accented_characters(self):
        wordlist = load_sample()
        result = wordlist.replace_accented_characters()
        expected_result = load_result('replace_accented_characters')
        self.assertTrue(result.equals(expected_result))

    def test_remove_accents(self):
        wordlist = kl.WordList(['ȫ', 'Ἒ', 'בּ'])
        result = wordlist.remove_accents()
        expected_result = kl.WordList(['o', 'Ε', 'ב'])
        self.assertTrue(result.equals(expected_result))

    def test_normalize_unicode(self):
        wordlist = kl.WordList(['µ', '𝚨', '𝓧'])
        result = wordlist.normalize_unicode()
        expected_result = kl.WordList(['μ', 'Α', 'X'])
        self.assertTrue(result.equals(expected_result))

    def test_replace_greek_characters(self):
        wordlist = load_sample()
        result = wordlist.replace_greek_characters()
        expected_result = load_result('replace_greek_characters')
        self.assertTrue(result.equals(expected_result))

    def test_replace_words(self):
        wordlist = load_sample()
        replacements = kl.lists.load('medical terms', substitutions=True)
        result = wordlist.replace_accented_characters()
        expected_result = load_result('replace_accented_characters')
        self.assertTrue(result.equals(expected_result))

    def test_word_isin(self):
        wordlist = load_sample()
        commonwords = kl.lists.load('common words Google')
        result = wordlist.word_isin(commonwords)
        expected_result = load_result('word_isin')
        self.assertTrue(result.equals(expected_result))

    def test_term_isin(self):
        wordlist = load_sample()
        commonwords = kl.lists.load('common words Google')
        result = wordlist.term_isin(commonwords)
        expected_result = load_result('term_isin')
        self.assertTrue(result.equals(expected_result))

    def test_word_number(self):
        wordlist = load_sample()
        result = wordlist.word_number()
        expected_result = load_result('word_number')
        self.assertTrue(result.equals(expected_result))

    def test_pos_tag(self):
        wordlist = load_sample()
        result = wordlist.pos_tag()
        expected_result = load_result('pos_tag')
        self.assertTrue(result.apply(str).equals(expected_result))

    def test_stem(self):
        wordlist = load_sample()
        result = wordlist.stem()
        expected_result = load_result('stem')
        self.assertTrue(result.equals(expected_result))

    def test_lemmatize(self):
        wordlist = load_sample()
        result = wordlist.lemmatize()
        expected_result = load_result('lemmatize')
        self.assertTrue(result.equals(expected_result))


    def melt_list(self):
        pass

    def test_exact(self):
        wordlist = load_sample()
        result = wordlist.exact()
        self.assertTrue(result.equals(wordlist))

    def test_extract_acronym(self):
        pass

    def test_sort_words(self):
        wordlist = load_sample()
        result = wordlist.sort_words()
        expected_result = load_result('sort_words')
        self.assertTrue(result.equals(expected_result))

    def test_natural_word_order(self):
        wordlist = load_sample()
        result = wordlist.natural_word_order()
        expected_result = load_result('natural_word_order')
        self.assertTrue(result.equals(expected_result))

    def test_normalize(self):
        wordlist = load_sample()
        result = wordlist.normalize()
        expected_result = load_result('normalize')
        self.assertTrue(result.equals(expected_result))
