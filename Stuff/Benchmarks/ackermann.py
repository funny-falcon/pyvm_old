#!/usr/bin/python
# $Id: ackermann-python.code,v 1.7 2005/03/16 08:37:10 bfulgham Exp $
# http://www.bagley.org/~doug/shootout/
# from Brad Knotwell


import sys

#DEJAVU
'''
{
'NAME':"Ackermann",
'DESC':"Ackermann from computer language shootout",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"5",
'BARGS':"8"
}
'''

import sys
sys.setrecursionlimit(5000000)

def Ack(M, N):
    if (not M):
        return( N + 1 )
    if (not N):
        return( Ack(M-1, 1) )
    return( Ack(M-1, Ack(M, N-1)) )

def main(NUM):
    sys.setrecursionlimit(10000)
    print "Ack(3,%d): %d" % (NUM, Ack(3, NUM))

if __name__=='__main__':
    main(int (sys.argv [1]))
