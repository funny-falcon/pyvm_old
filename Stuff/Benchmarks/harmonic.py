#harmonic
#!/usr/bin/python
# http://shootout.alioth.debian.org/
#
# Contributed by Greg Buchholz

#DEJAVU
'''
{
'NAME':"Harmonics",
'DESC':"Harmonics from computer language shootout",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"10000",
'BARGS':"1000000"
}
'''

import sys

def main():
    s = float(0)
    for i in range(int(sys.argv[1])):
        s = s + 1/(float(i+1))
    print "%.9f" % s

main()

