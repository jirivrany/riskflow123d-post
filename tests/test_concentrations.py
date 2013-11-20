#!/usr/bin/env python
# coding: utf-8
import unittest
import src.helpers.concentrations as conc
import src.flowIni.transport as trans

class Test(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        inpt = '../../data/post/Sensitivity/002/conc_suma'
        self.data = trans.load_vysledek(inpt)
        
    def test_sum_selected(self):
        
        teslist = ['19459','19704','19690']
        resu = 0.009987 + 0.002993 + 5.4e-05
        self.assertEquals(conc.sum_conc_for_selected(teslist, self.data), resu)    

    def test_sum_all(self):
        resu = 13.625943
        self.assertEquals(conc.sum_conc_all(self.data), resu)
    

    def test_grade_result(self):
        conc_list = [5,12,30,50]
        original = 10.0
        grades = [0,1,4,5]
        self.assertListEqual(grades, conc.grade_result(original, conc_list))    

if __name__ == "__main__":
    unittest.main()
    