#!/usr/bin/env python

'''
Module for handling surface elements 
'''
import mesh

def read_result(fname):
    '''
    reads file of surface elements to list
    '''
    elems = []
    try:
        resfile = open(fname, "r")
    except IOError:
        print 'failed to read file %s' % fname
        return False
    else:        
        for line in resfile:
            line = line.strip()
            elems.append(line)
    
    return elems        
        
def read(bcd_name,msh_name):
    """
    Read a Flow .bcd file for surface elements
    need a .msh file to apply 3D elements filtering
    returns list of surface elements
    """
    elements = []
    readmode = 0
    typ = 0
    where  = 0
    height_limit = 10
    
    mshfile = open(bcd_name, "r")
    for line in mshfile:
        line = line.strip()
        if line.startswith('$'):
            if line == '$BoundaryConditions':
                readmode = 1
            else:
                readmode = 0
        elif readmode:
            columns = line.split()
            if len(columns) > 5:
                #first column is type of condition
                typ = int(columns[1])
                #consider only type 1
                if typ == 1: 
                    ptr = 3 
                    where = int(columns[ptr])
                    if where in (2, 3) and abs(float(columns[2])) < height_limit:
                        try:
                            elements.append(int(columns[ptr+1]))
                        except ValueError:
                            print 'Element format error: '+line
                            readmode = 0
                         
    
    
        
    return __filter_3d(elements, msh_name)

def __filter_3d(elements,msh_name):
    '''apply filter for 3d elements only'''
    msh = mesh.Mesh()
    msh.read(msh_name)
    #filter list of 3D elems
    three_dee = [elmid for elmid, elmtup in msh.elements.items() if elmtup[0] == 4]
    return [elmid for elmid in elements if elmid in three_dee]

def write(fname,elements):
    '''
    write list of elements to disk 
    output format / single element per line
    '''
    try:
        output = open(fname,'w')
    except IOError:
        print 'failed to create file %s' % fname
    else:
        for line in elements:
            output.write(str(line))
            output.write('\n')
        output.close()    


if __name__ == '__main__':
    FILENA = '../../data/01/mm.bcd'
    FIMSH = '../../data/01/mm.msh'
    ELM = read(FILENA, FIMSH)
    print ELM
    
    
    