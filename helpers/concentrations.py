'''
Created on 16.2.2012

@author: albert
'''
import bisect

def sum_conc(conc_suma, el_list):
    '''
    wrapper for universal call
    '''
    if not el_list:
        result = sum_conc_all(conc_suma)
    else:
        result = sum_conc_for_selected(el_list, conc_suma)    
    return result    
        
def sum_conc_all(conc_suma):
    '''
    sum values in dict
    :param: conc_suma - dict {elid : conc}
    :return: total_suma - sum of contentrations on selected elements
    '''
    suma = 0.0
    for vals in conc_suma.values():
        suma += vals
    return suma

def sum_conc_for_selected(el_list, conc_suma):
    '''
    sum concentration for given list of elements
    :param: el_list - list of elements
    :param: conc_suma - dict {elid : conc}
    :return: total_suma - sum of contentrations on selected elements
    conc_suma has str keys - numeric values must be converted
    '''
    rslt = 0.0
    for el_id in el_list:
        if conc_suma.has_key(str(el_id)):
            rslt += conc_suma[str(el_id)]
            
    return rslt

def grade_result(original, conc_list):
    '''
    grading method for concentration analysis
    :param original = original value
    :param conc_list = list of results to be compared
    :return = list of grades
    uses bisect for interval checking
    '''

    result = []
    if original == 0:
        return result
    divided_list = [float(ccc) / float(original) for ccc in conc_list]
    max_div = max(divided_list)
    if max_div < 2:
        max_div = 2.0
    grading_exp = [0.2, 0.4, 0.6, 0.8]
    grading_scale = [max_div ** expo for expo in grading_exp]
    
    for value in divided_list:
        
        if value < 1:
            result.append(0)
        else: 
            result.append(bisect.bisect_left(grading_scale, value)+1)

    return result        