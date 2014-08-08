#
# taken from python2.4 Lib/tests/test_genexp.py
#

def verify (x,y):
    if x != y: print "FAIL"
    else: print "OK"
def verifyn (x,y):
    if x != y: print "FAIL",
    else: print "OK",
def verifyExc (E, f):
    try:
	f ()
    except E:
	print "OK"
	return
    print "FAIL"


print "Test simple loop with conditional",
def sum (itr):
    s = 0
    for i in itr:
	s += i
    return s
verify (sum(i*i for i in range(100) if i&1 == 1), 166650)

print "Test simple nesting",

verify (list((i,j) for i in range(3) for j in range(4) ),
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)])

print "Test nesting with the inner expression dependent on the outer",

verify (list((i,j) for i in range(4) for j in range(i) ),
    [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2)])

print "Make sure the induction variable is not exposed",

i = 20
verifyn ( sum(i*i for i in range(100)), 328350)
verify (i, 20)

print "Test first class",

g = (i*i for i in range(4))
verify (list(g), [0, 1, 4, 9])

print "Test direct calls to next()",

g = (i*i for i in range(3))
verifyn (g.next(), 0)
verifyn (g.next(), 1)
verifyn (g.next(), 4)
verifyExc (StopIteration, g.next)

print "Does it stay stopped?",

verifyExc (StopIteration, g.next)
verify (list(g), [])

print "Test running gen when defining function is out of scope",

def f(n):
    return (i*i for i in xrange(n))
verifyn (list(f(10)), [0, 1, 4, 9, 16, 25, 36, 49, 64, 81])

def f(n):
    return ((i,j) for i in xrange(3) for j in xrange(n))

verifyn ( list(f(4)),
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)])
def f(n):
    return ((i,j) for i in xrange(3) for j in xrange(4) if j in xrange(n))
verifyn (list(f(4)),
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)])
verify ( list(f(2)),
    [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)])


print "Verify early binding for the outermost for-expression",

x=10
g = (i*i for i in range(x))
x = 5
verify ( list(g), [0, 1, 4, 9, 16, 25, 36, 49, 64, 81])

print "Verify that the outermost for-expression makes an immediate check for iterability",

try:
    x = (i for i in 6)
except TypeError:
    print "OK"
else:
    print "FAIL"

print "Verify late binding for the outermost if-expression",

include = (2,4,6,8)
g = (i*i for i in range(10) if i in include)
include = (1,3,5,7,9)
verify (list(g), [1, 9, 25, 49, 81])

print "Verify late binding for the innermost for-expression",

g = ((i,j) for i in range(3) for j in range(x))
x = 4
verify (list(g),
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)])

print "Verify re-use of tuples (a side benefit of using genexps over listcomps)",

tupleids = map(id, ((i,i) for i in xrange(10)))
verify (max(tupleids) - min(tupleids), 0)




print "Make a generator that acts like range()",

yrange = lambda n:  (i for i in xrange(n))
verify (list(yrange(10)),
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

print "Generators always return to the most recent caller:",

def creator():
    r = yrange(5)
    print "creator", r.next()
    return r
def caller():
    r = creator()
    for i in r:
            print "caller", i
caller()

print "Generators can call other generators:",

def zrange(n):
    for i in yrange(n):
        yield i
verify (list(zrange(5)), [0, 1, 2, 3, 4])

print "That's all folks! No more tests"
