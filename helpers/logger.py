'''
Created on 10.11.2011

@author: albert
'''
import logging

def create_logger(name,fname):
    x = logging.getLogger(name)
    x.setLevel(logging.DEBUG)
    h = logging.FileHandler(fname)
    f = logging.Formatter("%(levelname)s %(asctime)s %(message)s")
    h.setFormatter(f)
    x.addHandler(h)

def get_it(an, lf):
    create_logger(an, lf)
    lg = logging.getLogger(an)
    return lg

if __name__ == '__main__':
    '''test'''
    an = 'RiskFlow'
    ld = '../../../data/01/'
    lf = '{}{}.log'.format(ld,an.lower())
    lg = get_it(an,lf)
    lg.info('all test passed')