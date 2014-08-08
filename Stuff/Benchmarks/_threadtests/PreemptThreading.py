#
# This here checks some very complex stuff which has to do with threads
# and preemptions and sched_yielding and blocking in preemption
#
#
#
#
#
import thread
import time

LOCK = thread.allocate_lock ()
DO = 0

def forevah ():
    while 1:
	for i in xrange(2000000):
	    pass
	print "Hi!"
	if DO:
	    LOCK.acquire ()
	    print "Hi! (TADAAAN)"
	    for i in xrange(2000000):
	        pass
	    print "Hi!"
	    LOCK.release ()
	    while 1:
		for i in xrange(2000000):
		    pass
		print "Hi!"


thread.start_new_thread (forevah, ())

class A:
    def __eq__ (self, x):
	if not DO:
		print "INSIDE PREEMPTION, NOT SUPPOSED TO SEE ANY OTHER THREAD"
		print
		for i in xrange (10000000):
		    pass
		print "LEAVING PREEMPTION"
		return 0
	else:
		print "WILL RELEASE THE LOCK, BUT YOU WON'T SEE 'Hi!'"
		print
		LOCK.release ()
		for i in xrange (30000000):
		    pass
		print "WILL ACQUIRE THE LOCK IN PREEMPTION!!!!"
		LOCK.acquire ()
		print "RETURN"

#time.sleep (2)
a=A()
for i in xrange (10000000):
    pass
print "DONE DELAY"

a==1
for i in xrange (1000000):
    pass

#0000000000000000000000000000000000000000000000000000000000000000

print 50*'-'
print "NOW WILL DO THE TRICKY THING"
LOCK.acquire ()
DO = 1
time.sleep (1)
for j in (1,2, 3, 4, 5):
    print "Secondary thread frozen?"
    for i in xrange (3000000):
        pass
a==1
for i in xrange (10000000):
    pass


