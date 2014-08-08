#
# taken from Python-2.4 Lib/tests/test_decorators.py
#

def funcattrs(**kwds):
    def decorate(func):
        func.__dict__.update(kwds)
        return func
    return decorate

class MiscDecorators (object):
    @staticmethod
    def author(name):
        def decorate(func):
            func.__dict__['author'] = name
            return func
        return decorate

# -----------------------------------------------

class DbcheckError (Exception):
    def __init__(self, exprstr, func, args, kwds):
        # A real version of this would set attributes here
        Exception.__init__(self, "dbcheck %r failed (func=%s args=%s kwds=%s)" %
                           (exprstr, func, args, kwds))


def dbcheck(exprstr, globals=None, locals=None):
    "Decorator to implement debugging assertions"
    def decorate(func):
        expr = compile(exprstr, "dbcheck-%s" % func.func_name, "eval")
        def check(*args, **kwds):
	    if not globals:
		if not eval (expr):
                    raise DbcheckError(exprstr, func, args, kwds)
	    elif not eval(expr, globals, locals):
                raise DbcheckError(exprstr, func, args, kwds)
            return func(*args, **kwds)
        return check
    return decorate

# -----------------------------------------------

def countcalls(counts):
    "Decorator to count calls to a function"
    def decorate(func):
        func_name = func.func_name
        counts[func_name] = 0
        def call(*args, **kwds):
            counts[func_name] += 1
            return func(*args, **kwds)
        call.func_name = func_name
        return call
    return decorate

# -----------------------------------------------

def memoize(func):
    saved = {}
    def call(*args):
        try:
            return saved[args]
        except KeyError:
            res = func(*args)
            saved[args] = res
            return res
        except TypeError:
            # Unhashable argument
            return func(*args)
    call.func_name = func.func_name
    return call

# -----------------------------------------------

def verify(x, y, msg=None):
    if x != y:
	if msg:
	    print msg
	FAIL ()

def FAIL ():
    print "FAIL"
    raise SystemExit

def verifyRaises (E, f, *args):
    try:
	f (*args)
    except E:
	return
    FAIL ()

def test_single():
        class C(object):
            @staticmethod
            def foo(): return 42
        verify(C.foo(), 42)
        verify(C().foo(), 42)

def test_dotted():
        decorators = MiscDecorators()
        @decorators.author('Cleese')
        def foo(): return 42
        verify(foo(), 42)
        verify(foo.author, 'Cleese')

def test_argforms():
        # A few tests of argument passing, as we use restricted form
        # of expressions for decorators.

        def noteargs(*args, **kwds):
            def decorate(func):
                setattr(func, 'dbval', (args, kwds))
                return func
            return decorate

        args = ( 'Now', 'is', 'the', 'time' )
        kwds = dict(one=1, two=2)
        @noteargs(*args, **kwds)
        def f1(): return 42
        verify(f1(), 42)
        verify(f1.dbval, (args, kwds))

        @noteargs('terry', 'gilliam', eric='idle', john='cleese')
        def f2(): return 84
        verify(f2(), 84)
        verify(f2.dbval, (('terry', 'gilliam'),
                                     dict(eric='idle', john='cleese')))

        @noteargs(1, 2,)
        def f3(): pass
        verify(f3.dbval, ((1, 2), {}))

def test_dbcheck():
        @dbcheck('args[1] is not None')
        def f(a, b):
            return a + b
        verify(f(1, 2), 3)
        verifyRaises(DbcheckError, f, 1, None)

def test_memoize():
        counts = {}

        @memoize
        @countcalls(counts)
        def double(x):
            return x * 2
        verify(double.func_name, 'double')

        verify(counts, dict(double=0))

        # Only the first call with a given argument bumps the call count:
        #
        verify(double(2), 4)
        verify(counts['double'], 1)
        verify(double(2), 4)
        verify(counts['double'], 1)
        verify(double(3), 6)
        verify(counts['double'], 2)

        # Unhashable arguments do not get memoized:
        #
        verify(double([10]), [10, 10])
        verify(counts['double'], 3)
        verify(double([10]), [10, 10])
        verify(counts['double'], 4)

def test_double():
        class C(object):
            @funcattrs(abc=1, xyz="haha")
            @funcattrs(booh=42)
            def foo(self): return 42
        verify(C().foo(), 42)
        verify(C.foo.abc, 1)
        verify(C.foo.xyz, "haha")
        verify(C.foo.booh, 42)

def test_order():
        # Test that decorators are applied in the proper order to the function
        # they are decorating.
        def callnum(num):
            """Decorator factory that returns a decorator that replaces the
            passed-in function with one that returns the value of 'num'"""
            def deco(func):
                return lambda: num
            return deco
        @callnum(2)
        @callnum(1)
        def foo(): return 42
        verify(foo(), 2,
                            "Application order of decorators is incorrect")

def test_eval_order():
        # Evaluating a decorated function involves four steps for each
        # decorator-maker (the function that returns a decorator):
        #
        #    1: Evaluate the decorator-maker name
        #    2: Evaluate the decorator-maker arguments (if any)
        #    3: Call the decorator-maker to make a decorator
        #    4: Call the decorator
        #
        # When there are multiple decorators, these steps should be
        # performed in the above order for each decorator, but we should
        # iterate through the decorators in the reverse of the order they
        # appear in the source.

        actions = []

        def make_decorator(tag):
            actions.append('makedec' + tag)
            def decorate(func):
                actions.append('calldec' + tag)
                return func
            return decorate

        class NameLookupTracer (object):
            def __init__(self, index):
                self.index = index

            def __getattr__(self, fname):
                if fname == 'make_decorator':
                    opname, res = ('evalname', make_decorator)
                elif fname == 'arg':
                    opname, res = ('evalargs', str(self.index))
                else:
                    assert False, "Unknown attrname %s" % fname
                actions.append('%s%d' % (opname, self.index))
                return res

        c1, c2, c3 = map(NameLookupTracer, [ 1, 2, 3 ])

        expected_actions = [ 'evalname1', 'evalargs1', 'makedec1',
                             'evalname2', 'evalargs2', 'makedec2',
                             'evalname3', 'evalargs3', 'makedec3',
                             'calldec3', 'calldec2', 'calldec1' ]

        actions = []
        @c1.make_decorator(c1.arg)
        @c2.make_decorator(c2.arg)
        @c3.make_decorator(c3.arg)
        def foo(): return 42
        verify(foo(), 42)

        verify(actions, expected_actions)

        # Test the equivalence claim in chapter 7 of the reference manual.
        #
        actions = []
        def bar(): return 42
        bar = c1.make_decorator(c1.arg)(c2.make_decorator(c2.arg)(c3.make_decorator(c3.arg)(bar)))
        verify(bar(), 42)
        verify(actions, expected_actions)

def R(x):
    print x.func_name,
    x ()
    print "OK"

def test_main():
    R (test_single)
    R (test_dotted)
    R (test_argforms)
    R (test_dbcheck)
    print "This will fail for 2.3:",
    R (test_memoize)
    R (test_double)
    R (test_order)
    R (test_eval_order)

if __name__=="__main__":
    test_main()
