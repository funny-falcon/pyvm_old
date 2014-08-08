#
# higher level functionality over _JIT module
#
# 1) provides abstraction for compiling shared libs
# 2) uses the convention for cached .dll
# 3) provides some essential CJITed functions for interaction with C libs
# 4) generally other useful stuff for when wrapping libraries
#
# TODO1: use disutils to use the compiler portably
# TODO2: refactor to use pelf properly
#
import _JIT
import os
import md5
from binascii import hexlify
from _JIT     import CStringToPyString, Memcpy, MemcpyInts, StructMember

def DoubleIndirection (i):
	return StructMember (StructMember (i, 0), 0)

CC = 'gcc'
SOPATH = './'

Callback = _JIT.Callback
dllopen = _JIT.dllopen

class DLLError:
	def __init__ (self, reason):
		self.reason = reason
	def __repr__ (self):
		return self.reason
	def __str__ (self):
		return self.reason

def c_compile (infile, outfile, options=None, dll=False):
	if options is None:
		options = []
	if dll:
		options += ['-fpic', '-shared']
		if '-c' in options:
			options.remove ('-c')
	else:
		if '-c' not in options:
			options.append ('-c')
	cmd = ' '.join ([CC, ' '.join (options), infile, '-o', outfile])
	print "RUNNING:", cmd
	if os.system (cmd):
		raise DLLError (cmd)

libno = 0

def CJIT (PROGRAM, options=None, dll=True):
	"""Compile PROGRAM and return a dynamically linked library. The file of the library
	will be removed when the library is freed"""
	global libno
	cname = '_dlltmp.c'
	file (cname, 'w').write (PROGRAM)
	libname = SOPATH + '_dlltmplib%i.so' % libno
	libno += 1
	c_compile (cname, libname, options, dll=1)
	lib = _JIT.dllopen (libname)
	os.unlink (libname)
	os.unlink (cname)
	return lib

def CachedLib (name, PROGRAM, options=None, force=False, dll=True):
	H = md5.new ()
	H.update (PROGRAM)
	PATH = sys.PYVM_HOME + 'Public/so'
	if dll: ext = '.so'
	else: ext = '.o'
	fnm = PATH + '/' + name + '.' + hexlify (H.digest ()) + ext
	if os.access (fnm, os.R_OK) or force:
		##print "CACHED", fnm
		if dll:
			return _JIT.dllopen (fnm)
		return pelfopen (fnm)
	cname = PATH + '/_dlltmp.c'
	file (cname, 'w').write (PROGRAM)
	c_compile (cname, fnm, options, dll=dll)
	os.unlink (cname)
	if dll:
		return _JIT.dllopen (fnm)

	return pelfopen (fnm)

def pelfopen (fnm):
	# This is here so pelf is not required by the bootstrap 
	import pelf
	return pelf.dllopen (fnm)

#
# default argument wrapper. Not strictly related to DLL but usefull when 
# wrapping libraries like gtk
#
def dfl_wrapper (func, argnames, defaults):
	"""dflt_wrapper (func, argnames, defaults) --> callable
	Create a callable with arguments specified in the 'argnames' string and default
	values in the 'defaults' tuple that will call the callable 'func'. Example:
		def foo (a, b, c):
			print a, b, c
		foo2 = dfl_wrapper (foo, "x y z", (2, 3))
		foo2 (x=1)
	"""
	class Unbound:
		pass
	argnames = argnames.split (' ')
	x = {}
	for i, j in zip (argnames [-len (defaults):], defaults):
		x [i] = j
	defaults = x
	argcount = len (argnames)
	def call_func (*args, **kwargs):
		if len (args) > argcount:
			raise TypeError ("Too many arguments to %s" %func.func_name)
		arglist = list (args) + [Unbound] * (argcount - len (args))
		if kwargs:
			for i, j in kwargs.iteritems ():
				try:
					idx = argnames.index (i) 
				except IndexError:
					raise TypeError ("%s() for unexpected keyword argument %s"
							 %(func.func_nme, i))
				if arglist [idx] is not Unbound:
					raise TypeError ("%s() got multiple values for %s"
							 %(func.func_name, i))
				arglist [idx] = j
		if Unbound in arglist:
			for i, j in enumerate (arglist):
				if j is Unbound:
					try:
						arglist [i] = defaults [argnames [i]]
					except KeyError:
						raise TypeError ("%s() No value for %s"
								 %(func.func_name, argnames [i]))
		return func (*arglist)
	return call_func
