# coding: utf-8
__author__="albert"
__date__ ="$10.8.2011 13:37:40$"

import re
import basicParser
import os.path

import inspect


orderOfMtr = (
 'Materials',
 'Storativity',
 'Geometry',
 'Sorption',
 'SorptionFraction',
 'DualPorosity',
 'Reactions'
 )

fileHead = '''$MaterialFormat
1.0  0  8
$EndMaterialFormat
'''

class EmptyListException(BaseException):
    pass


class Matdata(object):
    
    def __init__(self):
        self.id = 0
        self.type = 0
        self.type_spec = 0.0
        self.storativity = []
        self.sorption = []
        self.dualporosity = []
        self.sorptionfraction = []
        self.geometry = []
        self.reactions = []
        
    def __str__(self):
        boring = dir(type('dummy', (object,), {}))
        it = [item
            for item in inspect.getmembers(self)
            if item[0] not in boring]
        return str(it)



class Material(basicParser.BasicParser):
    '''flow.ini file parser'''
    def __init__(self):
        '''open the ini file and creates dictionary with values of interest'''
        basicParser.BasicParser.__init__(self)
        self.material = Matdata
        self.values = {}
        self.file = None
        self.attribute = False
        self.cleanCollections()
        
    def cleanCollections(self):
        self.li_materials = []
        self.li_storativity = []
        self.li_sorption = []
        self.li_dualporosity = []
        self.li_sorptionfraction = []
        self.li_geometry = []
        self.li_reactions = []
        
        
    def saveDictToFile(self,fileName,dictName = 'self'):
        '''
        Stores dictionary of material objects to given file
        '''
        try:
            outFile = open(fileName,'w')
        except IOError:
            adr = os.path.dirname(fileName)
            try: 
                os.mkdir(adr)
                outFile = open(fileName,'w')
            except IOError:    
                print 'Error: file %s did not exists. Failed to create dir %s' % (fileName,adr)
                return
        
        self.cleanCollections()
        self.dictToCollections(dictName)
        
        outFile.write(fileHead)
        for mtr_prop in orderOfMtr:
            outFile.write('$'+mtr_prop+'\n')
            liname = 'li_'+mtr_prop.lower()
            if mtr_prop == 'Materials': outFile.write(str(len(self.li_materials))+'\n')
            for line in getattr(self,liname):
                outFile.write(line)
                outFile.write('\n')
            outFile.write('$End'+mtr_prop+'\n')
                        
        self.restart_app_clear(outFile)   
            
    def dictToCollections(self,workdct = 'self'):
        '''
        Converts values dir to self.li_attrname lists of attributes
        '''
        if workdct == 'self':
            workdct = self.values
        
        for key in sorted(workdct.keys()):
            tempO = workdct[key]
            vlast = [e for e in dir(tempO) if isinstance(getattr(tempO,e),(list))] 
            matStr = '%s\t%s\t%s' % (tempO.id, tempO.type, tempO.type_spec)
            self.li_materials.append(matStr)
            for attribute1 in vlast:
                atStr = False
                if len(getattr(tempO,attribute1)) > 0:
                    atStr = str(tempO.id)
                    for atVal in getattr(tempO,attribute1):
                        atStr += '\t'
                        atStr += atVal
                
                if atStr:        
                    getattr(self,'li_' + attribute1).append(atStr)  
        
    def getDictFromFile(self, fileName):
        '''@param fileName
           @return Dictionary of values'''
        self.dialog_ini_file_open(fileName)
        self.getDataFromSource()
        self.restart_app_clear()
        if len(self.values) == 0:
            raise EmptyListException("Failed to load data from Material file. Check if it's in correct format.")
        else:
            return self.values

    def parse(self,line):
        '''search a line for =, parser values to a dict if succeed
           interested only for items in listOfInterest 
        '''
        try:
            line = line.strip()
            if line.count('$') == 1:
                if (line.count('$End')) == 1:
                    self.attribute = False
                else:
                    self.attribute = line[1:].lower()
                    
            else:
                filtr = re.compile('\s{1,}')
                line = filtr.sub(';',line)
                #print '%s = %s' % (self.attribute,line)
                if self.attribute == 'materials' and line.count(';'):
                    key,type,type_spec = line.split(';')
                    if not(self.values.has_key(key)):
                        to = self.material()
                        to.id = key
                        to.type = type
                        to.type_spec = type_spec
                        self.values[key] = to
                        
                   
                elif(self.attribute.count('density') == 0):
                    data = line.split(';')
                    
                    key = data[0]
                    if self.values.has_key(key) and data[1:]:
                        getattr(self.values[key],self.attribute).extend(data[1:])
                        
        except ValueError:
            pass
