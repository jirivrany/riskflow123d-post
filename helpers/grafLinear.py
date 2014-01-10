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

def value_set(dic, key):
    '''
    test if value is in dict and is not empty
    '''
    if dic.has_key(key) and dic[key]:
        return True
    

def draw_chart(data, settings):
    '''
    draw png file 
    '''
    lab_x = settings['xlabel'] if value_set(settings, 'xlabel') else 'time (s)'
    lab_y = settings['ylabel'] if value_set(settings, 'ylabel') else 'concentration'
    lab_tit = settings['title'] if value_set(settings, 'title') else 'concentration'
    
    plot(data['times'], data['disp'], '-', lw=2)
    xlabel(lab_x)
    ylabel(lab_y)
    title(u'graph of {} for element {}'.format(lab_tit, settings['xkey']))
    grid(True)
    axes()
    savefig('{}element_{}'.format(settings['where'], settings['xkey']))
    close()
    