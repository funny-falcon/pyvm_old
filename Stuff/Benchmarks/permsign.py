
import sys

#DEJAVU
'''
{
'NAME':"xpermutations/permsign",
'DESC':"Compute the permutation sign (Tim Peters) using ASPN recipe (Ulrich Hoffmann)",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"5 SEM",
'BARGS':"8 8 8 8 7"
}
'''

def xcombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xcombinations(items[:i]+items[i+1:],n-1):
                yield [items[i]]+cc

def xpermutations(items):
    return xcombinations(items, len(items))

def permsign(p):
    """Return sign of permutation p.

    p must be a permutation of the list range(len(p)).
    The return value is 1 if p is even, or -1 if p is odd.
    *** MODIFIED ***: return the number of permutations required

    >>> for p in ([0,1,2], [0,2,1], [1,0,2],
    ...           [1,2,0], [2,0,1], [2,1,0]):
    ...     print p, permsign(p)
    [0, 1, 2] 1
    [0, 2, 1] -1
    [1, 0, 2] -1
    [1, 2, 0] 1
    [2, 0, 1] 1
    [2, 1, 0] -1
    """

    n = len(p)
    rangen = range(n)
    if sorted(p) != rangen:
        raise ValueError("p of wrong form")

    # Decompose into disjoint cycles.  We only need to
    # count the number of cycles to determine the sign.
    num_cycles = 0
    seen = {}
    for i in rangen:
        if i in seen:
            continue
        num_cycles += 1
        j = i
        while True:
            seen [j] = 1
            j = p[j]
            if j == i:
                break

    return n - num_cycles

if 'SEM' in sys.argv:
 for i in xpermutations (range(int (sys.argv [1]))):
    print i, permsign(i)
else:
 for n in sys.argv [1:]:
  for i in xpermutations (range(int (n))):
    pass
