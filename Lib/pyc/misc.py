import sys
import itertools
from gco import GCO

#
# 2.3 compat
#

def reversed (x):
	x = list (x)
	x.reverse ()
	for i in x:
		yield i

def sorted (x):
	x = list (x)
	x.sort ()
	return x

# print successful optimizations

def opt_progress(x):
	if GCO ['showmarks']:
		if x[0] != '>':
			print x,

# needed by something

def flatten(tup):
	elts = []
	for elt in tup:
		if type(elt) is tuple:
			elts = elts + flatten(elt)
		else:
			elts.append(elt)
	return elts

#
# python's array ('c') is rather broken because it
# cannot be initialized from a list of integers (even if
# those integers are in the proper range)
# pyvm can. And that is an important speed-up.
#

if sys.copyright.startswith ('pyvm'):
	from array import array
	def list_to_string (lst):
		return array ('c', lst).tostring ()
else:
	def list_to_string (lst):
		return ''.join (map (chr, lst))
    
#
# NullIterator
#

def make_null_iter ():
	nulliter = iter (())
	return lambda self: nulliter

NullIter = make_null_iter ()

#
# counter
#

def counter ():
	return itertools.count ().next
	return xrange (1000000).next

#
# Load constants-file
#

def import_constants (fnm):
	# build the CONSTANTS dictionary from the file's __all__
	# for all things that are marshalable
	D = {}
	if fnm.endswith ('.py'):
		fnm = fnm [:-3]
	try:
		mod = __import__ (fnm)
	except ImportError:
		print "Cannot load constants from %s"%fnm
		raise SystemExit (1)
	try:
		all = mod.__all__
	except:
		all = mod.__dict__.keys ()
	for i in all:
		if type (mod.__dict__ [i]) in (int, str, float):
			D [i] = mod.__dict__ [i]
	return D

def import_constants_from_files (filelist):
	if not filelist:
		return None
	D = {}
	for i in filelist:
		D.update (import_constants (i))
	return D
