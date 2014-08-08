import _socket
from array import array
from _JIT import fptr_wrapper

for i, j in _socket.__dict__.iteritems ():
	if i == i.upper ():
		globals()[i] = j

#
# This module is done with a different way to provide builtins:
# instead of implementing these as python callables in C, we just
# pass pointers to functions and wrap them with the DLL module
# With the other approach, the calls are a little bit faster, but
# this way the executable of pyvm is smaller. This is an experiment.
#
# This is 'the middle way'. 
#	1. all in pyvm as python callables. Like module binascii
#	2. pyvm exports pointers to functions. Like this one
#	3. nothing in pyvm. Use DLL module only. Like zlib and Tkinter
#
# we could use '3' but that doesn't get along very well with structures
# and portability.
# 
socket_call = fptr_wrapper ('i', _socket.socket, 'iii')
bind_af_inet_call = fptr_wrapper ('i', _socket.bind_af_inet, 'iii')
listen_call = fptr_wrapper ('i', _socket.listen, 'ii')
send_call = fptr_wrapper ('i', _socket.send, 'isii', True)
close_call = fptr_wrapper ('', _socket.close, 'i', True)
setsockopt_call = fptr_wrapper ('', _socket.setsockopt, 'iiii')
getsockname_af_inet = fptr_wrapper ('', _socket.getsockname_af_inet, 'ip32')
sendall_call = fptr_wrapper ('i', _socket.sendall, 'isii')

inet_addr = fptr_wrapper ('i', _socket.inet_addr, 's')
recv = _socket.recv
gethostname = _socket.gethostname
accept_af_inet = _socket.accept_af_inet
connect_af_inet_call = _socket.connect_af_inet
inet_ntoa = fptr_wrapper ('s', _socket.inet_ntoa, 'i')

class error(Exception):
	def __init__ (self, msg=None):
		print "SOCKET ERROR:", msg
		whereami ()

class Timeout(Exception):
	pass

class socket:
	def __init__ (self, family=AF_INET, type=SOCK_STREAM, proto=0, fd = -1):
		self._timeout_ = -1
		self.family = family
		self.type = type
		self.proto = proto
		if fd == -1:
			fd = socket_call (family, type, proto)
		if fd == -1:
			raise error
		self.fd = fd
	def bind (self, addr):
		r = self.bind_or_connect (addr, bind_af_inet_call)
		if r == -1:
			raise error ("Address already in use")
		return r
	def connect (self, addr):
		if self.bind_or_connect (addr, connect_af_inet_call) == -1:
			raise error ("Connection refused")
	def bind_or_connect (self, addr, af_inet):
		if self.family == AF_INET:
			addr, port = addr
			if type (addr) is str:
				addr = addr or '0.0.0.0'
				addr = inet_addr (addr)
			return af_inet (self.fd, addr, port)
		raise error
	def listen (self, n=1):
		return listen_call (self.fd, n)
	def accept (self):
		if self.family == AF_INET:
			fd, host, port = accept_af_inet (self.fd)
			if fd == -1:
				raise error ("accept returned -1")
			return socket (AF_INET, self.type, self.proto, fd), (inet_ntoa (host), port)
		raise error
	def recv (self, buflen, flags=0):
		data = recv (self.fd, buflen, flags, self._timeout_)
		if data == -2:
			raise Timeout
		return data
	def send (self, data, flags=0):
		return send_call (self.fd, data, len (data), flags)
	def close (self):
		if self.fd != -1:
			close_call (self.fd)
			self.fd = -1
	def setsockopt (self, level, optname, value):
		setsockopt_call (self.fd, level, optname, value)
	def getsockname (self):
		v = array ('i', (0,0))
		getsockname_af_inet (self.fd, v)
		return inet_ntoa (v[0]), v[1]
	def sendall (self, data, flags=0):
		if not sendall_call (self.fd, data, len (data), flags):
			raise error
	def makefile (self, mode, bufsize):
		return fileobj (self, mode, bufsize)
	def settimeout (self, val):
		self._timeout_ = val
	def __del__ (self):
		self.close ()

del _socket, fptr_wrapper

class fileobj:
	def __init__ (self, sock, mode, bufsize=8192):
		self.sock = sock
		if bufsize < 0:
			bufsize = 8192
		self.maxlinelen = 2 * bufsize
		self.bufsize = bufsize
		self.mode = mode
		if 'w' in mode:
			self.wbuf = []
			self.wlen = 0
		if 'r' in mode:
			self.rbuf = ''
	def write (self, s):
		self.wbuf.append (s)
		self.wlen += len (s)
		if self.wlen > self.bufsize:
			self.flush ()
	def flush (self):
		try:
			if self.wbuf:
				self.sock.sendall (''.join (self.wbuf))
				self.wbuf = []
		except:
			pass
	def close (self):
		self.flush ()
		self.sock = None
	closed = property (lambda self: self.sock is None)
	def readline (self):
		while '\n' not in self.rbuf:
			data = self.sock.recv (self.bufsize)
			if not data:
				data = self.rbuf
				self.rbuf = ''
				return data
			self.rbuf += data
			if len (self.rbuf) > self.maxlinelen:
				raise ValueError, "pyvm/Lib/socket.py: line too long"
		i = self.rbuf.find ('\n')+1
		data = self.rbuf [:i]
		self.rbuf = self.rbuf [i:]
		return data
	def read (self, size=-1):
		if size <= 0:
			buffers = [self.rbuf]
			while 1:
				data = self.sock.recv (self.bufsize)
				if data:
					buffers.append (data)
				else:
					break
			self.rbuf = []
			return ''.join (buffers)
		if size <= len (self.rbuf):
			data = self.rbuf [:size]
			self.rbuf = self.rbuf [size:]
			return data
		buf = self.rbuf
		rbuf = []
		buffers = [buf]
		l = len (buf)
		while l < size:
			data = self.sock.recv (size - l)
			if not data:
				break
			buffers.append (data)
			l += len (data)
		return ''.join (buffers)
	def __iter__ (self):
		while True:
			l = self.readline ()
			if not l:
				return
			yield l
		
# This is from Python/Lib/socket.py

def getfqdn(name=''):
	name = name.strip()
	if not name or name == '0.0.0.0':
		name = gethostname()
	try:
		hostname, aliases, ipaddrs = gethostbyaddr(name)
	except:
		pass
	else:
		aliases.insert(0, hostname)
		for name in aliases:
			if '.' in name:
				break
		else:
			name = hostname
	return name
