#
# tcl/tk is a frozen ABI for a long time and since tcl/tk's
# strongest point is its avaibility on a great variety of
# systems, it's even more unlikely that the ABI will be broken.
#
# works out of the box
#

#
# this file is mainly a rewrite of python's _tkinter.c
# in python w/ DLL
#
# although, in reallity this is tcl.py: we can call
# a tcl interpreter from python. The tk part is an
# application of this module. Therefore we should allow
# this module to be usable without libtk...
#

import DLL

#
# dynload libtcl
#

libtcl = 'tcl8.4'
TCLlib = DLL.dllopen ('lib' + libtcl + '.so')

def DF (name, spec, ret='', blocking=False):
    globals() [name] = TCLlib.get ((ret, name, spec), blocking)

DF ('Tcl_CreateInterp', '', 'i')
DF ('Tcl_Init', 'i', 'i')
DF ('Tcl_GetCurrentThread', '', 'i')
DF ('Tcl_GetVar2Ex', 'iszi', 'i')
DF ('Tcl_GetObjType', 's', 'i')
DF ('Tcl_DeleteCommand', 'is')
DF ('Tcl_SetVar2', 'isssi', 'i')
DF ('Tcl_SetVar', 'issi', 'i')
DF ('Tcl_GetObjResult', 'i', 'i')
DF ('Tcl_NewStringObj', 'si', 'i')
DF ('Tcl_NewBooleanObj', 'i', 'i')
DF ('Tcl_NewLongObj', 'i', 'i')
DF ('Tcl_NewDoubleObj', 'd', 'i')
DF ('Tcl_SetResult', 'isi')
DF ('Tcl_NewListObj', 'ipv', 'i')
DF ('Tcl_EvalObjv', 'iipvi', 'i', blocking=True)
DF ('Tcl_GetString', 'i', 'i')
DF ('Tcl_GetBoolean', 'isp32')
DF ('Tcl_SplitList', 'isp32pv')
DF ('Tcl_Free', 'i')
DF ('Tcl_SetVar2Ex', 'isvii', 'i')
DF ('Tcl_GetInt', 'isp32')
DF ('Tcl_GetByteArrayFromObj', 'ip32', 'i')
DF ('Tcl_GetStringFromObj', 'ip32', 'i')
DF ('Tcl_ListObjLength', 'iip32', 'i')
DF ('Tcl_ListObjIndex', 'iiipv', 'i')
DF ('Tcl_CreateCommand', 'isiii', 'i')
DF ('Tcl_DoOneEvent', 'i', 'i', blocking=True)

del DF, TCLlib

# dllopen libtk -- only if we got 'wantTk'
# XXX: maybe we can initialize Tk from tcl by calling
# tcl commands, an thus avoid the dlopening

def dynload_Tk ():
    try:
	Tk_Init
	return
    except:
	pass
    TKlib = DLL.dllopen ('libtk8.4.so')
    def DF (name, spec, ret='', blocking=False):
        print "ADD NAME:", name
        globals() [name] = TKlib.get ((ret, name, spec), blocking)
    DF ('Tk_Init', 'i', 'i')
    DF ('Tk_MainWindow', 'i', 'i')
    DF ('Tk_GetNumMainWindows', '', 'i')

#

import threading

tcl_lock = threading.Semaphore ()

ENTER_TCL = tcl_lock.acquire
LEAVE_TCL = tcl_lock.release

del tcl_lock, threading

class LOCKED_TCL:
    def __context__ (self):
	return self
    def __enter__ (self):
	ENTER_TCL ()
    def __exit__ (self, *args):
	LEAVE_TCL ()

LOCKED_TCL = LOCKED_TCL ()

#
# threaded Tcl.  In *my* linux system Tcl is not threaded.
# 


class TclError:
    def __init__ (self, msg=''):
	if msg:
	    print msg
	self.msg = msg

clientDataDict = {}
BooleanType = 0
errorInCmd = False

class TkappType:
    def __init__ (self, screenName, baseName, className, interactive,
		  wantobjects, wantTk, sync, use):
	self.interp = Tcl_CreateInterp ()
	self._wantobjects = wantobjects
	if Tcl_GetVar2Ex (self.interp, "tcl_platform", "threaded", TCL_GLOBAL_ONLY) != 0:
	    print "Sorry. Your tcl interpreter appears to be threaded. Aborten"
	    raise TclError
	self.thread_id = Tcl_GetCurrentThread ()
	self.dispatching = 0

	global BooleanType, ByteArrayType, DoubleType, IntType, ListType, ProcBodyType, StringType
	if not BooleanType:
	    BooleanType = Tcl_GetObjType ("boolean")
	    ByteArrayType = Tcl_GetObjType ("bytearray")
	    DoubleType = Tcl_GetObjType ("double")
	    IntType = Tcl_GetObjType ("int")
	    ListType = Tcl_GetObjType ("list")
	    ProcBodyType = Tcl_GetObjType ("procbody")
	    StringType = Tcl_GetObjType ("string")

	Tcl_DeleteCommand (self.interp, "exit")
	if screenName:
	    Tcl_SetVar2 (self.interp, "env", "DISPLAY", screenName, TCL_GLOBAL_ONLY)
	Tcl_SetVar (self.interp, "tcl_interactive", interactive and "1" or "0", TCL_GLOBAL_ONLY)

	# this must be Tcl_Alloc()'d ?
	Tcl_SetVar (self.interp, "argv0", className.lower (), TCL_GLOBAL_ONLY)

	if not wantTk:
	    Tcl_SetVar (self.interp, "_tkinter_skip_tk_init", "1", TCL_GLOBAL_ONLY)

	if sync or use:
	    if sync and use:
		cmd = '-sync -use %s' % use
	    elif sync:
		cmd = '-sync'
	    else:
		cmd = '-use %s' % use
	    Tcl_SetVar (self.interp, "argv", cmd, TCL_GLOBAL_ONLY)

	self.Tcl_AppInit (wantTk)
	###EnableEventHook ()

    def wantobjects (self):
	return self._wantobjects

    def call (self, *args):

	args = CallArgs (args)
	ENTER_TCL ()
	i = Tcl_EvalObjv (self.interp, len (args), args, TCL_EVAL_DIRECT)    # blocking
	try:
	    if i == TCL_ERROR:
		print self.CallResult ()
		raise TclError
	    else:
		return self.CallResult ()
	finally:
	    LEAVE_TCL ()
	    Dealloc_Args (args)

    def getboolean (self, s):
	return pyTcl_GetBoolean (self.interp, s)

    def getint (self, s):
	return pyTcl_GetInt (self.interp, s)

    def setvar (self, *args):
	self.setvar_common (args, TCL_LEAVE_ERR_MSG)

    def globalsetvar (self, *args):
	self.setvar_common (args, TCL_LEAVE_ERR_MSG|TCL_GLOBAL_ONLY)

    def getvar (self, name1, name2=None):
	return self.getvar_common (name1, name2, TCL_LEAVE_ERR_MSG)

    def globalgetvar (self, name1, name2=None):
	return self.getvar_common (name1, name2, TCL_LEAVE_ERR_MSG|TCL_GLOBAL_ONLY)

    def createcommand (self, cmdName, func):
	if not callable (func):
	    raise TclError

	clientData = self, cmdName, func
	clientDataDict [id (clientData)] = clientData

	with LOCKED_TCL:
	    if Tcl_CreateCommand (self.interp, cmdName, PythonCmdCB.fptr (),
		  id (clientData), PythonCmdDeleteCB.fptr ()) == TCL_ERROR:
		raise TclError

    def deletecommand (self, cmdName):
	with LOCKED_TCL:
	    if Tcl_DeleteCommand (self.interp, cmdName) == -1:
		raise TclError

    def quit (self):
	self.quitMainLoop = 1

    def splitlist (self, arg):
	if type (arg) is tuple:
	    return arg
	return pyTcl_SplitList (self.interp, arg)

    def mainloop (self, threshold=0):
	self.quitMainLoop = 0
	while not self.quitMainLoop and not errorInCmd:
	    if self.wantTk and Tk_GetNumMainWindows () <= threshold:
		break
	    if Tcl_DoOneEvent (0) < 0:
		break
	print self.quitMainLoop, errorInCmd, "Leave tcl.mainloop"

    # prive

    def getvar_common (self, name1, name2, flags):
	name1 = varname_converter (name1)
	with LOCKED_TCL:
	    return self.TclObjAsPythonObj (Tcl_GetVar2Ex (self.interp, name1, name2, flags))

    def setvar_common (self, args, flags):
	if len (args) == 2:
	    name1, newValue = args
	    name1 = varname_converter (name1)
	    newValue = PythonObjAsTclObj (newValue)
	    with LOCKED_TCL:
		if not Tcl_SetVar2Ex (self.interp, name1, 0, newValue, flags):
		    raise TclError
	else:
	    raise NotImplemented ("setvar name1, name2, value")

    def CallResult (self):
	if self._wantobjects:
	    value = Tcl_GetObjResult (self.interp)
	    Tcl_IncrRefCount (value)
	    res = self.TclObjAsPythonObj (value)
	    Tcl_DecrRefCount (value)
	    return res
	raise NotImplemented ("dontwantobjects")

    def Tcl_AppInit (self, wantTk):
	self.wantTk = wantTk
	if Tcl_Init (self.interp) == TCL_ERROR:
	    raise TclError
	if not wantTk:
	    return
	dynload_Tk ()
	if Tk_Init (self.interp) == TCL_ERROR:
	    raise TclError (self.CallResult ())
	main_window = Tk_MainWindow (self.interp)

class PyTclObject(object):
    def __init__ (self, arg):
	self.value = arg
	if arg:
	    Tcl_IncrRefCount (arg)

    def __str__ (self):
	return self.string

    def gstring (self):
	# tkinter.c comment: python stops at 0x80
	r = self.__dict__ ['string'] = pyTcl_GetString (self.value)
	return r

    string = property (gstring)

    def __repr__ (self):
	return "tcl object"
    def __cmp__ (self, other):
	return cmp (self.string, other.string) ##pyTcl_GetString (other.value))
    def __del__ (self):
	if self.value:
	    Tcl_DecrRefCount (self.value)

#
# Python-as-Tcl
#
# returns an integer which really is a pointer to a Tcl_Obj
#
def PythonObjAsTclObj (value):
    # can use a dict with lamdas
    if type (value) is str:
	return Tcl_NewStringObj (value, len (value))
    if type (value) is bool:
	return Tcl_NewBooleanObj (value and 1 or 0)
    if type (value) is int:
	return Tcl_NewLongObj (value)
    if type (value) is float:
	return Tcl_NewDoubleObj (value)
    if type (value) is tuple:
	objv = [PythonObjAsTclObj (i) for i in value]
	return Tcl_NewListObj (len (objv), objv)
    if isinstance (value, PyTclObject):
	Tcl_IncrRefCount (value.value)
	return value.value
    try:
        return PythonObjAsTclObj (str (value))
    except:
	print value
	return PythonObjAsTclObj ("object without __str__")

#
# Tcl-as-Python
#
# returns a python object which corresponds to the tcl object
# or falls through to PyTclObject which wraps a non-primitive
# tcl type to a python class instance
#
def TclObjAsPythonObj (self, tclobj):
    t = Tcl_typePtr (tclobj)
    if not t:
	return Tcl_NULLValue (tclobj)
    if t == BooleanType:
	return bool (Tcl_longValue (tclobj))
    if t == IntType:
	return Tcl_longValue (tclobj)
    if t == DoubleType:
	return Tcl_doubleValue (tclobj)
    if t == ByteArrayType:
	return pyTcl_GetByteArrayFromObj (tclobj)
    if t == StringType:
	return pyTcl_GetStringFromObj (tclobj)
    if t == ListType:
	lengthPtr = arrayPtr (1)
	if Tcl_ListObjLength (self.interp, tclobj, lengthPtr) == TCL_ERROR:
	    raise TclError
	L = []
	for i in xrange (lengthPtr [0]):
	    L.append (self.TclObjAsPythonObj (pyTcl_ListObjIndex (self.interp, tclobj, i)))
	return tuple (L)
    return PyTclObject (tclobj)

TkappType.TclObjAsPythonObj = TclObjAsPythonObj

def CallArgs (args):
    if len (args) == 1 and type (args [0]) is tuple:
	# can't figure out
	args = args [0]
    R = []
    for i in args:
	if i is None:
	    break
	i = PythonObjAsTclObj (i)
	Tcl_IncrRefCount (i)
	R.append (i)
    return R

def Dealloc_Args (args):
    for i in args:
	Tcl_DecrRefCount (i)

# utf-8?
def varname_converter (var):
    if type (var) is str:
	return var
    if isinstance (var, PyTclObject):
	return var.string ()
    # should raise?

#
# PythonCmd callbacks
#

def PythonCmd (clientData, interp, argc, argv):
    self, cmdName, func = clientDataDict [clientData]
    args = [CStringToPyString (i) for i in GetArgv (argc, argv)]
    try:
	Tcl_SetResult (self.interp, str (func (*args)), TCL_VOLATILE)
	return TCL_OK
    except:
	global errorInCmd
	errorInCmd = 1
	return TCL_ERROR

def _PythonCmd (clientData, interp, argc, argv):
    LEAVE_TCL ()
    r = PythonCmd (clientData, interp, argc, argv)
    ENTER_TCL ()
    return r

def PythonCmdDelete (clientData):
    del clientDataDict [clientData]
    return TCL_OK

PythonCmdCB = DLL.Callback (('i', 'iiii'))
PythonCmdCB.set_callback (_PythonCmd)
PythonCmdDeleteCB = DLL.Callback (('i', 'i'))
PythonCmdDeleteCB.set_callback (PythonCmdDelete)

#
# public functions
#

def create (screenName, baseName, className, interactive,
	    wantobjects, wantTk, sync, use):
    return TkappType (screenName, baseName, className,
		      interactive, wantobjects, wantTk,
		      sync, use)

def flatten(tup):
    elts = []
    for elt in tup:
        if type(elt) in (tuple, list):
            elts = elts + flatten(elt)
        else:
            elts.append(elt)
    return elts

#
# constants
#

READABLE	= 2
WRITABLE	= 4
EXCEPTION	= 8
TK_VERSION	= '8.4'
TCL_VERSION	= '8.4'

TCL_DONT_WAIT	=	1<<1
TCL_WINDOW_EVENTS=	1<<2
TCL_FILE_EVENTS	=	1<<3
TCL_TIMER_EVENTS=	1<<4
TCL_IDLE_EVENTS	=	1<<5	### WAS 0x10 ????
TCL_ALL_EVENTS	=	~1

###########################
TCL_GLOBAL_ONLY = 1
TCL_OK = 0
TCL_VOLATILE = 1
TCL_ERROR = 1
TCL_LEAVE_ERR_MSG = 0x200

#
TCL_NO_EVAL	=	0x10000
TCL_EVAL_GLOBAL	=	0x20000
TCL_EVAL_DIRECT	=	0x40000
TCL_EVAL_INVOKE	=       0x80000

#
# low level Tcl JITs
#

from array import array
arrayPtr = lambda n: array ('i', n * [0])

TCLJIT = r"""
	#if 0
	/* This depends on tcl.h but all we really need is the Tcl_Obj
	 * structure.  We could reproduce this here to avoid the dependancy
	 */
	#include <tcl.h>
	#else
	/* Here it is! */
	typedef struct Tcl_ObjType Tcl_ObjType;
	typedef struct Tcl_Obj {
	    int refCount;
	    char *bytes;
	    int length;	
	    struct Tcl_ObjType *typePtr;
	    union {
		long longValue;
		double doubleValue;
		void *otherValuePtr;
		//Tcl_WideInt wideValue;
		struct {
		    void *ptr1;
		    void *ptr2;
		} twoPtrValue;
	    } internalRep;
	} Tcl_Obj;
	#   define Tcl_IncrRefCount(objPtr) \
		++(objPtr)->refCount
	#   define Tcl_DecrRefCount(objPtr) \
		if (--(objPtr)->refCount <= 0) TclFreeObj(objPtr)
	#endif

	/* return the typePtr */
	Tcl_ObjType *typePtr (Tcl_Obj *T)
	{
		return T->typePtr;
	}

	/* return longValue */
	int longValue (Tcl_Obj *T)
	{
		return T->internalRep.longValue;
	}

	/* return doubleValue */
	double doubleValue (Tcl_Obj *T)
	{
		return T->internalRep.doubleValue;
	}

	/* length */
	int tclobj_length (Tcl_Obj *T)
	{
		return T->length;
	}

	/* bytes */
	char *tclobj_bytes (Tcl_Obj *T)
	{
		return T->bytes;
	}

	/* these are macros */
	void incref (Tcl_Obj *T)
	{
		Tcl_IncrRefCount (T);
	}
	void decref (Tcl_Obj *T)
	{
		Tcl_DecrRefCount (T);
	}
"""

jits = DLL.CachedLib ('tcljit', TCLJIT, ['-O2', '-l' + libtcl])

Memcpy = DLL.Memcpy
MemcpyInts = DLL.MemcpyInts
Tcl_typePtr = jits.get (('i', 'typePtr', 'i'))
Tcl_longValue = jits.get (('i', 'longValue', 'i'))
Tcl_doubleValue = jits.get (('d', 'doubleValue', 'i'))
Tcl_length = jits.get (('i', 'tclobj_length', 'i'))
Tcl_bytes = jits.get (('i', 'tclobj_bytes', 'i'))
Tcl_IncrRefCount = jits.get (('', 'incref', 'i'))
Tcl_DecrRefCount = jits.get (('', 'decref', 'i'))

CStringToPyString = DLL.CStringToPyString

def GetArgv (argc, argv):
    ret = arrayPtr (argc)
    MemcpyInts (ret, argv, argc)
    #xxx
    rr = []
    for i in range (len (ret)):
	rr.append (ret [i])
    return rr [1:]

##    return ret

def Tcl_NULLValue (value):
    return Memcpy (Tcl_bytes (value), Tcl_length (value))

def pyTcl_GetString (obj):
    return CStringToPyString (Tcl_GetString (obj))

def pyTcl_GetBoolean (interp, obj):
    if obj in (True, False):
	return obj
    boolPtr = arrayPtr (1)
    Tcl_GetBoolean (interp, obj, boolPtr)
    return bool (boolPtr [0])

def pyTcl_GetInt (interp, obj):
    intPtr = arrayPtr (1)
    Tcl_GetInt (interp, obj, intPtr)
    return intPtr [0]

def pyTcl_GetByteArrayFromObj (obj):
    lengthPtr = arrayPtr (1)
    ret = Tcl_GetByteArrayFromObj (obj, lengthPtr)
    n = lengthPtr [0]
    return Memcpy (ret, n)

def pyTcl_GetStringFromObj (obj):
    lengthPtr = arrayPtr (1)
    cptr = Tcl_GetStringFromObj (obj, lengthPtr)
    length = lengthPtr [0]
    return Memcpy (cptr, length)

def pyTcl_ListObjIndex (interp, value, i):
    objPtr = arrayPtr (1)
    if Tcl_ListObjIndex (interp, value, i, objPtr) == TCL_ERROR:
	raise TclError
    return objPtr [0]

def pyTcl_SplitList (interp, lst):
    # Tcl_SplitList returns the number of elements in argcPtr and it allocates
    # an array which must be freed with Tcl_Free and is returned in argvPtr
    argcPtr = arrayPtr (1)
    argvPtr = arrayPtr (1)
    if Tcl_SplitList (interp, lst, argcPtr, argvPtr) == TCL_ERROR:
	whereami ()
	raise TclError
    argc, argv = argcPtr [0], argvPtr [0]
    ret = arrayPtr (argc)
    MemcpyInts (ret, argv, argc)
    Tcl_Free (argv)
    return tuple ([DLL.CStringToPyString (x) for x in ret])
