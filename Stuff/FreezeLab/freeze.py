from marshal import dump
import zlib
import os
from os.path import isdir
import glob

args = sys.argv [1:]
if not args:
	print """usage: pyvm freeze.py directory"""
	raise SystemExit

BASE = args [0]

print '##### preparing files ######'

os.chdir (BASE)
os.system ('pyvm Make.py')
os.chdir ('..')

EXCLUDE = []
for i in open (os.path.join (BASE,'EXCLUDE')):
	i = i.rstrip ()
	if i:
		EXCLUDE.append (glob.compile (i))

print
print '###### building memfs ########'
MEMFS = {}

def addfile (path, data):
	D = MEMFS
	p = path.split ('/')
	path = p [:-1]
	filename = p [-1]
	for i in path:
		try:
			D = D [i]
		except:
			D [i] = {}
			D = D [i]
	D [filename] = data

def sizeof (l):
	s = '%i'%l
	if len (s) < 4:
		return s
	return s [:-3] + '.' + s [-3:]

def excluded (fnm):
	for j in EXCLUDE:
		if j.match (fnm):
			return True
	return False

SKIPS = []

def addbasedir (D):
	for i in os.listdir (D or '.'):
		i = D + i
		if excluded (i):
			SKIPS.append (i)
			continue
		if isdir (i):
			addbasedir (i + '/')
		else:
			txt = open (i).read ()
			print "adding %s\t(%s bytes)"%(i, sizeof (len (txt)))
			addfile (i, txt)
os.chdir (BASE)
addbasedir ('')
print "SKIPPED:", SKIPS
os.chdir ('..')

def dict2tuple (D):
	L = []
	for k, v in D.iteritems ():
		if type (v) is dict:
			v = dict2tuple (v)
		L.append ((k, v))
	return tuple (L)

MEMFST = dict2tuple (MEMFS)

dump (MEMFST, open ('xxxtmpxxx', 'w'))
MEMFSS = open ('xxxtmpxxx', 'r').read ()
os.remove ('xxxtmpxxx')
print "Frozen memfs size:\t", sizeof (len (MEMFSS))

MEMFSZ = zlib.compress (MEMFSS)
print "Compressed:\t\t", sizeof (len (MEMFSZ))

print
print '###### ICECUBE.c ########'
F = open ('ICECUBE.c', 'w')
W = F.write
W ('static const unsigned char icecubicle [] = {\n')
for n, i in enumerate (list (MEMFSZ)):
	W (str (ord (i)) + ',')
	if not n%20:
		W ('\n')
W ('};\n')
W ('static const int sizeof_icecubicle = sizeof icecubicle;\n')
F.flush ()
F.close ()
os.system ('gcc ICECUBE.c -c -o ICECUBE.o')
print "OK. Your ICECUBE is ready:"
os.system ('size ICECUBE.o')
print
print "Now"
print "1. The file `ICECUBE.c` should be symlinked from toolchain/pyvm/"
print "2. Go to toolchain/pyvm/.  type `make frozen`"
print "3. Build pyvm (`make o3` or `make cygwin` or whatever)"
print "4. strip the executable, copy to new name"
print "5. type `touch boot.c+; make o3` to rebuild pyvm"
