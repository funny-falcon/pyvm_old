"""
The Grand Robot Pyramid Schema

We have 1000 robots.  One robot has the 'product' initially.
Each robot that has the product is obliged to give it to two
other (random) robots.  If a robot already has the product it
does nothing.  How many robots will eventually have the
product and therefore be liable of piracy?

There is certainly a mathematical answer to this, but we
will do this with a statistical algorithm.
"""


import sys

#DEJAVU
'''
{
'NAME':"Robots/Pyramid",
'DESC':"Robotic Pyramid Schema",
'GROUP':'real-bench',
'CMPOUT':2,
'ARGS':"10",
'BARGS':"120"
}
'''


from random import random, seed
import sys

seed (2233)

sys.setrecursionlimit (40000000)

P=1000
CNT=0

def share(root, G, int=int, random=random,P=P):
    if LST [root]:
	return
    LST[root] = 1
    global CNT
    CNT += 1
    for i in G:
	# robot not allowed to give to self
	n = root
        while n == root:
    	    n = int (random () * P)
        share (n, G)

N = int (sys.argv [1])

def runtest (G=2):
  global CNT
  global LST
  sum=0
  for i in xrange (N):
    CNT = 0
    LST = [0]*P
    share (int (random () * P), range (G))
    #print 'total took:', CNT
    sum += CNT
  return 100.0 * float (sum/N) / float (P)

for i in [2,3,4]:
	print 'If each robot copies the product to %i other robots, eventually %.2f%% of the population will be guilty of piracy' % (i, runtest (i))

