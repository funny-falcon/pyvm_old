
from os import system, listdir
from time import time
from sys import stdout


def vsystem (cmd):
#    print "Running: %s" %cmd
    system (cmd)

def forfile (ext, dir='.', skip=()):
    for i in listdir (dir):
	if i.endswith (ext) and i not in skip:
	    yield i

def progress (itr):
    t0 = time()
    for i in itr:
        stdout.write ('.')
        stdout.flush ()
	yield i
    stdout.write ('[%.2f]\n' %(time()-t0))

