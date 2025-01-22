import unittest
import koalas as kl
import koalas.scripts.binomial_name

class TestBinomialNameScript(unittest.TestCase):

    def test_binomial_name(self):
        candidates = kl.WordList(['Homo sapiens', 'Aluminium dioxide',
                                  'Arabidopsis thaliana', 'Bacillus ssp.'])
        binomial_name = candidates.script.is_binomial_name()
        self.assertTrue(all(binomial_name == [True, False, True, True]))
