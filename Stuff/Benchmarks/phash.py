
#DEJAVU
'''
{
'NAME':"Perfect Hash",
'DESC':"Find the perfect string hashing function with brute force",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"1",
'BARGS':"3"
}
'''

#
# we have a string and its length. the hash function can XOR
# characters from the start of the string, from the end and the length.
# the coefficients can be shifted.
# For example:
#	parameters: ((1,1),(-3,0),('l',2))
#  	is the hash function: str [1] >> 1 ^ str [len - 3] ^ len >> 2
#
# Our goal is to find the parameters that for a set of WORDS,
# - obviously generate a different value for each word
# - the values are as close as possible (no gap == perfect)
# - have a good offset (0 is the best but power of 2 is good)
# - it is cheap (few coefficients, zero shifts, no negative indexes)
#
# The program just prints the 'best' 50 with a crappy heuristic and let's
# us figure out more. (for example "str [1]>>2 ^ str [2]>>2" is
# "(str[1]^str[2])>>2" which is cheaper).
#
# For many words it is better to separate them in two subsets by length.
# For example if we want to find the perfect hash of C++'s reserved words
# small keywords ('and', 'or') limit our choices since length can be 0,1,-1,-2
# In this case it's better to make one set of words with length <= 3 and a
# second one with length > 3, find two perfect hashes for the two sets and
# divide the search.
#

WORDS = ('__bases__', '__name__', '__dict__', '__getattr__', '__del__')

def calc (p, s):
    x = 0
    for i, j in p:
	if i == 'l':
	   x = x ^ len (s) >> j
	else:
	   x = x ^ ord (s [i]) >> j
    return x

def cost (*p):
    L = [calc (p, x) for x in WORDS]
    if len (L) != len (set (L)):
	return -1
    L.sort ()
    return L [-1] - L [0]

def prcost (p):
    return [calc (p, x) for x in WORDS]

minlen = min ([len (x) for x in WORDS])
rng = tuple (range (minlen) + range (-minlen, 0) + ['l'])
print minlen, rng

def xperm (items, n):
    if not n:
	yield ()
	return
    for i in items:
	for j in xperm (items, n-1):
            yield (i,) + j
   

def xcomb (items, n):
    if not n:
	yield []
	return
    for i, e in enumerate (items):
	for cc in xcomb (items [i+1:], n-1):
	    yield [e] + cc


def main (SHIFTS):
    from bisect import bisect_right as find
    L = [(1000, 1000)] * 50
    for n in xrange (1, 5):
        shifts = tuple (xperm (range (SHIFTS), n))
        for i in xcomb (rng, n):
	    for s in shifts:
	        j = zip (i, s)
                c = cost (*j)
                if c > 0:
	            pp = c + len (j), tuple (j)
		    if pp < L [-1]:
			L.insert (find (L, pp), pp)
			L.pop ()

    for c, i in L:
        print c, i, prcost (i)

import sys
main (int (sys.argv [1]))

for i in WORDS:
#    print (ord (i [5]) >> 3 ^ len (i)) & 3, i
    print (ord (i [3]) ^ ord (i [-4])) >> 2, i
