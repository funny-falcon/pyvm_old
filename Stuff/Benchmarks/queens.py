
# Example of using generators to implement backtracking search.
# The example below is an implementation of the classic "N queens"
# problem (place N queens on an N x N chessboard so that none are
# threatened by the others.)
#
# Board representation: Since no two queens can be one the same
# row, the board is represented as a tuple of N length, where
# each element is the column occupied by the queen on that row.

#DEJAVU
'''
{
'NAME':"Queens",
'DESC':"Classic N Queens problem from c.l.py",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"5",
'BARGS':"10"
}
'''


    # Function to test if a queen is threatened by any previously
    # placed queen.
def threaten( qarray, newpos ):
        # Now check the diagonals
        dist = len( qarray )        # Distance between rows
        for q in qarray:
            if q == newpos: return True             # Same column
            if q + dist == newpos: return True      # diagonal
            if q - dist == newpos: return True      # diagonal
            dist -= 1
        return False

def qsearch(bsize, qarray = () ):
        for q in range( 0, bsize ):        # Try each position
            if not threaten( qarray, q ):  # If not threatened
                pos = qarray + ( q, );     # Append to the pos array

                if len( pos ) >= bsize:    # Are we done?
                    yield pos              # Yield the answer
                else:            # recursively call new generator
                    for pos in qsearch(bsize, pos ):
                        yield pos

def queens( bsize ):
    print "Queens problem for", bsize, "x", bsize, "board."
    for ans in qsearch(bsize):
        # Print out the board
        print "+" + "---+" * bsize;
        for q in ans:
            print "|" + "   |" * q + " Q |" + "   |" * (bsize - q - 1)
            print "+" + "---+" * bsize;
        print

import sys
queens( int (sys.argv[1]) )
