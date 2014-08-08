#>Background:
#>>The problem I'm trying to solve is.
#>>There is a 5x5 grid.
#>>You need to fit 5 queens on the board such that when placed there are
#>>three spots left that are not threatened by the queen.


#I know this wasn't a contest, but here's my solution.  This finds 8
#solutions, which are all reflections and rotations of each other:

#DEJAVU
'''
{
'NAME':"5x5 grid",
'DESC':"Solution from Tim Roberts for the c.l.py thread",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"",
'BARGS':""
}
'''

rows = (
  (  1,  2,  3,  4,  5 ),
  (  6,  7,  8,  9, 10 ),
  ( 11, 12, 13, 14, 15 ),
  ( 16, 17, 18, 19, 20 ),
  ( 21, 22, 23, 24, 25 ),
  ( 1, 6, 11, 16, 21 ),
  ( 2, 7, 12, 17, 22 ),
  ( 3, 8, 13, 18, 23 ),
  ( 4, 9, 14, 19, 24 ),
  ( 5, 10, 15, 20, 25 ),
  ( 16, 22 ),
  ( 11, 17, 23 ),
  ( 6, 12, 18, 24 ),
  ( 1, 7, 13, 19, 25 ),
  ( 2, 8, 14, 20 ),
  ( 3, 9, 15 ),
  ( 4, 10 ),
  ( 2, 6 ),
  ( 3, 7, 11 ),
  ( 4, 8, 12, 16 ),
  ( 5, 9, 13, 17, 21 ),
  ( 10, 14, 18, 22 ),
  ( 15, 19, 23 ),
  ( 20, 24 )
)

zeros = [ 0 ] * 25

def printme( cells ):
    for i,j in enumerate(cells):
	print "%2d" % j,
	if i % 5 == 4:
	    print

def check( queens ):
    cells = zeros[:]
    for q in queens:
	for row in rows:
	    if q in row:
		for x in row:
		    cells[x-1] = 1
    nils = len( [1 for k in cells if not k] )
    if nils >= 3:
	for i in queens:
	    cells[i-1] = 9
	print queens
	printme( cells )

for q1 in range(25):
    for q2 in range(q1+1,25):
	for q3 in range(q2+1,25):
	    for q4 in range(q3+1,25):
		for q5 in range(q4+1,25):
		    check( [q1+1,q2+1,q3+1,q4+1,q5+1] )

