import unittest
import numpy as np
import koalas as kl


columns = ['term', 'frequency']

values = [['Rhode Island Tercentenary half dollar', 3.0],
       ['United States Mint', 5.0],
       ['golden-headed cisticola', 10.0],
       ['Gord Renwick', np.nan],
       ['Order of Hockey in Canada', 3.0],
       ['Operation Thunderbolt', 32.0],
       ['Augusta Peaux', 69.0],
       ['Mr. Shivers', 5.0],
       [np.nan, 99.0],
       ['Newbury Park tube station', 9.0],
       ['Jackson Gallagher', 14.0],
       ['Tidying Up with Marie Kondo', 5.0],
       ['Sewer explosions', 23.0],
       ['13th Dalai Lama', 45.0],
       ['Subtropical Storm Andrea (2007)', 61.0],
       ['was assassinated', 61.0],
       ["Cayley's Ω process", 9.0],
       ['List of historical anniversaries', 9.0],
       ['a United States trial', 16.0],
       ['Preparing for a Fancy Dress Ball', 64.0],
       ['Agaricus deserticola', 56.0],
       ['Adenanthos obovatus', 5.0],
       ['Euryoryzomys emmonsae', 0.0],
       ['Uranium', 12.0],
       ['Casino Royale (novel)', np.nan],
       ['α-helix', 11.0],
       ['fatigue syndrome, chronic', 4.0]]

class TestFactories(unittest.TestCase):

    def test_read_csv(self):
        result = kl.read_csv('tests/data/sample.csv')
        expected_result = kl.WordFrame(values, columns=columns)
        self.assertTrue(result.equals(expected_result))

    def test_read_json(self):
        result = kl.read_json('tests/data/test_factories/sample.json')
        expected_result = kl.WordFrame(values, columns=columns)
        self.assertTrue(result.equals(expected_result))

    def test_read_excel(self):
        result = kl.read_excel('tests/data/test_factories/sample.xlsx')
        expected_result = kl.WordFrame(values, columns=columns)
        self.assertTrue(result.equals(expected_result))




