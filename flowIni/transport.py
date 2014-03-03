#!/opt/python/bin/python
'''
@author: Jiri Vrany
A module for handling flow123d transport output
Parses transport_out pos file, takes only non-zero values of concetrations
and saves them to json file, also saves list of times (even if all conc at 
such time was zero).  
'''

from multiprocessing import Process, Queue, cpu_count
from iniparse import INIConfig
import os
import time
import getopt
import sys
import shutil

import flow

FNAME_TIME = 'times'
FNAME_ELEMS = 'elements_concentration'
FNAME_SUMA = 'conc_suma'
FNAME_EXT = {'json':'json', 'pickle':'pck'}

def worker(input_queue, done_queue, substances=False):
    '''
    Worker process - takes data from input, saves results to disk
    and puts time of computation to output
    
    :param: input_queue / multiprocessing Queue
    :param: output_queue / multiprocessing Queue
    '''
    for reseni in iter(input_queue.get, 'STOP'):
        start_time = time.time() 
        #grabs host from queue
        if substances:
            work_on_multiple_substances(reseni)
        else:    
            work_on_single_substance(reseni)
        
        done_queue.put(time.time() - start_time)

        
def read_transport(fname, suma=False, substances=False):
    """
    Read a Flow .pos file.
    @param: suma - set True if sum of concentration has to be computed too
    """
    try:
        with open(fname, "r") as mshfile:
            data = mshfile.readlines()
    except IOError:
        print 'Error - failed to open file %s ' % fname
    else:
        #in result times, elements, elems_suma
        if substances:
            result = parse_multiple_substances(data, suma)
        else:
            result = parse_single_substances(data, suma)
        if suma:
            return result[0], result[1], result[2]
        else:
            return result[0], result[1]
        
    
def parse_single_substances(data_lines, suma=False):
    '''
    parses transport data for classic task / only one substance
    '''
    elements = {}
    times = []
    elems_suma = {}
    readmode = 0
    curent_time = 0  
    
    for line in data_lines:
        line = line.strip()
        if line.startswith('$'):
            if line == '$ElementData':
                readmode = 1
                counter = 0
            else:
                readmode = 0
        elif readmode:
            if counter < 9: 
                counter += 1
            columns = line.split()
            if len(columns) > 1 and counter > 7:
                key = int(columns[0])
                val = float(columns[1])
                if val > 0:
                    if elements.has_key(key): 
                        elements[key][curent_time] = val
                        if suma:
                            elems_suma[key] += val
                    else: 
                        elements[key] = {curent_time:val}
                        if suma:
                            elems_suma[key] = val
                    
            elif len(columns) == 1 and counter == 4:
                curent_time = float(columns[0])
                times.append(curent_time)
                    
    if suma:
        return times, elements, elems_suma
    else:
        return times, elements  


def parse_multiple_substances(data_lines, suma=False):
    '''
    parses transport data for multiple substances task 
    at each simulation time there are @substances number of results
    '''
    all_subs = {}
    times = set()
    all_sumas = {}
    readmode = 0
    current_time = 0
    current_sub = ''  
    
    for line in data_lines:
        line = line.strip()
        if line.startswith('$'):
            if line == '$ElementData':
                readmode = 1
                counter = 0
            else:
                readmode = 0
        elif readmode:
            if counter < 9: 
                counter += 1
            columns = line.split()
            if len(columns) > 1 and counter > 7:
                key = int(columns[0])
                val = float(columns[1])
                if val > 0:
                    if all_subs[current_sub].has_key(key): 
                        all_subs[current_sub][key][current_time] = val
                        if suma:
                            all_sumas[current_sub][key] += val
                    else: 
                        all_subs[current_sub][key] = {current_time:val}
                        if suma:
                            all_sumas[current_sub][key] = val
                    
            elif len(columns) == 1 and counter == 4:
                #4th row after element is simulation time
                current_time = float(columns[0])
                times.add(current_time)
            
            elif len(columns) == 1 and counter == 2:
                #2nd row after element is substantion name
                current_sub = columns[0][1:-1]
                if current_sub not in all_subs:
                    all_subs[current_sub] = {}
                
                if suma and current_sub not in all_sumas:
                    all_sumas[current_sub] = {}
                        
                    
                
               
    times = sorted(times)                
    if suma:
        return times, all_subs, all_sumas
    else:
        return times, all_subs  
   

def parse_task_dirs(dirname, search_for='ini'):
    '''
    walk through dirname -r
    find file of search_for type file
    '''
    inifiles = []
    for root, dirs, files in os.walk(dirname):
        for fname in files:
            if fname.lower().endswith(search_for):
                inifiles.append('/'.join([root, fname]))
            elif fname == search_for:
                inifiles.append('/'.join([root, dirs, fname]))  
                
    return inifiles     
                       
def get_name_from_ini_file(ininame):
    '''
    Quick open inifile and find filename of solution
    '''
    try:
        file_handler = open(ininame,'r')
    except IOError:
        print 'failed to open %s' % ininame
    else:
        pars = INIConfig(file_handler)
        return pars['Transport']['Transport_out']

def create_ini_file_for_substance(ininame, substance):
    '''
    copy inifile to subfolder
    '''
    dir_name, file_name = os.path.split(ininame)
    dir_name = os.path.join(dir_name, substance)
    file_name = substance + '_' + file_name
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    new_file_name = os.path.join(dir_name, file_name)
    shutil.copy2(ininame, new_file_name)
    flow.change_paths_in_file(new_file_name, '..')    
        
            
def get_result_files(dirname, substances=False):
    '''
    Search dirname for solution files
    test if solution file exists
    '''
    res = []
    inifiles = parse_task_dirs(dirname)
    for inif in inifiles:
        dir_name, _fin = os.path.split(inif)
        res.append(dir_name + '/' + get_name_from_ini_file(inif))        
    if substances:
        return zip(inifiles, res)
    
    return res

def read_process_substances(source, fformat='json'):
    '''
    Read solution data from task dirs, remove zeros
    save non-zero concentration elements and times to pickle file
    '''
    for reseni in source:
        work_on_multiple_substances(reseni)
        

def read_process_all(source, fformat='json'):
    '''
    Read solution data from task dirs, remove zeros
    save non-zero concentration elements and times to pickle file
    '''
    for reseni in source:
        work_on_single_substance(reseni)

def work_on_multiple_substances(reseni):
    '''
    parse one transport file for data with multiple substances
    '''
    inifile = reseni[0]
    posfile = reseni[1]
    klic, _sou = os.path.split(posfile)
    times, elements, suma = read_transport(posfile, True, True)
    
    for subst in elements.keys():
        names = subst.split('_')
        sub_name = names[0]
        create_ini_file_for_substance(inifile, sub_name)
        
        fname = os.path.join(klic, sub_name, FNAME_ELEMS)
        save_vysledek(fname, elements[subst])
        
        fname = os.path.join(klic, sub_name, FNAME_SUMA)
        save_vysledek(fname, suma[subst])
        
        fname = os.path.join(klic, sub_name, FNAME_TIME)
        save_vysledek(fname, times)
        
        #multiple processing hack
        fname = os.path.join(klic, FNAME_ELEMS+'.json')
        with open(fname, 'w') as done_file:
            done_file.write('{"_comment" : "data are saved in nested substances subdirectories",\n"completed" : "true"}')
            
        
        print 'zpracovano %s' % klic       
        
def work_on_single_substance(reseni):
    '''
    parse one transport file, for data with only one substance
    '''
    jmena = os.path.split(reseni)
    klic = jmena[0]
    times, elements, suma = read_transport(reseni, True)
    fname = os.path.join(klic, FNAME_ELEMS)
    save_vysledek(fname, elements)
    
    fname = os.path.join(klic, FNAME_SUMA)
    save_vysledek(fname, suma)
    
    fname = os.path.join(klic, FNAME_TIME)
    save_vysledek(fname, times)
    return 'zpracovano %s' % klic        
        
def save_vysledek(filename, vysledek, fformat = 'json'):
    '''
    wrapper for file format
    save result vysledek to a filename, using file format
    @param: fformat - json, pickle
    '''
    if not filename.endswith(FNAME_EXT[fformat]):
        filename = filename + '.' + FNAME_EXT[fformat]
    globals()['__save_'+fformat](filename, vysledek)
        
def __save_json(filename, vysledek):
    '''
    save result vysledek to a filename, using JSON format
    '''
    import json
    try:
        fout = open(filename,'wb')
        fout.write(json.dumps(vysledek, fout))
        fout.close()
    except IOError:
        print "failed to write data in %s" % filename
        
def __save_pickle(filename, vysledek):
    '''
    save result vysledek to a filename, using pickle
    '''
    import cPickle
    try:
        fout = open(filename,'wb')
        cPickle.dump(vysledek, fout)
        fout.close()
    except IOError:
        print "failed to write data in %s" % filename
        
def load_vysledek(filename, fformat = 'json'):
    '''
    wrapper for file format
    load result vysledek from filename, using file format
    @param: fformat - json, pickle
    '''
    if not filename.endswith(FNAME_EXT[fformat]):
        filename = filename + '.' + FNAME_EXT[fformat]
    return globals()['__load_'+fformat](filename)                                        
        
def __load_pickle(filename):
    '''
    load result vysledek from a filename, using pickle
    :return: vysledek
    :rtype: dict
    '''
    import cPickle
    pars = open(filename, 'rb')
    vysledek = cPickle.load(pars)
    return vysledek
    
def __load_json(filename):
    '''
    load result vysledek from a filename, using json
    :return: vysledek
    :rtype: dict
    '''
    import json
    pars = open(filename, 'rb')
    vysledek = json.load(pars)
    return vysledek
        

def dict_to_csv(dct):
    '''
    converts dict to a csv 
    :param: dictionary of values
    :return: csv string
    '''
    rslt = ''
    for el_id, sol in dct.items():
        rslt += str(el_id)
        rslt += ';'
        for val in sol.values():
            rslt += str(val)
            rslt += ';'              
    
        rslt += '\n'
     
    return rslt

def __test_vysledek_save():
    '''
    testing func.
    '''
    pokus = '../../data/post/Sensitivity'
    rslts = get_result_files(pokus)
    read_process_all(rslts, 'json')
    
def __test_vysledek_load():
    '''
    testing func.
    '''
    inpt = '../../data/post/Sensitivity/001/elements_concentration'
    data = load_vysledek(inpt)
    print data
    print data['19506']
    
    
def main_multiprocess(dirname, substances=False):
    '''
    main loop for multiprocess run
    '''
    
    rslts = get_result_files(dirname, substances)
    nr_of_proc = cpu_count()
    
    # Create queues
    task_queue = Queue()
    done_queue = Queue()
    
    #populate queue with data
    for result in rslts:
        task_queue.put(result)
    
    #Start worker processes
    for i in range(nr_of_proc):
        Process(target=worker, args=(task_queue, done_queue, substances)).start()
    
    # Get and print results
    sumtime = 0
    print 'Unordered results:'
    for i in range(len(rslts)):
        rtime = done_queue.get()
        print '\t', rtime
        sumtime += rtime        
    
    # Tell child processes to stop
    for i in range(nr_of_proc):
        task_queue.put('STOP')
        print "Stopping Process #%s" % i      
    
    print 'Total runtime %s sec' % sumtime 

def usage():
    '''
    shows help
    '''
    print 'Tool for flow123d transport_out data compression.'
    print 'Recursively search given directory for files, and write output in json format'
    print 'usage: transport -s dirname for single process, with single substance'
    print 'usage: transport -u dirname for single process, with multiple substances'
    print 'usage: transport -m dirname for multiprocess (multicore CPU is a big advantage for this)'
    print 'usage: transport -c dirname for multiprocess with multiple substances'
    
def main():
    '''
    getopt main procedure
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:m:h:u:c:", ["single=", "multi=", "help", "msubst=", "subpro="])
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
        elif opt in ("-s", "--single"):
            rslts = get_result_files(arg)
            read_process_all(rslts, 'json')
        elif opt in ("-u", "--msubst"):
            rslts = get_result_files(arg, True)
            read_process_substances(rslts, 'json')    
        elif opt in ("-m", "--multi"):
            main_multiprocess(arg)
        elif opt in ("-c", "--subpro"):
            main_multiprocess(arg, True)          
        else:
            usage()
            sys.exit()

if __name__ == "__main__":
    main()
    
    
    
      
        
        
    
    