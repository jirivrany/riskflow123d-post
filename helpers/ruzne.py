'''
Created on 16.11.2011

@author: albert
'''
import os.path

def format_time(given_time):
    '''
    converts given number to time string
    >>> format_time(124)
    '2 min 4 sec'
    >>> format_time(3601)
    '1 h 1 sec'
    >>> format_time(60)
    '1 min '
    '''
    result = ''
    hour = given_time / 3600
    if hour >= 1:
        result = '%d h ' % hour
        given_time = given_time - round(hour) * 3600 
    minut = given_time / 60
    if minut >= 1:
        result += '%d min ' % minut
        given_time = given_time - round(minut) * 60 
    sec = given_time
    if sec > 0:     
        result += '%d sec' % sec
        
    return result    

def isit_task_folder(dirname):
    '''Test if provided dirname contains master folder'''
    return os.path.isfile(dirname + '/problem.type')


def text2floatmp(text):
    '''returns a float or 1 for multiplication'''
    if text != '': 
        return float(text)
    else: 
        return 1

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    