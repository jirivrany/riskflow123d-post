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

FNAME_TIME = 'times'
FNAME_ELEMS = 'elements_concentration'
FNAME_SUMA = 'conc_suma'
FNAME_EXT = {'json':'json', 'pickle':'pck'}

def worker(input_queue, done_queue):
    '''
    Worker process - takes data from input, saves results to disk
    and puts time of computation to output
    
    :param: input_queue / multiprocessing Queue
    :param: output_queue / multiprocessing Queue
    '''
    for reseni in iter(input_queue.get, 'STOP'):
        start_time = time.time() 
        #grabs host from queue
        klic, soubor = os.path.split(reseni)
        del(soubor)
        times, elements, suma = read_transport(reseni, True)
        fname = klic + '/' + FNAME_ELEMS
        save_vysledek(fname, elements)
        fname = klic + '/' + FNAME_TIME
        save_vysledek(fname, times)
        fname = klic + '/' + FNAME_SUMA
        save_vysledek(fname, suma)
        
        done_queue.put(time.time() - start_time)

        
def read_transport(fname, suma=False):
    """
    Read a Flow .pos file.
    @param: suma - set True if sum of concentration has to be computed too
    """
    elements = {}
    times = []
    elems_suma = {}
    readmode = 0
    curent_time = 0
    try:
        mshfile = open(fname, "r")
    except IOError:
        print 'Error - failed to open file %s ' % fname
    else:        
        for line in mshfile:
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

   

def parse_task_dirs(dirname, search_for='ini'):
    '''
    walk through dirname -r
    find file of search_for type file'''
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

        
def get_result_files(dirname):
    '''
    Search dirname for solution files
    test if solution file exists
    '''
    res = []
    for inif in parse_task_dirs(dirname):
        dirname, finame = os.path.split(inif)
        del(finame)
        res.append(dirname + '/' + get_name_from_ini_file(inif))        
    return res

def read_process_all(source, fformat='json'):
    '''
    Read solution data from task dirs, remove zeros
    save non-zero concentration elements and times to pickle file
    '''
    for reseni in source:
        klic, soubor = os.path.split(reseni)
        del(soubor)
        times, elements, suma = read_transport(reseni, True)
        fname = klic + '/' + FNAME_ELEMS
        save_vysledek(fname, elements, fformat)
        
        fname = klic + '/' + FNAME_SUMA
        save_vysledek(fname, suma, fformat)
        
        fname = klic  + '/' + FNAME_TIME
        save_vysledek(fname, times, fformat)
        print 'zpracovano %s' % klic
        
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
    
    
def main_multiprocess(dirname):
    '''
    main loop for multiprocess run
    '''
    
    rslts = get_result_files(dirname)
    nr_of_proc = cpu_count()
    
    # Create queues
    task_queue = Queue()
    done_queue = Queue()
    
    #populate queue with data
    for result in rslts:
        task_queue.put(result)
    
    #Start worker processes
    for i in range(nr_of_proc):
        Process(target=worker, args=(task_queue, done_queue)).start()
    
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
    print 'usage: transport -d dirname for single process'
    print 'usage: transport -m dirname for multiprocess (multicore CPU is a big advantage for this)'
    
def main():
    '''
    getopt main procedure
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:m:h", ["dir=", "multi=", "help"])
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
            rslts = get_result_files(arg)
            read_process_all(rslts, 'json')
        elif opt in ("-m", "--multi"):
            main_multiprocess(arg)    
        else:
            usage()
            sys.exit()

if __name__ == "__main__":
    main()
    
    
    
      
        
        
    
    