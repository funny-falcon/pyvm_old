#!/usr/bin/env python

import sys


#DEJAVU
'''
{
'NAME':"nccstrip",
'DESC':"""nccstrip of the ncc source code analyser, stripping python's
callgraph.  nccstrip *is not* a well written python program for at the
time I wrote it I knew little about python vms ;-). Still, it is very
good to test non well-written programs!""",
'GROUP':'real-bench',
'CMPOUT':1,
'DATA':'DATA/nccout',
'ARGS':"1",
'BARGS':"4"
}
'''

import sys

def getsub (line, set):
    TS = ''
    TL = [ line ]
    for j in infile:
        if j[0] not in set:
            break
	j = j[:-1]
	TS += j
	TL.append (j)
    if line in have:
	X = have [line]
	if type(X) == type (''):
	    if X == TS:
		return
	    have [line] = [X, TS]
	else:
	    for k in have [line]:
	        if k == TS:
		    return
	    have [line].append (TS)
    else:
	have [line] = TS
    for j in TL:
	print j;
    print

def main():
 global have
 have = {}
 global infile
 infile = file ('DATA/nccout')
 for i in infile:
    if i [0] == '#':
	continue
    if i [0] == 'D':
	getsub (i[:-1], 'FgGsS')
    elif i [0] == 'P':
	getsub (i[:-1], 'YL')
    else:
	print i[:-1]

for i in range (int (sys.argv [1])):
 main ()
