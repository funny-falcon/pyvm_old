#
#
#
# Simple threads & blocking in preemption
#
#
#
import thread
import time

def dela ():
	for x in xrange (100000):
		pass

class A:
    def __cmp__ (self, other):
	print "CMPING"
	print "LOLO"
	f1 ('x****')
	print "LALA"
	return 0

def f1(x):
    for i in xrange (200):
	dela ()
	print x

def f2 (*args):
    a = A()
    a == 2

thread.start_new_thread (f2, ())
thread.start_new_thread (f1, ('-',))
thread.start_new_thread (f1, ('- -',))
f1('o')
