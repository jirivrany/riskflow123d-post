'''
Created on 18.1.2012

@author: albert
'''

from grafLinear import fill_up_zeros
from os import path

SINGLE_NAME = 'concentrations.csv'
COMP_NAME = 'conc_comparsion.csv'

def write_comparsion_tab(table_rows, whereto, substance_name=None):
    '''
    writes comparsion table to csv
    @param table_rows: (element_id,suma,grade)
    @param whereto: output dir 
    '''
    if substance_name:
        cname = COMP_NAME[:-4] + '_' + substance_name + '.csv'
        filename = path.join(whereto, cname)
    else:
        filename = path.join(whereto, COMP_NAME)

    out_file = open(filename,'w')
    print >> out_file,'element;sum;grade'
    for element, suma, grade in table_rows:
        print >> out_file, '{};{};{}'.format(element, suma, grade)
        
    out_file.close()    


def write_single_conc_tab(data, times, whereto):
    '''
    writes sparse concentration table to dense csv file
    @param data: sparse {}
    @param times: times []
    @param whereto: output dir 
    '''
    
    out_file = open(path.join(whereto, SINGLE_NAME), 'w')

    print >> out_file, 'elem./time;'+';'.join(map(str, times))
    for xkey, xval in data.items():
        disp = fill_up_zeros(times, xval)         
        vals = ';'.join(map(str, disp))
        print >> out_file, '{};{}'.format(xkey, vals)
        
    out_file.close()    

if __name__ == '__main__':
    import pickle
    FOP = open('../../../data/output_zpracovany.pickle', 'rb')
    MYDATA = pickle.load(FOP)
    MYTIME = pickle.load(FOP)
    FOP.close()
    
    write_single_conc_tab(MYDATA, MYTIME, '../../../data/')
    
    
    