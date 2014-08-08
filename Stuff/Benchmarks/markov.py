import random
import sys

import sys

#DEJAVU
'''
{
'NAME':"Markov Chain",
'DESC':"The Markov Chain Algorithm ASPN recipe from Brian Chin",
'GROUP':'real-bench',
# The output can be compared as long as python and pyvm have the
# same random number generator and the seed yields the same sequence
# This is true for python 2.4
# Otherwise, set cmpout to 0
'CMPOUT':2,
'ARGS':"SEM",
'BARGS':"",
'DATA':'DATA/Darwin.txt'
}
'''

SEMANTIC = 'SEM' in sys.argv

nonword = "\n" # Since we split on whitespace, this can never be a word

def readtable (fnm):
    w1 = nonword
    w2 = nonword

    # GENERATE TABLE
    table = {}

    for line in file (fnm):
        for word in line.split():
            table.setdefault( (w1, w2), [] ).append(word)
            w1, w2 = w2, word

    table.setdefault( (w1, w2), [] ).append(nonword) # Mark the end of the file
    return table

def maketext(table):
    # GENERATE OUTPUT
    w1 = nonword
    w2 = nonword


    random.seed (10)

    if SEMANTIC:
     maxwords = 3000
     for i in xrange(maxwords):
        newword = random.choice(table[(w1, w2)])
        if newword == nonword: break
        print newword,
        w1, w2 = w2, newword
     print
    else:
     maxwords = 48000
     for i in xrange(maxwords):
        newword = random.choice(table[(w1, w2)])
        if newword == nonword: break
        w1, w2 = w2, newword

TEXT='DATA/CrimeNPunishment.txt'
TEXT='DATA/ProblemChild.txt'
TEXT='DATA/Darwin.txt'
#TEXT='DATA/wordfreq-input.txt'
if SEMANTIC:
    maketext(readtable (TEXT))
else:
    table = readtable (TEXT)
    maketext(table)
