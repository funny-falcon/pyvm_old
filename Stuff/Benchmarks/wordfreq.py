
#wordfreq
#!/usr/bin/python
# $Id: wordfreq-python.code,v 1.5 2004/12/05 01:58:32 bfulgham Exp $
# http://shootout.alioth.debian.org/
#
# adapted from Bill Lear's original python word frequency counter
#
# Joel Rosdahl suggested using translate table to speed up
# word splitting.  That change alone sped this program up by
# at least a factor of 3.
#
# with further speedups from Mark Baker

import sys


#DEJAVU
'''
{
'NAME':"Wordfreq",
'DESC':"Wordfreq from computer language shootout",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"1",
'BARGS':"10"
}
'''

def main(printem):
    count = {}
    i_r = map(chr, range(256))

    trans = [' '] * 256
    o_a, o_z = ord('a'), (ord('z')+1)
    trans[ord('A'):(ord('Z')+1)] = i_r[o_a:o_z]
    trans[o_a:o_z] = i_r[o_a:o_z]
    trans = ''.join(trans)

    for line in file ('DATA/wordfreq-input.txt'):
        for word in line.translate(trans).split():
            try:
                count[word] += 1
            except KeyError:
                count[word] = 1

    l = zip(count.values(), count.keys())
    l.sort()
    l.reverse()

    if printem:
        print '\n'.join(["%7i %s" % (count, word) for (count, word) in l])
    else:
        '\n'.join(["%7i %s" % (count, word) for (count, word) in l])

for i in range (int (sys.argv [1])):
    main(sys.argv [1] == '1')
