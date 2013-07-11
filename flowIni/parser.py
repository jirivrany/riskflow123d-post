import os.path
# To change this template, choose Tools | Templates
# and open the template in the editor.
# coding: utf-8
__author__="albert"
__date__ ="$10.8.2011 13:37:40$"

import sys
import os

# @TODO metodu open ktera otevre soubor pro dalsi zpracovani
# @TODO metody pro nacteni hodnot jednotlivych dilcich souboru
# jak na parsovani? - zajimave radky jsou vzdy klic = hodnota
# nejlepsi tedy bude cely soubor nacist a ze zajimavych radek po nacteni vytvorit slovnik
# jednotlive hodnoty tak budou snadno pristupne

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

class Parser:
    '''flow.ini file parser'''
    def __init__(self):
        '''open the ini file and creates dictionary with values of interest'''
        
        self.values = {}
        self.file = None
        self.listOfInterest = dictOfExtensions.keys()
    
    def __fileOpen(self, fileName):
        '''open file with given name'''
        try:
            self.file = open(fileName, "r")
            
        except IOError:
            print os.listdir(os.curdir)
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def __getDataFromSource(self):
        '''parses open file'''
        try:
            for line in self.file:
                self.__parse(line)
        except:
            e = sys.exc_info()[1]
            print ('Error: %s</p>' % e )

    def __fileClose(self):
        try:
            self.file.close()
        except IOError:
            print ('failed to close file %s' % self.file)

    def __parse(self,line):
        '''method for inheritance
        '''
        pass
