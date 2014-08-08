#
# poll sleeping. interesting if you can interpret the output.
#
#
import threading
from time import sleep

NN = 20

def work ():
	while 1:
		pass


def foo(x, n):
	sleep (x)
	print n, "awaken"
	sleep (x)
	print n, "awaken"
	sleep (100)
for i in xrange (NN):
	threading.Thread (None, foo, None, (2.0+(i/80.0),'one%i'%i)).start ()
sleep (4)
threading.Thread (None, work, None, ()).start ()
threading.Thread (None, work, None, ()).start ()
sleep (4)
try:
	import pyvm_extra
	pyvm_extra.thread_status ()
except:
	pass
raise SystemExit
