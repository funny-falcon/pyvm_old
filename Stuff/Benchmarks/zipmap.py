
#
# IF N is too big then zip may need to alloc too much memory
# and eventually swap.  Not good.
#

#DEJAVU
'''
{
'NAME':"zipmap",
'DESC':"What's faster: zip, izip or map? Derrived from c.l.py post by Mandus",
'GROUP':'real-bench',
'CMPOUT':0,
'ARGS':"",
'BARGS':""
}
'''

from itertools import izip
from time import time

def f1():
    return map(lambda bb,ii,dd: bb+ii*dd,b,i,d)
def f2():
    return [ bb+ii*dd for bb,ii,dd in zip(b,i,d) ]
def f3():
    return [ bb+ii*dd for bb,ii,dd in izip(b,i,d) ]

def run(f, K):
    t0 = time ()
    for i in xrange (K):
	f()
    return time()-t0

T = 100000

def BENCH(K):
    global b, i, d
    N = T/K
    print "%i times tuples of size %i:" % (K,N)
    b = tuple (range(0, -N, -1))
    i = tuple (range(N))
    d = tuple (N*[1])
    for x, y in sorted ([ (run (x1,K), y1) for x1, y1 in ((f2,'zip'),(f3,'izip'))]):
    #for x, y in sorted ([ (run (x1,K), y1) for x1, y1 in ((f1,'map'),(f2,'zip'),(f3,'izip'))]):
	print '%s: %.2f' %(y,x),
    print

BENCH(200000)
BENCH(20000)
BENCH(2000)
BENCH(200)
BENCH(20)
BENCH(1)
