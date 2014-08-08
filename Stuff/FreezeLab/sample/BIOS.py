#
# This is the BIOS of frozen pyvm
#
# We are not allowed to call any python bytecode
# unless it's protected inside try..except
#
# Everything has been loaded on memfs://
# We use __import_compiled__ to start the main.pyc script.
# We also modify sys.path to memfs://Lib
#
import sys, traceback

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

    # empty sys.path.
    # We cannot say `sys.path = []`, because it is referenced internally
    # and pyvm will use the old value.
    # We cannot say `del sys.path [:]`, because ATM this opcode is not
    # implemented. So.. clear the list the safe way.
    while sys.path:
        sys.path.pop ()
    sys.path.append ('memfs://Lib/')

    try:
        __import_compiled__ ('memfs://main.pyc' , '__main__')
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
