import sys

fl = sys.argv [1]
import marshal

x=marshal.loads (file (fl).read ()[8:])
def showc(x):
    print x.co_name, x.co_stacksize
    for i in x.co_consts:
        if type (i) == type (x):
		showc (i)
showc (x)
