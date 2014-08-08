#
#
# Big complex TCP/IP server on 127.0.0.1
#
#
#
import sys
import socket
import threading
import random
from time import sleep



RUNNING = True

try:
	from pyvm_extra import thread_status
	def foo ():
		while RUNNING:
			print "HI"
			sleep (6)
			print "HERE"
			thread_status ()
		###	import gc
		###	gc.collect ()
	XXX = threading.Thread (None, foo, None, ())
	XXX.start ()
except:
	pass

PORT = 50000 + random.randint (1, 700)
print "Will use 127.0.0.1:%i" %PORT
OK = False

def server (PORT):
	try:
		s=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
		print "BIND:", s.bind (('127.0.0.1', PORT))
		print "LISTEN:", s.listen (5)
		print "NAME:", s.getsockname()
		global OK
		OK = True
	finally:
		L.release ()
	while True:
	#	print 'wait on accept...'
		conn, addr = s.accept ()
	#	print 'ok ok accept...'
		data = conn.recv (1024)
	#	print 'data=[%s]'% data
		conn.send (data)
		conn.close ()
	#	print data
		if data [:3] == 'END':
			break

ITER = 100

class CLIENT (threading.Thread):
	def run (self):
		print "START CLIENT", self.getName()
		for i in xrange (ITER):
	#		print i
			s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
			s.connect (('127.0.0.1', PORT))
			s.send ('Hello world!')
			data = s.recv (1000)
			for j in xrange (6000):
				pass
			if random.randint (1, 100) < 10:
				sleep (0.01)

	#		print 'recv [%s]'% data
			s.close ()
		print "END CLIENT", self.getName ()

N=185
L = threading.Lock()
L.acquire ()
T = threading.Thread (None, server, None, (PORT,))
T.start ()
L.acquire ()
if not OK:
	print "Experiment failed"
	raise SystemExit
print "ok, go on"
clients =  [ CLIENT () for i in range (N)]
for i in clients:
	i.start ()
for i in clients:
	i.join ()
print "HERE I AM"
s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
s.connect (('127.0.0.1', PORT))
s.send ('END')
s.close ()
print "END OF ALL"
RUNNING = False
