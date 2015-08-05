################################
# Author   : septicmk
# Date     : 2015/07/24 16:57:30
# FileName : tool.py
################################

import numpy as np
import os,sys

def exeTime(func):
    '''
    Usage:
     - just put '@exeTime'(with out quotation) before your function
     - will show the running time
    '''
    import time
    def wraper(*args, **args2):
        s = time.time()
        ret = func(*args, **args2)
        e = time.time()
        msg = "%3.3fs taken for {%s}" % (e-s, func.__name__)
        log('time')(msg)
        return ret
    return wraper

def showsize(obj, name = ''):
    '''
    Usage:
     - show the size of a object
     - e.g. showsize(img_stack, '1-L-Red.tif')
    Args:
     - obj: a variable
     - name: the name you want to print
    '''
    sz = sys.getsizeof(obj)
    if type(obj) is np.ndarray:
        sz = obj.nbytes + .0
    if sz < 1024.0:
        print "%s %.2f B" % (name ,sz)
    elif sz < 1024*1024:
        print "%s %.2f K" % (name, sz/(1024.0))
    elif sz < 1024*1024*1024:
        print "%s %.2f M" % (name, sz/(1024.0*1024.0))
    else:
        print "%s %.2f G" % (name, sz/(1024.0*1024.0*1024.0))
    
    
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[33m'
    PUP = '\033[35m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    dic = { 'warn' : WARNING,
            'info'  : '',
            'error' : FAIL,
            'endc' : ENDC,
            'time' : OKGREEN,
            'debug' : PUP
        }
    @staticmethod
    def decode(level):
        return bcolors.dic.get(level,'')
    
def bar(level):
    '''
    Usage:
     - this will show a progress bar
     - e.g. bar('info')(msg, i, 100)
    '''
    loglevel=['info','error','time','debug','warn']
    if level in loglevel:
        def wraper(msg, i, end):
            if i <= end:
                sys.stdout.write('[' + bcolors.decode(level) + level + bcolors.decode('endc') + '] ('+ str(i)+'/' + str(end) + ') '+ msg + '\r')
                sys.stdout.flush()
            if i == end:
                print
        return wraper
    else:
        def wraper(msg, i, end):
            pass
        return wraper

def log(level):
    '''
    Usage:
     - this will just show info
     - e.g. log('info')(msg)
    '''
    loglevel=['info','error','time','debug','warn']
    if level in loglevel:
        def wraper(msg):
            print '[' + bcolors.decode(level) + level + bcolors.decode('endc') + '] '+ msg
        return wraper
    else:
        def wraper(msg):
            pass
        return wraper

if __name__ == '__main__':
    pass
    
