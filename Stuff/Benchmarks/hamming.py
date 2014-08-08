
import sys

#DEJAVU
'''
{
'NAME':"Hamming sequence",
'DESC':"Hamming sequence from Jeff Eppler c.l.py post",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"1",
'BARGS':"150"
}
'''

#
# This does only up to the 1690th hamming number because beyond
# that it doesn't fit in 32 bit integer
#

from itertools import tee, islice, izip, count
import sys

def imerge(xs, ys):
    x = xs.next()
    y = ys.next()
    while 1:
        if x == y:
            yield x
            x = xs.next()
            y = ys.next()
        elif x < y:
            yield x
            x = xs.next()
        else:
            yield y
            y = ys.next()

def tee4(itr):
    t1, t2 = tee(itr)
    t1 = tee (t1)
    t2 = tee (t2)
    return (t1 [0], t1 [1], t2 [0], t2 [1])

if sys.copyright.startswith ('pyvm'):
 def hamming():
    generators = []
    def _hamming(j, k):
        yield 1
        hamming = generators[j]
        for i in hamming:
            yield i * k
    generator = imerge(imerge(_hamming(0, 2), _hamming(1, 3)), _hamming(2, 5))
    generators[:] = tee4(generator)
    return generators[3]
else:
 def hamming():
    def _hamming(j, k):
        yield 1
        hamming = generators[j]
        for i in hamming:
            yield i * k
    generators = []
    generator = imerge(imerge(_hamming(0, 2), _hamming(1, 3)), _hamming(2, 5))
    generators[:] = tee(generator, 4)
    return generators[3]

def main (N):
 if N==1:
  for i,j in izip (islice (hamming(), 1690), count()):
    print j, i
 else:
    for xx in xrange (N):
	for i in islice (hamming (), 1690):
	    pass

main (int (sys.argv [1]))
