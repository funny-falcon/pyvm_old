#
# This test is not enabled because the first time we run it it
# takes aeons because the dircache is not dirty (or whatever)
#
import os
import sys

class iterdir(object):
    def __init__(self, path, deep=False):
	self._root = path
	self._files = None
	self.deep = deep
    def __iter__(self):
	return self
    def next(self):
	if self._files:
	    join = os.path.join
	    d = self._files.pop()
	    r = join(self._root, d)
	    if self.deep and os.path.isdir(r):
		self._files += [join(d,n) for n in os.listdir(r)]
	elif self._files is None:
	    self._files = os.listdir(self._root)
	if self._files:
	    return self._files[-1]
	else:
	    raise StopIteration
   

# sample:
# 	a deep traversal of directories which starts with a vowel
#
from sys import argv
it = iterdir(argv [1])
for x in it:
    p = os.path.basename(x)
    it.deep = p[0].lower() not in "aeiou"
    print x



#DEJAVU
'''
{
'NAME':"Dirwalk",
'DESC':"dirwalk ASPN recipe",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':".",
'BARGS':"~"
}
'''
