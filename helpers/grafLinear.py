'''
Created on 18.1.2012

@author: albert
'''
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt


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
    plt.plot(times, disp, '-', lw=2)
    plt.xlabel('time (s)')
    plt.ylabel('concentration')
    plt.title('graph of concentration for element {}'.format(xkey))
    plt.grid(True)
    plt.axes()
    plt.savefig('{}element_{}'.format(where,xkey))
    plt.close()
    

if __name__ == '__main__':
    import pickle
    fo = open('../../../data/output_zpracovany.pickle','rb')
    data = pickle.load(fo)
    times = pickle.load(fo)
    print times
    fo.close()
    
    print data.items()
    for xkey, xval in data.items():
        disp = fill_up_zeros(times, xval)         
        draw_chart(times,disp,'../../../data/grafy/')
        