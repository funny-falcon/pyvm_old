#
# Compile the toplevel of the batteries with CPython producing garbage/*.pyc1
# Compile with pyc producing garbage/*.pyc2
#
# Use wc -c to calculate the difference
#
# dynlocals-false enabled

import root
from test_util import *
import sys


D = '/usr/local/lib/python2.4/'
TF = "garbage/tmp.py"
TFC = "garbage/tmp.pyc"

#vsystem ('rm -f garbage/*.pyc[12]')
if 0:
 import py_compile
 for i in progress (forfile ('.py', D)):
    vsystem ('cp %s %s' %(D+i,TF))
    vsystem ("""python -c 'import py_compile; py_compile.compile ("%s")'""" % TF)
    py_compile.compile (TF)
    vsystem ('cp %s garbage/%sc1' %(TFC, i))

for i in progress (forfile ('.py', D)):
#    print i
    vsystem ('rm %s' % TFC)
    vsystem ('cp %s %s' %(D+i,TF))
    root.compileFile (TF, dynlocals=False, showmarks=0, rrot3=1)
    vsystem ('cp %s garbage/%sc2' %(TFC, i))
