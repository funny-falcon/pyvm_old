#
# This is the BIOS of pyvm
#
# We are not allowed to call any python bytecode
# unless it's protected inside try..except
#
# 'traceback' is a builtin in pyvm for the moment
#
# __import_compiled__ is a special builtin which should
# probably be named '__execcompiled__' and it runs a pyc
# file from its path location (doesn't use sys.path) and
# without using the import lock.
#
# 'make BIOS' to recompile
#
import sys, traceback

__version__ = 'pyvm 1.2'

# this file is indented with spaces on purpose so we will
# be reluctant to modify without having thought about it.

def _COMPAT ():
    del _COMPAT

    # Python provides some builtins which'd better be done in python
    # because either speed doesn't matter or there are newer 2.4 features
    # that deprecate them. By implementing them in python here, we reduce
    # the size of the binary of pyvm.
    # However, we must make sure that they aren't used by pyc in the bootstrap
    # procedure.

    class super:
        def __getattr__ (self, x):
            a = getattr (self.t1, x)
            if callable (a) and self.ot:
                x = self.ot
                return lambda *args, **kwargs: a (x, *args, **kwargs)
            return a

    def _super (t, ot=None):
        s = super ()
        s.t1 = t.__bases__ [0]
        s.ot = ot
        return s

    def sorted (lst, **kwargs):
        lst = list (lst)
        lst.sort ()
        return lst

    def _issubclass (C, B):
        if C is B:
            return True
        for i in C.__bases__:
            if _issubclass (i, B):
                return True
        return False
    def issubclass (C, B):
        if type (B) is tuple:
            for i in B:
                if _issubclass (C, i):
                    return True
        else:
            return _issubclass (C, B)

    __builtins__.super = _super
    __builtins__.sorted = sorted
    __builtins__.issubclass = issubclass

    # file methods
    sys.stdout.__dict__ ['readlines'] = lambda f: [xxx for xxx in f]
    def readline (f, size=0):
        try:
            return f.next ()
        except StopIteration:
            return ''
    sys.stdout.__dict__ ['readline'] = readline

    # the pyc compiler transforms `print>>S,x` to `__print_to__(S.write,x)`
    __builtins__.__print_to__ = lambda W, *args: map (W, map (str, args))

    # auto-import sys !!
    __builtins__.sys = sys
    sys.prefix = '/usr/local'

    # string.stuff (bw compat. yawn)
    import string
    string.lower = str.lower
    string.rfind = str.rfind
    string.find = str.find

    # methods of object
    def obj__new__ (S, *args, **kwargs):
        return S (*args, **kwargs)
    def obj__str__ (S):
        return '<%s.%s object at %i>' %(__module__, S.__class__.__name__, id (S)) 
    object.__dict__ ['__new__'] = obj__new__
    object.__dict__ ['__str__'] = obj__str__


def BIOS ():

    del BIOS

    ##print "pyvm BIOS 1.0"

    try:
        _COMPAT ()
    except:
        print "BIOS: (errors in _COMPAT)"

    if not sys.argv:
        print "BIOS: Hi!"
        return

    if sys.argv [0] == '-V':
        print __version__
        return

    if sys.argv [0].endswith ('.pyc'):
        pycfile = sys.argv [0]
    elif sys.argv [0].endswith ('.py') or sys.argv [0].endswith ('.pe'):
        try:
            import pyc
        except:
            print "BIOS: Cannot import the pyc compiler", sys.exc_info ()
            return
        try:
            pycfile = pyc.compileFile (sys.argv [0], pyvm=True, dynlocals=True, marshal_builtin=True)
            ##pycfile = pyc.compileFile (sys.argv [0], pyvm=True, dynlocals=True)
        except:
            print 'BIOS:', sys.argv [0], ":Syntax Error", traceback.format_exc ()
            return
    elif sys.argv [0] == '-cc':
        try:
            import pyc
            ##pyc.compileFile (sys.argv [1], dynlocals=True)
            pyc.compileFile (sys.argv [1], pyvm=True, dynlocals=True, marshal_builtin=True)
        except:
            print "Compilation Failed", sys.exc_info ()
        return
    else:
        print "BIOS: No script"
        return

    if '/' in pycfile:
        try:
            import os
            basedir = os.path.dirname (os.path.abspath (pycfile)) + '/'
            sys.path.insert (0, basedir)
        except:
            print "BIOS: cannot import os.path. Will not add basedir to sys.path"

    try:
        __import_compiled__ (pycfile, '__main__')
    except SystemExit:
        pass
    except:
        try:
            print "BIOS: Uncaught exception:", sys.exc_info (), traceback.format_exc ()
        except:
            try:
                print "BIOS: exception while formatting exception!!", sys.exc_info ()
            except:
                pass

    try:
        sys.exitfunc ()
    except:
        pass

BIOS ()
