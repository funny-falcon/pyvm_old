#
# For pyvm. We start threads, some are RUNNING, some are BLOCKING
# and some are SOFTBLOCKING (all possible combinations)
#
# Then we call pyvm_extra.thread_status () to see that
#
#
#
#
import thread
import gc
from time import sleep 

def foo ():
	while 1:
		pass
	print "RET"

def bar ():
	raw_input ()
	print "RET"

def zoo ():
	sleep (10000)

def pak ():
	while 1:
		sleep (1)
		for i in xrange (1000):
			pass
		gc.collect ()

print "STARTAD:", thread.start_new_thread (foo, ())
for i in xrange (10000):
	pass
thread.start_new_thread (bar, ())
thread.start_new_thread (zoo, ())
thread.start_new_thread (foo, ())
thread.start_new_thread (pak, ())
thread.start_new_thread (pak, ())
import pyvm_extra
pyvm_extra.thread_status ()
sleep (1)
print 30*'-'
pyvm_extra.thread_status ()
sleep (1)
print 30*'-'
pyvm_extra.thread_status ()
sleep (1)
print 30*'-'
pyvm_extra.thread_status ()
sleep (1)
print 30*'-'
pyvm_extra.thread_status ()
sleep (1)
print 30*'-'
pyvm_extra.thread_status ()
#import os
#os.system ('ps -eLF')
#sleep (200)
