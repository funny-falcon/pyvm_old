#
#
#
# Simple threads & blocking in preemption
#
#
#
import thread
import time

class A:
    def __cmp__ (self, other):
	print "LOLO"
	time.sleep (4)
	print "LALA"
	return 0

def f1():
    for i in xrange (20):
	time.sleep (1)
	print "f1!"

def f2 (*args):
    a = A()
    a == 2

thread.start_new_thread (f2, ())
f1()
