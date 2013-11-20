#!/usr/bin/env python
# coding: utf-8
import unittest
import src.flowIni.material as material

TEST_KEYS = ['9617', '9207', '4300', '9612', '9200', '9107', '9100', '4100', '9400', '4200', '9307', '9300', '2200', '2207', '9517', '9312', '1112', '9407', '1117', '9512', '9600', '9607', '9500', '9112', '9317', '9507', '9117', '4500', '9212', '9217', '4600', '2212', '2217', '4400', '1107', '9412', '1100', '9417']

class Test(unittest.TestCase):
    
    def test_file_load(self):
        inpt = '../../data/tests/material/mm.mtr'
        p = material.Material()
        slovnik = p.getDictFromFile(inpt)
        self.assertListEqual(TEST_KEYS, slovnik.keys(), 'chyba pri nahrani souboru mm.mtr')    

    def test_bad_load(self):
        inpt = '../../data/tests/material/mtr_v5_10_2.mtr'
        p = material.Material()
        self.assertRaises(material.EmptyListException, p.getDictFromFile, inpt)
        #self.assertListEqual(TEST_KEYS, slovnik.keys(), 'chyba pri nahrani souboru mm.mtr')    


def run_all():
    '''
    run all test in module
    '''
    unittest.main()
    
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    run_all()
    