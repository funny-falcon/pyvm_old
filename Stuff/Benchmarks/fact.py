#! /usr/bin/env python

#DEJAVU
'''
{
'NAME':"factorize",
'DESC':"fact.py from Python/Demos/scripts",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"SEM",
'BARGS':""
}
'''

# Factorize numbers.
# The algorithm is not efficient, but easy to understand.
# If there are large factors, it will take forever to find them,
# because we try all odd numbers between 3 and sqrt(n)...

import sys
from math import sqrt

error = 'fact.error'            # exception

def fact(n):
    if n < 1: raise error   # fact() argument should be >= 1
    if n == 1: return []    # special case
    res = []
    # Treat even factors special, so we can use i = i+2 later
    while n%2 == 0:
        res.append(2)
        n = n/2
    # Try odd numbers up to sqrt(n)
    limit = sqrt(float(n+1))
    i = 3
    while i <= limit:
        if n%i == 0:
            res.append(i)
            n = n/i
            limit = sqrt(n+1)
        else:
            i = i+2
    if n != 1:
        res.append(n)
    return res

def main():
    if 'SEM' in sys.argv:
	print 334455, fact (334455)
    else:
	for i in xrange (3000, 340000, 7):
		print i, fact (i)

if __name__ == "__main__":
    main()
