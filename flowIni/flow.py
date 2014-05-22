# coding: utf-8
'''
Parser for Flow.ini file. Works with Flow 1.6.x format.
'''

__author__ = "Jiri Vrany"
__date__  = "$23.10.2012$"


from iniparse import INIConfig
from os import sep

SEPAR = sep 

EXTENSIONS_DICT = {
                    'Input':{ 'Mesh':'msh',
                              'Material':'mtr', 
                              'Boundary':'bcd', 
                              'Neighbouring':'ngh'},
                    
                    'Transport' :{'Concentration':'ict', 
                                  'Transport_BCD':'bct', 
                                  'Transport_out':'pos'},
                    }

LABELS_DICT = {'Mesh':'msh', 
               'Material':'mtr', 
               'Boundary':'bcd', 
               'Neighbouring':'ngh', 
               'Concentration':'ict', 
               'Transport_BCD':'bct', 
               'Transport_out':'pos'}

def change_paths_in_file(file_name, new_dir_name):
    '''
    accepts list of changes
    @param fname: file name to save   
    '''
    with open(file_name, 'r') as confile:
        current_config = INIConfig(confile) 
        for dic_key in EXTENSIONS_DICT.keys():
            for iner_key in EXTENSIONS_DICT[dic_key].keys():
                current_config[dic_key][iner_key] = new_dir_name + SEPAR + current_config[dic_key][iner_key]
    
    with open(file_name, 'w') as confile:
        print >> confile, current_config
                    

def open_file(file_name):
    '''@param filenName
    Try open a file, throws exception if file not exist'''
    try:
        wfile = open(file_name)
        return wfile
    except IOError:
        return None
        
def get_txt_from_file(fname):
    '''
    @param fname / get a text from inifile
    '''
    fini = open_file(fname)
    txt = fini.read()
    fini.close()
    return txt
            
        
def get_dict_from_file(fname):
    '''@param fname
       @return Dictionary of values'''
    data = open_file(fname)
    vals = parse(data)
    data.close()
    return vals


def get_substances_from_file(fname):
    '''@param fname
       @return Dictionary of values'''
    data = open_file(fname)
    vals = parse_substances(data)
    data.close()
    return vals


def parser(opened_file):
    '''
    @param: opened_file - opened file
    @return: iniparse object 
    '''
    try:
        par = INIConfig(opened_file)
        return par
    except IOError:
        print "failed to handle file"

def parse(opened_file):
    '''search a file for values
    @param opened_file - opened file
    @return vals - {} of values
    '''
    values = {} 
    pars = parser(opened_file)
    for key in EXTENSIONS_DICT.keys():
        for in_key in EXTENSIONS_DICT[key].keys():
            values[in_key] = pars[key][in_key]
     
    return values       

def parse_substances(opened_file):
    '''search a file for values
    @param opened_file - opened file
    @return vals - {} of values
    '''
    values = {
              'Sorption': False,
              'Dual_porosity': False,
              'N_substances': 0,
              'Substances': None
              } 
    pars = parser(opened_file)
    for key in values.keys():
        values[key] = pars['Transport'][key]
     
    return values       

