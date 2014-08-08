#!/usr/bin/python
# $Id: fibo-python.code,v 1.5 2004/12/05 01:58:28 bfulgham Exp $
# http://www.bagley.org/~doug/shootout/

#DEJAVU
'''
{
'NAME':"Fibonacci",
'DESC':"Fibonacci from computer language shootout",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"25",
'BARGS':"30"
}
'''

import sys

def Fib(n):
    def fib(n):
        if (n < 2):
            return(1)
        return( fib(n-2) + fib(n-1) )
    return fib(n)

def main():
    N = int(sys.argv[1])
    #sys.setrecursionlimit(3000)
    print Fib(N)

main()

