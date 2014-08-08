# stelios xanthakis
#DEJAVU
'''
{
'NAME':"sudoku",
'DESC':"Sudoku puzzle solver",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"SEM",
'BARGS':"64"
}
'''

from sys import argv
SEMANTIC = 'SEM' in argv
if not SEMANTIC:
    TIMES = int (argv [1])

class Impossible:
    pass

Patterns = []
for r in range (9):
    for c in range (9):
	p = 27*(r/3) + 3*(c/3)
	pl = set (range (9*r, 9*r+9) + range (c, 81, 9) + [p+x for x in (0,1,2,9,10,11,18,19,20)])
	pl.remove (9*r+c)
	Patterns.append (tuple (sorted (list (pl))))

def initboard ():
    x = range (1, 10)
    return [ x [:] for i in xrange (9*9) ]

def printboard (board):
    if not SEMANTIC:
        return
    print 30*'-'
    for i in range (9):
	for j in board [9*i:9*(i+1)]:
	    if type (j) is list:
		#print 'X', 
		print ''.join (map (str, j)),
	    else: print j,
	print
    print 30*'-'

def dupboard (board):
    B = []
    for i in board:
	if type (i) is list:
	    B.append (i [:])
	else:
	    B.append (i)
    return B

def solve (board, coords):
    while coords:
	p, v = coords.pop ()
	board [p] = v
	for i in Patterns [p]:
	    if type (board [i]) is list:
		if v in board [i]:
		    board [i].remove (v)
		    if len (board [i]) == 1:
			board [i] = board [i][0]
			coords.append ((i, board [i]))
	    else:
		if board [i] == v:
		    raise Impossible
    for p, i in enumerate (board):
	if type (i) is list:
	    for j in i:
		try:
		    return solve (dupboard (board), [(p, j)])
		except Impossible:
		    pass
	    raise Impossible
    return board


PP = [
[
"xxxxxxxx1",
"3xx9xx5x7",
"x6x7x2xxx",
"x34x29x86",
"x2x147x5x",
"95x68x47x",
"xxx3x5x9x",
"5x9xx6xx3",
"4xxxxxxxx"
], [
"xxx8xx6xx",
"xxxx258x4",
"xx2x64x1x",
"1x3x7xx5x",
"xxxxxxxxx",
"x4xx9x3x6",
"x8x31x7xx",
"2x698xxxx",
"xx1xx2xxx"
], [
"xxxx8x461",
"xxxxxxxxx",
"x25x41xxx",
"xx96xxxx7",
"7x2xxx5x8",
"1xxxx72xx",
"xxx49x12x",
"xxxxxxxxx",
"238x6xxxx"
], [
"x3x4xx57x",
"xx1x7xxx8",
"25xxxx4xx",
"4xxxx7x65",
"6xx9x2xx3",
"57x34xxx1",
"xxxx9xx26",
"1xxxxx8xx",
"x69xx1x5x"
], [
"xx43xxx9x",
"x7xxx56xx",
"x5x89xxx1",
"x2xxxxxx7",
"x9652184x",
"1xxx7xx59",
"3xxxx8x7x",
"xx74xxxx2",
"x4xxx25xx"
], [
"xxxxxxxx2",
"xxxxx8x7x",
"x52xxx31x",
"4x8xx7x2x",
"xxx2x3xxx",
"x7x5xx6x1",
"x67xxx89x",
"x4x6xxxxx",
"9xxxxxxxx"
]
]

def puz2coord (P):
    if len (P) != 9:
	print "P must have 9 rows"
	raise SystemExit
    coords = []
    for r, i in enumerate (P):
	if len (i) != 9:
	    print "Row [%s] doesn't have 9 columns" %i
	    raise SystemExit
	for c, j in enumerate (list (i)):
	    if j != 'x':
		coords.append ((9*r + c, int (j)))
    return coords

try:
  if SEMANTIC:
    for P in PP:
        printboard (solve (initboard (), puz2coord (P)))
  else:
   for i in xrange (TIMES):
    for P in PP:
        printboard (solve (initboard (), puz2coord (P)))
except Impossible:
    print "IMPOSSIBLY IMPOSSIBLE"

