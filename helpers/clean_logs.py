#!/usr/bin/env python
'''
Created on 25.1.2012

@author: albert
'''
import os
import getopt
import sys

def clean(dir_name):
    '''
    recursively clean up dirname
    deletes flow123.0.log files
    deletes cluster.sh.o* files (for RiskFlow) 
    '''
    print 'starting clean-up'
    smazano = 0
    for root, dirs, files in os.walk(dir_name):
        del(dirs)
        for fname in files:
            tpth = '/'.join([root, fname])
            if fname == 'flow123.0.log' or fname.startswith('cluster.sh.o'):
                try:
                    os.remove(tpth)
                except os.error:
                    print 'nelze smazat flow.log log / chyba pristupu'
                else:
                    smazano += 1        
    
    print 'deleted %s flow123.0.log and clusters.sh.o files' % smazano

def usage():
    '''
    shows help
    '''
    print 'Tool for flow123d clean-up.'
    print 'Older version of Flow makes very long log files / use this tool to recursively clean up dir if you don\'t need this logs.'
    print 'usage: clean_logs -d dirname '
    
def main():
    '''
    getopt main procedure
    '''
    try:
        opts, _111 = getopt.getopt(sys.argv[1:], "d:h", ["dir=", "help"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
        
    if len(opts) == 0:
        usage()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--dir"):
            clean(arg)
        else:
            usage()
            sys.exit()

if __name__ == "__main__":
    main()
    