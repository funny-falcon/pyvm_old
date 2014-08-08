#
# This tests threading & blocking DLL libraries & callbacks
#
#
#
#
import os
import _JIT as DLL
import thread
import time

PROGRAM = r"""
	#include <stdio.h>
	void sleepus ()
	{
		sleep (1);
	}
	void sleepus2 (void (*f)())
	{
		sleep (1);
		f ();
		sleep (1);
	}
"""

LibNo = xrange (1000000).next

def MakeLib (PROGRAM):
    file ('tmpfile.c', 'w+').write (PROGRAM)
    libno = LibNo ()
    os.system ('gcc -fpic -O3 -shared tmpfile.c -o mylib%i.so' % libno)
    mylib = DLL.dllopen ('./mylib%i.so' %libno)
    os.unlink ('./mylib%i.so'%libno)
    return mylib

mylib = MakeLib (PROGRAM)
sleepus = mylib.get (('', 'sleepus', ''), True)

def forevah ():
    while 1:
	for i in xrange(2000000):
	    pass
	print "Hi!"

thread.start_new_thread (forevah, ())
for i in xrange (200000):
	pass
time.sleep (1)
print "SLEEP SOME MORE"
time.sleep (1)
print "WILL CALL SLEEPUS"
sleepus ()
print "OKIE DOKIE"


print '--=------------ the big test--------------'

cb = DLL.Callback (('', ''))
def callbackFunc ():
    print "I awoke"
cb.set_callback (callbackFunc)
sleepus2 = mylib.get (('', 'sleepus2', 'i'))
#sleepus2 = mylib.get (('', 'sleepus2', 'i'), True)
sleepus2 (cb.fptr ())

print "WAZOO"
