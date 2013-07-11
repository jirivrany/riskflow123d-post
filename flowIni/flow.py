# To change this template, choose Tools | Templates
# and open the template in the editor.
# coding: utf-8
__author__="albert"
__date__ ="$10.8.2011 13:37:40$"

import os.path
from iniparse import INIConfig 

dictOfExtensions = {
                    'Input':{'Mesh':'msh','Material':'mtr','Boundary':'bcd','Neighbouring':'ngh'}, 
                    'Transport' :{'Concentration':'tic','Transport_BCD':'tbc','Transport_out':'pos'},
                    }

dictOfLabels = {'Mesh':'msh','Material':'mtr','Boundary':'bcd','Neighbouring':'ngh', 'Concentration':'tic','Transport_BCD':'tbc','Transport_out':'pos'}
                    

def openFile(fileName):
        '''@param filenName
        Try open a file, throws exception if file not exist'''
        try:
            ff = open(fileName)
            return ff
        except IOError:
            return None
        
def getDictFromFile(fileName):
    '''@param fileName
       @return Dictionary of values'''
    f = openFile(fileName)
    va = parse(f)
    f.close
    return va

def parser(fileObject):
    '''
    @param: fileObject - opened file
    @return: iniparse object 
    '''
    try:
        par = INIConfig(fileObject)
        return par
    except IOError:
        pass

def parse(fileObject):
    '''search a file for values
    @param fileObject - opened file
    @return vals - {} of values
    '''
    values = {} 
    pa = parser(fileObject)
    for k in dictOfExtensions.keys():
        for j in dictOfExtensions[k].keys():
            values[j] = pa[k][j]
     
    return values       

if __name__ == '__main__':
    #fileName = '../../../data/01_steady_flow_123d/flow_matis.ini'
    fileName = '../../../data/01/flow_t.ini'
    adr = os.path.dirname(fileName)
    print adr
    slovnik = getDictFromFile(fileName)
    for key,name in slovnik.items():
        fname = adr + os.sep +name
        test = openFile(fname)
        if test:
            print '%s is OK' % key
        else:
             print "failed to open %s file" % key