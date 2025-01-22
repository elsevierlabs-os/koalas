import unittest
import pandas as pd
import koalas as kl
import os

class TestListLoader(unittest.TestCase):

    def test_load_lists(self):
        for filename in os.listdir('koalas/lists'):
            if filename.endswith('.json'):
                listname = filename.replace('.json', '')
                with self.subTest(i=listname):
                    koalas_list = kl.lists.load(listname)
                    self.assertTrue(koalas_list is not None)
