# (c) 2005 Peter Goodspeed's sister
#plife.py - conway's game of life, with no object-orientation,
# a DIMxDIM non-wrapping grid, and no exceptions

#DEJAVU
'''
{
'NAME':"Life",
'DESC':"Game of life by Peter Goodspeed's sister (from shedskin's tests)",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"20",
'BARGS':"33"
}
'''

import sys
DIM = int (sys.argv [1])

#functions
def rawBoard():
        return [DIM * [False] for i in xrange(DIM)]

#def fromKb():
#        eventLoop(lambda arg: raw_input(arg))

def nextI(qstr):
        global source
        if source == 1: #from keyboard
                return raw_input(qstr)
        elif source == 2: #from file
                global flines
                global fcur
                if fcur < len(flines):
                        ret = flines[fcur]
                        fcur += 1
                        return ret


def pb(board):
        #print board
        print "-" * DIM
        for row in board:
                ro = ''
                for i in xrange(len(row)):
                        if row[i]: ro += "X"
                        else: ro += " "
                print ro
        print "-" * DIM

def eventLoop(nextInput):
       cont = 'p'
       while cont.lower()[0] == 'p':
                board = rawBoard()

                #how many inputs should we expect?
                numcells = int(nextInput("how many cells? "))

                #get that many cells
                for i in xrange(numcells):
                        xy = str(nextInput("x,y: ")).split(',')
                        x,y = int(xy[0]),int(xy[1])
                        #set those cells
                        board[x][y] = True

                #pb(board)
                runSim(board)

                cont = nextInput("play again? (p for yes; anything else for no): ")

def runSim(board):
        #main loop for simulating life
        turns = 0
        ob = None # old board

        while turns < 50 and board != ob:
                turns += 1
                ob = board
                board = nextgen(board)
                #pb(board)
                #print
        if turns >= 50: print "50 turns exhausted"
        else: print "stabilized on turn %s" % str(turns + 1)

def nextgen(board):
        #transform the old board into a new one
        nb = rawBoard()

        for rown in xrange(len(board)):
                for coln in xrange(len(board[rown])):
                        nn = 0
                        for r,c in neighbors(rown, coln):
                                if board[r][c]: nn += 1
                        if nn == 3: nb[rown][coln] = True
                        elif nn >= 4 or nn < 2: nb[rown][coln] = False
                        else: nb[rown][coln] = board[rown][coln]

        return nb

def neighbors(x,y):
        rl = []
        for mx in [-1,0,1]:
                for my in [-1,0,1]:
                        if not (mx == 0 and my == 0):
                                r = (x + mx, y + my)
                                if r[0] >= 0 and r[0] < DIM and r[1] >= 0 and r[1] < DIM:
                                        rl.append(r)
        return rl

#main
source = 0
while source not in [1,2]:
        source = 2 #int(raw_input("1 for input from keyboard; 2 for input from file: "))

if source==2:
        fp = open('DATA/life.txt')
        flines = [line for line in fp]
        fp.close()
        fcur = 0

eventLoop(nextI)
