
import thread

L=thread.allocate_lock ()

LOOPS=10000
LOOPS=30
NTH = 38
NTH=4
CTH = NTH

def foo(d):
    for i in xrange (LOOPS):
	print d, i
    global CTH
    CTH = CTH - 1
    if CTH <= 0:
        L.release ()

def bar ():
    L.acquire()
    for i in range (CTH):
	thread.start_new_thread (foo, (i,))
    L.acquire()
    print 'Everybody happy?'

bar ()
