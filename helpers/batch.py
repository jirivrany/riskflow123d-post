'''
Created on 9.10.2012

@author: albert
'''
import os.path
import sys.platform

SEPARATOR = '/'

SUBMIT_ALL = 'submit_all.sh'
COMPRESS = 'compress.sh'
CLEAN_LOGS = 'clean_logs.sh'
CLUSTER = 'cluster.sh'
DEFAULT_LAUNCHER = '/share/apps/flow123d/bin/flow123d'


def create_cluster_batch(adr):
    '''wrap up - calls all file creators'''    
    create_cluster_submit_all(adr)
    create_cluster_clean(adr)
    create_cluster_compress(adr)
        
    

def create_cluster_launcher(inifile, launcher = None):
    '''creates a sh for cluster / hydra by default''' 
    if not launcher:
        launcher = DEFAULT_LAUNCHER
    
    adr, inifname  = os.path.split(inifile)
    file_name = adr + SEPARATOR + CLUSTER
    launcher_file = open(file_name, 'w')
    print >> launcher_file, '#!/bin/bash'
    print >> launcher_file, '#$ -cwd'
    print >> launcher_file, '#$ -j y'
    print >> launcher_file, '#$ -S /bin/bash'
    print >> launcher_file, '{} -S {}'.format(launcher, inifname)
    launcher_file.close()

def create_local_launcher(inifile, flow_exec):
    '''creates a batch file for windows
    '''
    adr, inifname = os.path.split(inifile)
    
    if sys.platform.find('win') > -1:
        file_name = adr + SEPARATOR + 'run.bat'
    else:
        file_name = adr + SEPARATOR + 'run.sh'    
    
    launcher_file = open(file_name, 'w')
    print >> launcher_file, '{} -S {}'.format(flow_exec, inifname)
    launcher_file.close()

def create_cluster_submit_all(adr):
    '''creates submit all batch'''
    file_name = adr + SEPARATOR + SUBMIT_ALL
    batch_file = open(file_name, 'w')
    print >> batch_file, cluster_launcher_batch('cluster.sh')
    batch_file.close()    
        
def create_cluster_compress(adr):
    '''
    creates compress shell file
    '''
    file_name = adr + SEPARATOR + COMPRESS
    compress_file = open(file_name, 'w')
    print >> compress_file, cluster_compress()
    compress_file.close()
    
def create_cluster_clean(adr):
    '''
    creates cleanup shell file
    '''
    file_name = adr + SEPARATOR + CLEAN_LOGS
    cluster_clean = open(file_name, 'w')
    print >> cluster_clean, cluster_cleanup()
    cluster_clean.close()     


def cluster_launcher_batch(fname):
    '''
    creates launcher batch for Cluster
    '''
    text = '''#!/bin/bash
#
# search for batchfile name
'''
    text += 'BF={}'.format(fname)
    text += '''
# QSUB
# -j y
# -cwd
# -b y
# -S /bin/bash

for file in *; do
    if [ -d "$file" ]; then

        echo "Submit: $file/$BF"
        # uloz si aktualni pracovni adresar
        wd=`pwd`
        
        
        cd $file
        qsub -j y -cwd -S /bin/bash $BF
        
        #vrat se zpet
        cd $wd
      fi
done
'''
    return text


def cluster_cleanup():
    '''
    creates launcher for cleanup of data on Cluster
    '''
    text = '''#!/bin/bash
#clean flow logs
/share/apps/tools/clean_flow_logs/clean_logs.py -d $PWD'''
    return text

def cluster_compress():
    '''
    creates launcher for compress  of data on Cluster
    '''
    text = '''#!/bin/bash
#submit compress script to qsub
qsub -j y -cwd -S /bin/bash /share/apps/tools/transport/compress.qsub'''
    return text

if __name__ == '__main__':
    import doctest
    doctest.testmod()
