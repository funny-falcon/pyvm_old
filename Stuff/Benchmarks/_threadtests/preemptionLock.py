#
#
# Locks in preemption shouldn't block the vm
#
#
import threading
import time

class A:
    def __cmp__ (self, other):
	print "there"
	L1.release ()
	L2.acquire ()
	print "O.K."
	return 1

def f1():
	print "here"
	L1.acquire ()
	print "normal vm goes on ..."
	time.sleep (2)
	L2.release ()
	time.sleep (2)

def f2 (*args):
    a = A()
    a == 2

L1 = threading.Lock ()
L2 = threading.Lock ()
print 1
L1.acquire ()
print 2
L2.acquire ()
threading.Thread (None, f2, None, ()).start ()
f1()
