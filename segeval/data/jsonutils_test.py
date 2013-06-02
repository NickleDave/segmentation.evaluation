'''
Tests the data merge functions and package.

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
'''
import unittest
import os
import re
from .jsonutils import output_linear_mass_json, input_linear_mass_json
from .samples import HEARST_1997_STARGAZER


class TestJsonUtils(unittest.TestCase):
    '''
    Test data merge functions.
    '''
    #pylint: disable=R0904,C0103
    test_data_dir = os.path.split(__file__)[0]
    
    def test_output_linear_mass_json(self):
        '''
        Test ``Dataset.add()``.
        '''
        file_path_new = os.path.join(self.test_data_dir, 'hearst1997_test.json')
        file_path_existing = os.path.join(self.test_data_dir, 'hearst1997.json')
        output_linear_mass_json(file_path_new, HEARST_1997_STARGAZER)
        self.assertEqual(re.sub(r'\s+', '', open(file_path_new).read()),
                         re.sub(r'\s', '',open(file_path_existing).read()))
        os.remove(file_path_new)
        self.assertFalse(os.path.exists(file_path_new))
        
    def test_input_linear_mass_json(self):
        '''
        Test mass JSON file input.
        '''
        json_file = os.path.join(self.test_data_dir, 'hearst1997.json')
        dataset = input_linear_mass_json(json_file)
        self.assertEqual(dataset, HEARST_1997_STARGAZER)