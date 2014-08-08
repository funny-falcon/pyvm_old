# The Great Computer Language Shootout
# http://shootout.alioth.debian.org/
#
# Contributed by Kevin Carson
#
# This example uses loops.


import sys

#DEJAVU
'''
{
'NAME':"Fannkuchen",
'DESC':"Fannkuchen from computer language shootout",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"6",
'BARGS':"8 8 7 7 7 7 7"
}
'''

import sys

def fannkuch(n) :
    p = range(1, n+1)
    q = [None]*n
    maxflips = 0

    while 1:
        if p[0] != 1 :
            q[0:n] = p[0:n]

            flips = 0
            while q[0] != 1 :
                k = q[0] - 1
                i = 0
                while i < k :
                    q[i],q[k] = q[k],q[i]
                    i += 1
                    k -= 1
                flips += 1

            if flips > maxflips :
                maxflips = flips

        j = k = 0
        for i in xrange(1, n) :
            if p[i - 1] < p[i] :
                j = i
            if (j != 0) and (p[i] > p[j-1]) :
                k = i

        if j == 0 :
            break

        p[j-1],p[k] = p[k],p[j-1]

        i = j
        j = n - 1
        while i < j :
            p[i],p[j] = p[j],p[i]
            i += 1
            j -= 1

    return maxflips


def main(n) :
    print "Pfannkuchen(%d) = %d" % (n, fannkuch(n))

for i in sys.argv [1:]:
    main (int (i))
