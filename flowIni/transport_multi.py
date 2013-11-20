#!/usr/bin/env python
'''
A module for handling flow123d transport output

'''
from multiprocessing import Process, Queue, cpu_count
import os
import time
import transport


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
        times, elements = transport.read_transport(reseni)
        fname = klic + '/elements_concentration.pck'
        transport.save_vysledek(fname, elements)
        fname = klic + '/times.pck'
        transport.save_vysledek(fname, times)
        done_queue.put('zpracovano {} za {}'.format(klic, time.time() - start_time))
        
        
def main():
    '''
    testing func.
    '''
    
    pokus = '../../data/post/Monte2'
    rslts = transport.get_result_files(pokus)
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
    print 'Unordered results:'
    for i in range(len(rslts)):
        print '\t', done_queue.get()       
    
    # Tell child processes to stop
    for i in range(nr_of_proc):
        task_queue.put('STOP')
        print "Stopping Process #%s" % i     
    
if __name__ == '__main__':
    #test_vysledek_load()
    STARTED = time.time()
    main()
    print "Elapsed Time: %s" % (time.time() - STARTED)
    
    
      
        
        
    
    