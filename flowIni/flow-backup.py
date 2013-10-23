# To change this template, choose Tools | Templates
# and open the template in the editor.
# coding: utf-8
__author__="albert"
__date__ ="$10.8.2011 13:37:40$"

import sys
import os
import basicParser

dictOfExtensions = {'Mesh':'msh','Material':'mtr','Boundary':'bcd','Neighbouring':'ngh','Concentration':'tic','Transport_BCD':'tbc'}

def openFile(fileName):
        '''@param filenName
        Try open a file, throws exception if file not exist'''
        try:
            text = open(fileName)
            return text
            close(fileName)
        except IOError:
            return False

class Flow(basicParser.BasicParser):
    '''flow.ini file parser'''
    def __init__(self):
        '''open the ini file and creates dictionary with values of interest'''
        
        self.values = {}
        self.file = None
        self.listOfInterest = dictOfExtensions.keys()
        
    def getDictFromFile(self, fileName):
        '''@param fileName
           @return Dictionary of values'''
        self.fileOpen(fileName)
        self.getDataFromSource()
        self.fileClose()
        return self.values

    def getDictFromString(self, stringName):
        '''@param fileName
           @return Dictionary of values'''
        self.file = stringName
        party = self.file.split('\n')
        self.file = party
        self.getDataFromSource()
        return self.values

    def parse(self,line):
        '''search a line for =, parser values to a dict if succeed
           interested only for items in listOfInterest 
        '''
        try:
            parts = line.split('=')
            
        except ValueError:
            pass

        if len(parts) > 1:
            key = parts[0].strip()
            value = parts[1].strip()
            if key in self.listOfInterest:
                self.values[key] = value

if __name__ == '__main__':
    fileName = '../../../data/01_steady_flow_123d/flow_matis.ini'
    #fileName = '../../data/flow_test.ini'
    p = Flow()
    dir = os.path.dirname(fileName)
    slovnik = p.getDictFromFile(fileName)
    for key,name in slovnik.items():
        fname = dir + name
        test = openFile(fname)
        if test:
            print '%s is OK' % key
        else:
             print "failed to open %s file" % key