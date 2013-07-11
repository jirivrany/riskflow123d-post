# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest
from flowIni import flow


class  Parser_TestCase(unittest.TestCase):
    def setUp(self):
        self.file = './data/flow_test.ini'
        self.P = flow.Flow()
    

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def testParseFromFile(self):
        mesh = {'Mesh' : './input/test1.msh'}
        self.P.listOfInterest = ['Mesh',]
        self.assertDictEqual(mesh, self.P.getDictFromFile(self.file), 'parser souboru nefunguje')

    def testParseFromString(self):
        mesh = {'Mesh' : './input/test1.msh'}
        self.P.listOfInterest = ['Mesh',]
        data = '''[Global]
            Problem_type	  = 1
            Description       = test1
            Stop_time	  = 5   //1275
            Save_step 	  = 0.1
            Density_steps     = 50
            Density_on        = No



            [Density]
            Density_max_iter  =21
            Density_implicit  = 1
            Eps_iter          =1e-5
            Write_iterations  = 0

            [Input]
            File_type         = 1
            Mesh              = ./input/test1.msh
            Material          = ./input/test1.mtr
            Boundary          = ./input/test1.fbc
            Neighbouring      = ./input/test1.ngh

            [Transport]
            Transport_on	  	= No
            Sorption 	  	= No
            Dual_porosity	  	= No
            Concentration	  	= test1.tic
            Transport_BCD	  	= test1.tbc
            Transport_out     	= transport.msh
            Transport_out_im     	= NULL
            Transport_out_sorp     	= NULL
            Transport_out_im_sorp  	= NULL
            N_substances      	= 1
            Substances	  	= A B C	D E F G H I J
            Substances_density_scales =	1	1	1'''
            
        self.assertDictEqual(mesh, self.P.getDictFromString(data), 'parser string nefunguje')

if __name__ == '__main__':
    unittest.main()

