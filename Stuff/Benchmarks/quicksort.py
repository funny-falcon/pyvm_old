# Python Quicksort Written by Magnus Lie Hetland
# http://www.hetland.org/python/quicksort.html

import sys

#DEJAVU
'''
{
'NAME':"Quicksort",
'DESC':"Quicksort used with phsyco benchmark",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"100 test",
'BARGS':"133000"
}
'''

def _partition(list, start, end):
    pivot = list[end]
    bottom = start-1
    top = end

    done = 0
    while not done:

        while not done:
            bottom = bottom+1

            if bottom == top:
                done = 1
                break

            if pivot < list[bottom]:
                list[top] = list[bottom]
                break

        while not done:
            top = top-1
            
            if top == bottom:
                done = 1
                break

            if list[top] < pivot:
                list[bottom] = list[top]
                break

    list[top] = pivot
    return top


def _quicksort(list, start, end):
    if start < end:
        split = _partition(list, start, end)
        _quicksort(list, start, split-1)
        _quicksort(list, split+1, end)

def quicksort(list):
    if len(list) > 1:
        _quicksort(list, 0, len(list)-1)

# ____________________________________________________________

from sys import argv
import random
random.seed (1234321)
l = range(int (argv [1]))
random.shuffle(l)
quicksort (l)

if 'test' in argv:
    print l
    random.shuffle (l)
    l.sort ()
    print l
