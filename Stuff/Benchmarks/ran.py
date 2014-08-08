#random

#!/usr/bin/python
# $Id: random-python.code,v 1.5 2004/12/05 01:58:28 bfulgham Exp $
# http://www.bagley.org/~doug/shootout/
# with help from Brent Burley


#DEJAVU
'''
{
'NAME':"Random",
'DESC':"Random from computer language shootout",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"100",
'BARGS':"700000"
}
'''

import sys

IM = 139968
IA = 3877
IC = 29573

LAST = 42
def gen_random(max):
    global LAST
    LAST = (LAST * IA + IC) % IM
    return( (max * LAST) / IM )

def main():
    N = int(sys.argv[1])
    if N < 1:
        N = 1
    gr = gen_random
    for i in xrange(1,N):
        gr(100.0)
    print "%.9f" % gr(100.0)

main()
