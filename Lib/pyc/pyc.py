# This file is used for testing the compiler (new features, etc)
# but it's not good for frontend of pyc

from root import *

from sys import argv
from time import time

USAGE="""pyc [options] file1 file2 ...

	--no-dynlocals:	Enable optimization of local variables
	--rrot3:	The vm prefers the sequence ROT2-ROT3-ROT2 over a LOAD_FAST
	--py2ext:	Accept Py2Extensions [default]
	--no-py2ext:	Forbid Py2Extensions
	--no-lnotab:	Do not emit the line-number table
	--show-marks:	Print various symbols for successful optimizations
	--pyvm		Enable special pyvm features

	--arch-[2.3|2.4|pyvm]
			bytecode format. 'pyvm' enables "shared names tuple"

	--marshal-builtin:	DON'T USE WITH Python 2.4

	--constants-file=xx.py	: Load constants from file's __all__ and inline into functions
	--no-mtime	Do not emit dependency check code for the constants file modification

	-O		Remove assert statements
	-O3		--no-dynlocals, remove asserts

pyc is free software, covered by the GNU General Public License.
pyc is derrived from Python-2.4 'compiler module'.
"""

options = {
	'--no-dynlocals':{'dynlocals': False},
	'--no-lnotab':{'nolno': True},
	'-O':{'asserts': False, 'dynlocals':False, 'docstrings':False},
	'-O3':{'dynlocals': False},
	'--py2ext':{'py2ext': True},
	'--no-py2ext':{'py2ext': False},
	'--show-marks':{'showmarks': True},
	'--rrot3':{'rrot3': True},
	'--no-mtime': {'mtime': False},
	'--marshal-builtin': {'marshal_builtin': True},
	'--pyvm':{'pyvm':True},
}
files = []
kwopts = {}

CONSTANTS = []

iarg = iter (argv [1:])

for i in iarg:
	if i [0] == '-':
		try:
			kwopts.update (options [i])
		except KeyError:
			if i.startswith ('--arch-'):
				kwopts ['arch'] = i [7:]
			elif i.startswith ('--constants-file='):
				CONSTANTS.append (i [17:])
			else:
				print "Invalid option:", i
				print USAGE
				raise SystemExit
	else:
		files.append (i)

if CONSTANTS is not None:
	kwopts ['constfiles'] = CONSTANTS

t0=time()

for i in files:
	print 'compiling %s ...' %i
	compileFile (i, **kwopts)

print 'totaltime:', time()-t0
