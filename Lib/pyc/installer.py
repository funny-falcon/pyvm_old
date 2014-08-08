#
# UNUSED!!!!!!!!!!!!!!
#
# DOES NOT WORK WITH 2.3
#
# -*-*-*-* IGNORE *-*-*-*-
#

from sys import argv
from test_util import vsystem, forfile

USAGE = """Usage: python installer.py [CMD [CMD [CMD ...]]]

Where CMD may be:
	'--help':	Display this text here
	'clean':	Clean .pyc files and other temporaries (not the bins!)
	'make24':	Compile the compiler with itself, produce 2.4 bytecode
	'make23':	Compile the compiler with itself, produce 2.3 bytecode
	'storeXX':	Store all the *.pyc files as bins/*.pycXX
	'fetchXX':	Get bins/*.pycXX to *.pyc (updating the timestamp)
	'packageXXX':	Create tarball

The commands are executed in order.
"""

for i in argv [1:]:
    if i in ('help', '--help', '-h'):
	print USAGE
    elif i == 'clean':
	vsystem ('rm -f *.pyc *~ *.pyc[123] garbage/*.pyc[12] garbage/*.pyc garbage/tmp.py .pyc-jit*')
    elif i in ('make', 'make24'):
	vsystem ('python pyc.py *.py')
    elif i == 'make23':
	vsystem ('python2.3 pyc.py --target=2.3 *.py')
    elif i.startswith ('store'):
	ext = i [5:]
	for i in forfile ('.pyc'):
	    vsystem ('cp %s bins/%s%s' %(i,i,ext))
    elif i.startswith ('package'):
	ext  = i [7:]
	vsystem ('tar c *.py > ../pyc-%s.tar' %ext)

