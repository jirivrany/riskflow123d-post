'''
Created on 11.10.2012

@author: albert
'''
import os
from genericpath import exists

DIRNAME = {'Monte Carlo' : 'MonteCarlo', 'Sensitivity Task' : 'Sensitivity', 'Basic Problem' : 'basicProblem'}
SEPARATOR = '/'

        
def set_output_dir(start_dir, method):
    '''
    output dir string builder
    '''
    output_dir = start_dir + SEPARATOR + DIRNAME[method] + SEPARATOR
    return output_dir
    
def create_if_not_exists(output_dir):
    '''
    if output dir not exsist create it
    if it's not empty display warning
    '''
        
    wmsg = False
    if not exists(output_dir):
        os.mkdir(output_dir)
        wmsg = "Output dir created"
    elif os.listdir(output_dir) != []: 
        wmsg = 'WARNING: {} is not empty, existing data will be overwritten'.format(output_dir)
        
    return wmsg
        
