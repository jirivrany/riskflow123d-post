#!/usr/bin/env python
'''
A module for handling flow123d transport output

'''
import Queue
import threading
from iniparse import INIConfig
import os
import time
import transport

queue = Queue.Queue()

class ThreadReader(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            #grabs host from queue
            reseni = self.queue.get()
            
            klic, soubor = os.path.split(reseni)
            del(soubor)
            times, elements = transport.read_transport(reseni)
            fname = klic + 'elements_concentration.pck'
            transport.save_vysledek(fname, elements)
            fname = klic + 'times.pck'
            transport.save_vysledek(fname, times)
            print 'zpracovano {}'.format(klic)
            
            #signals to queue job is done
            self.queue.task_done()

        
def test_vysledek_save():
    '''
    testing func.
    '''
    
    pokus = '../../data/post/Monte2'
    rslts = transport.get_result_files(pokus)
    #spawn a pool of threads, and pass them queue instance 
    for i in range(5):
        t = ThreadReader(queue)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for result in rslts:
        queue.put(result)
    
    #wait on the queue until everything has been processed
    queue.join()
    
       
    
if __name__ == '__main__':
    #test_vysledek_load()
    start = time.time()
    test_vysledek_save()
    print "Elapsed Time: %s" % (time.time() - start)
    
    
      
        
        
    
    