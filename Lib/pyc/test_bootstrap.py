#
# Three stage bootstrap.
#
# First we compile "the compiler" with CPython.  That gives us
# compiler 'pyc1'.
# Then we compile the compiler with 'pyc1' and that generates
# a new compiler 'pyc2'.
# Finally, we compile the compiler with 'pyc2' resulting in
# a new compiler 'pyc3'.
# 
# The object files from pyc2 and pyc3 should be the same otherwise
# we are in serious trouble.
#


from test_util import *
import sys

vsystem ('rm -f *.pyc *.pyc2 *.pyc3 xxxx.py')

def build ():
#   vsystem ('python -v pyc.pyc *.py')
    if 1:
	vsystem ('pyvm build.pyc ' + ' '.join (sys.argv [1:]))
#	vsystem ('valgrind --tool=memcheck --num-callers=12 pyvm build.pyc ' + ' '.join (sys.argv [1:]))
    elif 0:
	vsystem ('python2.3 build.py')
    else:
	vsystem ('python build.py')

print '########### Stage 1 #################'

vsystem ("""python -c 'import compileall; compileall.compile_dir (".")'""")
for i in forfile ('.pyc'):
    vsystem ('cp %s %s1' %(i,i))

print '########### Stage 2 #################'
build()
for i in forfile ('.pyc'):
    vsystem ('cp %s %s2' %(i,i))

print '########### Stage 3 #################'
build()

for i in forfile ('.pyc'):
    vsystem ('cp %s %s3' %(i,i))

print '############ comparing 2 & 3 #############'

for i in forfile ('.pyc2'):
    print i[:-5], ':',
    if system ('diff %s %s' %(i, i[:-1]+'3')):
	print 'FAIL. BOOTSTRAP BR0KEN'
	break
    else:
	print "Ok"
else:
    pass
#    system ('rm -f *.pyc *.pyc2 *.pyc3 xxxx.py *.pyc1')
    system ('rm -f *.pyc2 *.pyc3 xxxx.py *.pyc1')
