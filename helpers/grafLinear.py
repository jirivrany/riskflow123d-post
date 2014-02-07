'''
Created on 18.1.2012

@author: albert
'''
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from ruzne import value_set

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
    

def draw_chart(data, settings):
    '''
    draw png file 
    '''
    
    
    lab_x = settings['xlabel'] if value_set(settings, 'xlabel') else 'time (s)'
    lab_y = settings['ylabel'] if value_set(settings, 'ylabel') else 'concentration'
    lab_tit = settings['title'] if value_set(settings, 'title') else 'concentration'
    
    plt.clf()
    plt.plot(data['times'], data['disp'], '-', lw=2)
    plt.xlabel(u'{}'.format(lab_x))
    plt.ylabel(u'{}'.format(lab_y))
    plt.title(u'graph of {} for element {}'.format(lab_tit, settings['xkey']))
    plt.grid(True)
    plt.axes()
    plt.savefig('{}element_{}'.format(settings['where'], settings['xkey']))
    plt.close()
    