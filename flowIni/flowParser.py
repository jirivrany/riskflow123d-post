# To change this template, choose Tools | Templates
# and open the template in the editor.
# coding: utf-8
__author__="albert"
__date__ ="$10.8.2011 13:37:40$"

from iniparse import INIConfig 

# @TODO metodu open ktera otevre soubor pro dalsi zpracovani
# @TODO metody pro nacteni hodnot jednotlivych dilcich souboru
# jak na parsovani? - zajimave radky jsou vzdy klic = hodnota
# nejlepsi tedy bude cely soubor nacist a ze zajimavych radek po nacteni vytvorit slovnik
# jednotlive hodnoty tak budou snadno pristupne

dictOfExtensions = {
                    'Input':{'Mesh':'msh','Material':'mtr','Boundary':'bcd','Neighbouring':'ngh'}, 
                    'Transport' :{'Concentration':'tic','Transport_BCD':'tbc'}
                    }


if __name__ == '__main__':
    '''
    fileName = '../../../data/01_steady_flow_123d/flow_matis.ini'
    #fileName = '../../data/flow_test.ini'
    pa = INIConfig(open(fileName))
    for k in dictOfExtensions.keys():
        for j in dictOfExtensions[k].keys():
            print pa[k][j]
    '''
    fr = open('../riskFlow123d.ini')
    pa = INIConfig(fr)
    fr.close()
    #test zapisu
    pa['Output']['Dir'] = './RF123dOutput/'
    pa['Launcher']['Local'] = False
    pa['Launcher']['Local_bin'] = 'C:/'
    pa['Launcher']['Cluster'] = False
    ff = open('../riskFlow123d.ini','w')
    print >> ff, pa
    ff.close()
    