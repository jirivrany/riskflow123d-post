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


def openFile(fileName):
        '''@param filenName
        Try open a file, throws exception if file not exist'''
        try:
            text = open(fileName,'r')
            return text
        except IOError:
            return False

class BasicParser(object):
    '''flow.ini file parser'''
    def __init__(self):
        '''open the ini file and creates dictionary with values of interest'''
        self.values = {}
        self.file = None
    
    def dialog_ini_file_open(self, fileName):
        '''open file with given name'''
        try:
            self.file = open(fileName, "r")
            
        except IOError:
            print os.listdir(os.curdir)
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getDataFromSource(self):
        '''parses open file line by line'''
        try:
            for line in self.file:
                self.parse(line)
        except:
            e = sys.exc_info()[1]
            print ('Error: %s</p>' % e )

    def restart_app_clear(self,fileName = None):
        if fileName == None: fileName = self.file
        try:
            fileName.close()
        except IOError:
            print ('failed to close file %s' % self.file)

    def parse(self,line):
        '''method for inheritance
        '''
        pass
