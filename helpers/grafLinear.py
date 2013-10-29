'''
Created on 18.1.2012

@author: albert
'''
from matplotlib import use
use('Agg')
from matplotlib.pyplot import plot, xlabel, ylabel, title, grid, axes, savefig, close


def fill_up_zeros(times, xval):
    disp = []
    for key in times:
        key = str(key)
        if xval.has_key(key):
            disp.append(xval[key])
        else:
            disp.append(0)
            
    return disp

def list_filter(dct, flt):
    '''
    selects only elements in filter [] from dict {}
    converts key to str
    '''
    temp = {}
    for key in flt:
        key = str(key)
        if dct.has_key(key):
            temp[key] = dct[key]
    return temp

def draw_chart(xkey, times, disp, where):
    plot(times, disp, '-', lw=2)
    xlabel('time (s)')
    ylabel('concentration')
    title('graph of concentration for element {}'.format(xkey))
    grid(True)
    axes()
    savefig('{}element_{}'.format(where,xkey))
    close()
    