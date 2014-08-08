# see http://www.pycontest.net

#DEJAVU
'''
{
'NAME':"117",
'DESC':"Journey to 117 pycontest winning entry from Andri",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"1",
'BARGS':"80"
}
'''

def bench (NN):
	j=''.join;seven_seg=lambda z:j(j(' _   |_|_ _| |'[-~ord("¤Ž°Ú¬¼hJž"[int(a)])%u:][:3]for a in z)+"\n"for u in(3,14,10))
	from test_vectors import test_vectors
	for tt in xrange (NN):
		for i, s in test_vectors.iteritems ():
			if seven_seg (i) != s:
				print "FAIL:"

import sys
bench (int (sys.argv [1]))
