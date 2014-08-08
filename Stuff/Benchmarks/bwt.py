#### XXXX: some times this fails??? on a second re-run, it works !
##
## Name:     bwt.py
## Purpose:  Performs the Burrows-Wheeler Transform (BWT), or its inverse.
## Author:   M. J. Fromberger <http://www.dartmouth.edu/~sting/>
## Info:     $Id: bwt.py,v 1.2 2005/11/04 05:26:59 sting Exp $
##
## Copyright (C) 2003 Michael J. Fromberger, All Rights Reserved.
##
#
# included in the pyvm benchmark suite.
# * modified to use list.sort instead of sorted() because
#   I haven't implemented keyword arguments for sorted().
# * in _get_transform 'chars' is converted to a string
#   because a list doesn't have find()
# If we CJIT the comparison function, it'd be really neat
# to have this in the standard library as a fallback for
# the case we need to bunzip stuff and libbzip2 isn't there!
# we just need to see how to zlib the transformed string and
# primary index.
#
# Thanks to MJF!

def encode_bwt(src):
    """Encode the given string using the Burrows-Wheeler Transform (BWT), a
    block-sorting transformation.  Returns a tuple of the transformed string
    and the primary index (required to decode)."""
    
    vec = _get_sorted_vector(src)
    pix = _get_primary_index(vec)
    
    return ''.join([ src[s - 1] for s in vec ]), pix

def decode_bwt(src, index):
    """Decode a BWT-encoded string, given the primary index.  Returns the
    original string."""
    
    T = _get_transform_vector(src, index)
    
    cursor = index
    out = src[cursor]
    cursor = T[cursor]
    while cursor <> index:
        out += src[cursor]
        cursor = T[cursor]
    
    return out

def _get_transform_vector(src, index):
    charfind = ''.join (list(sorted(src))).find
    tvec = [-1] * len(src)

    for pos in xrange(len(src)):
        offset = 0
        
        while True:
            tloc = charfind(src[pos], offset)
            
            if tvec[tloc] < 0:
                tvec[tloc] = pos
                break
            
            offset = tloc + 1
    
    return tvec

def _get_sorted_vector(src):
    def make_comparator(src):
        size = len(src)
        src = src + src
        
        def compare(i, j):
            for pos in xrange(size):
                p = cmp(src[i], src[j])
                if p <> 0:
                    return p

                i += 1
                j += 1
            
            return 0

        return compare

    X = range (len (src))
    X.sort (make_comparator (src))
    return X
    return sorted(range(len(src)), cmp = make_comparator(src))

def _get_primary_index(vec):
    return vec.index(1)

# Here there be dragons

#DEJAVU
'''
{
'NAME':"Burrows-Wheeler",
'DESC':"Burrows-Wheeler Transform (BWT) (bzip2)",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"bwt.py",
'BARGS':"gengraph.py"
}
'''

from zlib import crc32
import sys

S = file (sys.argv [1]).read ()
C, p = encode_bwt (S)
print crc32 (C)
S2 = decode_bwt (C, p)
print crc32 (S2), crc32 (S)
