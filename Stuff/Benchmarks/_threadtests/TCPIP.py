#
# ps -eLf
#
import random
import threading
import SocketServer
import socket
from time import sleep 
import sys

class MyServer(SocketServer.ThreadingTCPServer):
	allow_reuse_addr = 1

	def serve_forever (self):
		while RUNNING:
			self.handle_request ()

RUNNING = True

class MyHandler(SocketServer.StreamRequestHandler):

	def handle (self):
		while 1:
			x= self.rfile.readline ()
			if not x:
				break
			self.wfile.write (x.upper ())

def server():
	print "PORT=", port
	MyServer (('', port), MyHandler).serve_forever ()

port = random.randint (9000, 49500)
threading.Thread (None, server, None, ()).start ()
sleep (1)
N=100
SS=10
CL=100

def client (nn):
	for i in xrange (N):
		s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
		s.connect (('127.0.0.1', port))
		for j in xrange (SS):
			s.send ("hello\n")
			sleep (0.002)
			data = s.recv (1024)
		s.close ()
		sleep (0.02)
	print 'END', nn
	global CL
	CL -= 1

for i in xrange (CL):
	threading.Thread (None, client, None, (i,)).start ()

while CL:
	sleep (1)

RUNNING = False
s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
s.connect (('127.0.0.1', port))
s.send ("SHUTDOWN\n")
s.recv (100)
s.close ()
