'''
Created on 29.8.2012
@author: albert
'''
from collections import defaultdict
from numpy import median, average
from scipy.stats.mstats import mquantiles

COLS = "time; master; median; average; 5%quantile; 95%quantile; values(comma separated)"

def merge_dict(list_of_dict):
        '''
        merge list of dict using defaultdict
        values with same key are append to list
        '''
        defdic = defaultdict(list)
        for d in list_of_dict:
            for key, value in d.iteritems():
                defdic[key].append(value)
                
        return defdic

def table_to_file(merged_table, master_conc, output_file, tasks, minval = 0.0):
    '''print table to file
    merged table is indexed by elements
    in table is list of time dicts
    '''
    try:
        fww = open(output_file,'w')
    except IOError:
        print 'failed to open file %s' % output_file    
    else:
        print >> fww, COLS
        for yyy in merged_table.iterkeys():            
                xxx = merge_dict(merged_table[yyy])
                try:
                    mxxx = master_conc[yyy]
                except KeyError:
                    pass    
                
                print >> fww, yyy
                for k in sorted(float(x) for x in xxx.iterkeys()):
                    v = [x for x in xxx[str(k)] if x > minval]
                    fv = v[:]
                    zeros = tasks-len(v)
                    if zeros > 0:
                        fv.extend([0]*zeros)
                    temp_str = ';'.join(str(x) for x in sorted(v))
                    quant_str = ';'.join(str(x) for x in mquantiles(fv, [0.05, 0.95]))
                    try:
                        master_tcon = mxxx[str(k)]
                    except KeyError:
                        master_tcon = 0.0
                            
                    if temp_str:
                        print >> fww, '{};{};{};{};{};{}'.format(k, master_tcon ,median(fv), average(fv), quant_str, temp_str)

if __name__ == '__main__':
    pass