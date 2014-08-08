#NEEDS DATA
#!/usr/bin/python
# $Id: wc-python.code,v 1.5 2004/12/05 01:58:32 bfulgham Exp $
# http://www.bagley.org/~doug/shootout/
# with help from Brad Knotwell

#DEJAVU
'''
{
'NAME':"Wordcount",
'DESC':"Wordcount from computer language shootout -- slightly modified",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"2",
'BARGS':"180"
}
'''

import sys

def main(N):
    for i in N:
        wc ('DATA/wc-input.txt')

def wc (fnm):
    lines = file (fnm).readlines()
    nl = nw = nc = 0
    nl += len(lines)
    for line in lines:
        nc += len(line)
        nw += len(line.split())

    print "%d %d %d" % (nl, nw, nc)

main(range (int (sys.argv[1])))
