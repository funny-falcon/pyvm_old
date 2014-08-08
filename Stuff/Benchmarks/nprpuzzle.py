

# got it from Skip Montanaro's page,
# http://orca.mojam.com/~skip
# very good for testing for-loops and string concat/dicts

#DEJAVU
'''
{
'NAME':"NPR Puzzle",
'DESC':"NPR Weekend Edition puzzle",
'GROUP':'real-bench',
'DATA':'/usr/share/dict/words',
'CMPOUT':1,
'ARGS':"3",
'BARGS':"20"
}
'''

import sys

# From the NPR Weekend Edition puzzle...
# http://www.npr.org/programs/wesun/puzzle/
# The challenge from October 7, 2001 reads:

### Draw a 4 by 3 box. The object is to fill it with letters spelling 3
### four-letter words across and 4 three-letter words reading down. The
### conditions: your box can not repeat any letters, and it must use all six
### vowels (a, e, i, o, u, y) once. All words must be uncapitalized, common
### English words.

class Bad(Exception):
    pass

# Build list of four-letter words - restrict it to as small a set as
# possible because we use it to pick the candidate set of words to consider
words4 = {}
for w in open("/usr/share/dict/words"):
    w = w.strip()
    if len(w) != 4 or w != w.lower():
        continue
    counts = {}
    for l in w:
        counts[l] = counts.get(l,0)+1
    try:
        for k in counts.keys():
            if counts[k] > 1:
                raise Bad
    except Bad:
        continue
    words4[w] = 1

print "found", len(words4), "candidate four-letter words"

# Build list of three-letter words - don't need to be as restrictive as
# with four-letter words - only used for comparisons
words3 = {}
[words3.update({w.strip():1})
 for w in open("/usr/share/dict/words")
 if len(w.strip()) == 3 and w == w.lower()]

def check(N):
    # march through candidates in an orderly fashion
    candidates = words4.keys()
    candidates.sort()
    
    write = sys.stdout.write
    flush = sys.stdout.flush
    is3 = words3.has_key

    for wi in candidates [:N]:
        write(' '+wi+' ') ; flush()
        # examine retricted set of candidates - those with no letters in
        # common with wi
        jlist = tuple ([w for w in candidates
                 if (wi[0] not in w and
                     wi[1] not in w and
                     wi[2] not in w and
                     wi[3] not in w)])
        for wj in jlist:
            # examine a further restricted set of candidates - those with
            # no letters in common with wi or wj
            klist = [w for w in jlist
                     if (wj[0] not in w and
                         wj[1] not in w and
                         wj[2] not in w and
                         wj[3] not in w)]
            for wk in klist:
                w = wi+wj+wk
		w_count = w.count
                # do we have one of each vowel?
                # does each three-letter string form a word?
                if (w_count("a") == w_count("e") == 
                    w_count("i") == w_count("o") ==
                    w_count("u") == w_count("y") == 1 and
                    is3(wi[0]+wj[0]+wk[0]) and
                    is3(wi[1]+wj[1]+wk[1]) and
                    is3(wi[2]+wj[2]+wk[2]) and
                    is3(wi[3]+wj[3]+wk[3])):
                    write(' '+`(wi,wj,wk)`+' ') ; flush()

check(int (sys.argv [1]))
print

