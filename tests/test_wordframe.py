import unittest
import koalas as kl

def load_sample():
    return kl.read_csv(f'tests/data/sample.csv')

def load_result(name):
    return kl.read_csv(f'tests/data/test_wordframe/{name}.csv')


class TestWordFrame(unittest.TestCase):

    def test_apply(self):
        pass

    def test_rename(self):
        pass

    def test_merge(self):
        pass

    def test_concat(self):
        pass

    def test_apply_by_row(self):
        pass

    def test_apply(self):
        pass

    def test_astype(self):
        wordframe = load_sample()
        result = wordframe.astype(bool, on='frequency')
        expected_result = load_result('astype')
        self.assertTrue(result.equals(expected_result))

    def test_deduplicate(self):
        wordframe = load_sample()
        result = wordframe.deduplicate(on='frequency')
        result.index = list(range(len(result)))
        expected_result = load_result('deduplicate')
        self.assertTrue(result.equals(expected_result))

    def test_filter(self):
        pass

    def test_match_to(self):
        pass

    def test_match_to_self(self):
        pass

    def test_to_json(self):
        pass

    def test_stack_list_same_column(self):
        wordframe = load_sample().apply(list, on='term', to='list')
        result = wordframe.stack_list(on='list')
        expected_result = load_data('stack_list_same_column')
        self.assertTrue(result.equals(expected_result))

    def test_stack_list_different_column(self):
        wordframe = load_sample().apply(list, on='term', to='list')
        result = wordframe.stack_list(on='list', to='term')
        expected_result = load_data('stack_list_different_column')
        self.assertTrue(result.equals(expected_result))
