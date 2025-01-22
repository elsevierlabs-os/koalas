import unittest
import koalas as kl


class TestMatching(unittest.TestCase):

    def test_match_to(self):
        a = kl.WordFrame({'label': ['first', 'second', 'THREEs']})
        b = kl.WordFrame({'label': ['first', 'second', 'THREEs']})
        self.assertTrue(all(a.match_to(b, on='label')[['matched_how']] == kl.WordFrame({'matched_how': ['exactly', 'exactly', 'exactly']})))
