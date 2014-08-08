import sys

import os

lst=os.listdir('.')

ones=[x for x in lst if x.endswith ('pyc1')]

import marshal

def showc(x):
    yield x.co_name, x.co_stacksize
    for i in x.co_consts:
        if type (i) == type (x):
		for j in showc (i):
		    yield j

for i in ones[:4]:
    t = i [:-1]+'2'
    x=list (showc (marshal.loads (file (i).read ()[8:])))
    y=list (showc (marshal.loads (file (t).read ()[8:])))
    if x==y:
	print i[:-2], "ok"
    else:
	print i[:-2], "PROBLEMS:"
	for i in zip (x,y):
	    if i[1]!=i[0]:
		print '   ',i
