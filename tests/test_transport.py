#!/usr/bin/env python
# coding: utf-8
import unittest
import src.flowIni.transport as trans

class Test(unittest.TestCase):
    
    def testGetName(self):
        fname = '../../data/flow_test.ini'
        self.assertEquals('transport.msh', trans.get_name_from_ini_file(fname))
        
    def test_vysledek_load(self):
        inpt = '../../data/post/Sensitivity/001/elements_concentration'
        data = trans.load_vysledek(inpt)
        resu = {u'480.0': 1e-06, u'500.0': 1e-06}
        self.assertDictEqual(data['19506'], resu)    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    