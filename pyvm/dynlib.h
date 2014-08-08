/*
 * pyvm global header file
 *
 * This should be used to connect the various builtin modules/files
 * but it's not the right file for the C API of pyvm
 *
 */

#define MAGIC (62061 | ((long)'\r'<<16) | ((long)'\n'<<24))
#define MAGIC23 (62011 | ((long)'\r'<<16) | ((long)'\n'<<24))
#define MAGIC_PYVM (62054 | ((long)'\r'<<16) | ((long)'\n'<<24))	/* unused */

/* tracebacks */
#define TRACEBACK_LEVEL 1

#include "oputil.h"
#include "seg-malloc.h"
#include "z-alloc.h.c+"
#include "inits.h"
#include "filedes.h"

#define ZLNOTAB		/* lnotab compression */

/* debug parameters */

//#define DEBUG_RELEASE
//#define DEBUG_GC
//#define DEBUG_GC_TRV
//#define HAVE_TYPEID

//
// on operator overloading, we can either preempt_pyvm or raise CONTEXT_SWITCH
// and avoid the preemption altogether. This macro specifies what to do
// xxx: broken in some places. we can investigate if we decide that we want
// to avoid too much preemption.
//
#define RAISE_CONTEXTS 0

//
// use the vmpoll code for true light threads
//
#define USE_VMPOLL 1
#define CAN_VMPOLL USE_VMPOLL && multitasking && !RC->preemptive

/* typenames */

extern const char NoneType[], IntType[], TypeType[], BoolType[], StringType[],
		  IteratorType[], TupleType[], ListType[], DictType[], NamespaceType[],
		  PyCodeType[], PyFuncType[], ClassType[], BoundType[], InstanceType[],
		  BugType[], ArrayType[], PropertyType[], BuiltinFuncType[], cStringIOType[];

/* need forward declarations of these due to annoying lwc bug */

class REFPTR;
class TypeObj;
struct dictEntry;
class dictionary;
class DictObj;
class ListObj;
class TupleObj;
class Tuplen;
class StringObj;
class IntObj;
class FloatObj;
class NamespaceObj;
class DynClassObj;
class DynInstanceObj;
class DynMethodObj;
struct block_data;
struct exec_stack;
struct vm_context;
class PyCodeObj;
class PyFuncObj;
class exec_stack;
struct SetObj;
struct bltinfunc;
struct method_attribute;

/* type objects, used in virtual variable */

extern TypeObj NoneTypeObj, IntTypeObj, FloatTypeObj, StringTypeObj, TupleTypeObj,
               ListTypeObj, DictTypeObj, IteratorTypeObj, NamespaceTypeObj, BuiltinFuncTypeObj,
	       PyCodeTypeObj, TypeTypeObj, BugTypeObj, PyFuncTypeObj, ClassTypeObj, InstanceTypeObj,
	       BoolTypeObj, BoundTypeObj, ArrayTypeObj, SetTypeObj, PropertyTypeObj;

extern DictObj NOMETHODS;

benum OBJECT_FLAGS {
	/* object flags */
	VF_NONE,
	VF_ISEQ,
	VF_ITER,
	VF_ATTR,
	VF_FUNPACK,
	VF_TUPLEOBJ,		// tuple() or list()
	VF_INTEGER,		// int or double
	VF_FLOAT,
	VF_NUMERIC,
	VF_VMEXEC,		// call is bytecode
	VF_CALLABLE,		// used by instance.getattr to inject self
	VF_CLSMETH,		// irregular
	VF_DESCR,		// descriptor
	VF_TRAVERSABLE,
	VF_PERMANENT,
	VF_NO_GC_BREAK
};

/* ---* master object *--- */

class __object__
{
	const virtual;

	/* These virtual variables are common for all instances of a class */
#ifdef	HAVE_TYPEID
	virtual	const char *const typeid;
#endif
	virtual	const char *const stype = BugType;
	virtual	const TypeObj &type = &BugTypeObj;
	virtual	const unsigned int vf_flags = 0;
	virtual DictObj *type_methods = &NOMETHODS;

	unsigned long refcnt;

	static inline void inf ()		{ refcnt = $LONG_MAX; }
	bool cmp_EQ_same (__object__ *s)	{ return s == this; }
	int cmp_GEN_same (__object__ *s)	{ return s - this; }

	/* Type downcasting, with/without checks.
	   These functions are 'modular' which means that they don't have "this"
	   and we can call __object__.func().  Moreover, they are 'auto' which
	   means that they are redefined in every derrived class to use the object's
	   parameters as constants  */

inlines	automod	void enforcetype (__object__ *o)	{ if_unlikely (stype != o->stype)
							  RaiseTypeError (stype, o->stype); }
inlines	automod	void fenforcetype (__object__ *o)	{ if_unlikely (!isinstance (o))
							  RaiseTypeError (stype, o->stype); }
inlines	automod	bool typecheck (__object__ *o)		{ return stype == o->stype; }
inlines	automod	_CLASS_ *checkedcast (__object__ *o)	{ enforcetype (o); return (_CLASS_*) o; }
inlines	automod	_CLASS_ *fcheckedcast (__object__ *o)	{ fenforcetype (o); return (_CLASS_*) o; }
inlines	automod _CLASS_ *cast (__object__ *o)		{ return (_CLASS_*) o; }
inlines	automod	bool isinstance (__object__ o)		{ return o._v_p_t_r_ == _CLASS_._v_p_t_r_; }
	bool Isinstance (__object__ *o)			{ return stype == o->stype; }

	/* internal */
	virtual	__object__ *__xgetitem__ (int) const;
	virtual int __find_in (REFPTR*, int);
	static inline double todouble ();
	static inline double todouble_nocheck ();
modular	virtual __object__ *type_call (REFPTR*, int);

   public:

	__object__ ()			{ refcnt = 0; }
	void __noinit ()		{ }

	/* ----* common methods *---- */

	/* 'print' is the only pure virtual function.  No virtual table is emited
	   for classes that don't declare a non-pure print method.  */
	virtual	void print () = 0;
	virtual	void xprint ();
	virtual	long hash ();
auto	virtual	bool cmp_EQ (__object__ *s)	{ return stype == s->stype ? cmp_EQ_same (s) : 0; }
auto	virtual	int cmp_GEN (__object__ *s)	{ return stype - s->stype ?: cmp_GEN_same (s); }
	virtual	int len ();
	virtual	StringObj *str ();
	virtual StringObj *repr ();

	/* ----* common attributes *---- */
	virtual	__object__ *iter ();
	virtual	__object__ *xnext ();
static inline
auto	virtual __object__ *next () alias (xnext);

	virtual	bool Bool ();
	virtual	bool contains (__object__*);
	virtual	__object__ *xgetitem (__object__*);
	virtual	void xdelitem (__object__*);
	virtual	__object__ *xgetslice (int, int);
	virtual	void xdelslice (int, int);
	virtual	void xsetitem (__object__*, __object__*);
	virtual	void xsetslice (int, int, __object__*);
	virtual	bool hasattr (__object__*);
	virtual	void setattr (__object__*, __object__*);
	virtual	void delattr (__object__*);
	virtual	__object__ *getattr (__object__*);
	__object__ *get_type_method (__object__*);

	/* Some notes on call().  The first argument is the REFPTR that shall hold the
	   return result.  The second is the &argv [-1].  So argv[0] usually == retval.
	   The third is argc without counting the first argv[0].  That's rather weird
	   but it has to do with something inside the vm.  */
	virtual	void call (REFPTR, REFPTR*, int);

	/* ----* common operatorships *---- */
	virtual	__object__ *binary_multiply (__object__*);
	virtual	__object__ *binary_modulo   (__object__*);
	virtual	__object__ *binary_add      (__object__*);
	virtual	__object__ *binary_sub      (__object__*);
	virtual	__object__ *binary_and      (__object__*);
	virtual	__object__ *binary_xor      (__object__*);
	virtual	__object__ *binary_or       (__object__*);
	virtual	__object__ *concat	    (__object__*);

	virtual __object__ *inplace_sub		(__object__*);

	/* the reference counter calls __release and never "delete object" */
	virtual	void __release () { }
	virtual	~__object__ ();
};

/* ---* useful essential base classes *--- */

class __destructible__ : __object__
{
	// when release invokes delete. Since this is an auto-function the call to
	// the destructor is not virtual so not only we avoid two virtual calls but
	// also manage to have overloaded new/delete and also call the custom deleter.

auto	virtual void __release () { delete *this; }
};

class __container__ : __destructible__
{
	// Objects which contain other object and therefore in the GC list

	const unsigned int vf_flags |= VF_TRAVERSABLE;
	__container__ *next, *prev;
	int sticky;
virtual	trv void traverse ()	{ }
virtual	trv void __clean ();

   public:
	__container__ ();
	~__container__ ();
	void GC_ROOT ();
};

benum { STICKY_TRAVERSE, STICKY_PRINT, STICKY_CIRCULAR };

__unwind__
static inline class sticky_set
{
	// for some recursive operations on __container__ we use the 'sticky' member
	// to protect from infinite recursion.  This setter will clear the sticky even
	// in the case of an exception (longjmp).
	__container__ *C;
   public:
	sticky_set (__container__ *c = (__container__*) this)	{ (C = c)->sticky |= STICKY_PRINT; }
	~sticky_set ()						{ C->sticky &= ~STICKY_PRINT; }
};

extern void GC_collect (REFPTR);
extern void weakref_collect ();

template class norelease {
slow	void __release ()	{ inf (); }
};

class __permanent__ : __object__, norelease
{
	// permanent object.  When __release is called it sets the refcnt to LONG_MAX

	const unsigned int vf_flags |= VF_PERMANENT;
   public:
	__permanent__ ();
	bool cmp_EQ (__object__ *o)	{ return o == this; }
};

class __permanent_container__ : __container__, norelease
{
	const unsigned int vf_flags |= VF_PERMANENT;
   public:
	__permanent_container__ ()	{ __container__.ctor (); }
};

/* template macro classes */

template class seg_allocd {
	// Overload "new" and "delete" to use the segment allocator
	// --- not all objects have lots of instances!! some have *very* few actually!!
	_CLASS_ *operator new ()
	{
		switch (sizeof (_CLASS_)) {
			case 56: return seg_alloc56();
			case 20:
			case 24: return seg_alloc24();
			case 28:
			case 32: return seg_alloc32();
			default: return seg_alloc (sizeof (_CLASS_));
		}
	}
	void operator delete ()		{ seg_freeXX (this); }
};

template class direct__find {
	// Find an object in a list. Avoids virtual comparison costs
	// This template class can be used for some objects to override the
	// default __find_in which uses virtual comparison
	static inline int __object__.__find_in (REFPTR arr[], int l)
	{
		for (int i = 0; i < l; i++)
			if ((*this).cmp_EQ (arr [i].o))
				return i;
		return -1;
	}
};

/* REFPTR.  The reference counter class */

static
__unwind__
inline class REFPTR
{
	union {
		__object__ *o;
		__container__ *c;

		/* these are possible because of same offset */
		DictObj		*as_dict;
		SetObj		*as_set;
		ListObj		*as_list;
		TupleObj	*as_tuple;
		Tuplen		*as_tuplen;
		StringObj	*as_string;
		IntObj		*as_int;
		FloatObj	*as_double;
		NamespaceObj	*as_ns;
		DynClassObj	*as_class;
		DynInstanceObj	*as_inst;
		DynMethodObj	*as_meth;
		PyFuncObj	*as_func;
		PyCodeObj	*as_code;
	};
	void __swap (REFPTR);
   public:
	REFPTR (__object__*) nothrow INLINE;
	REFPTR () nothrow INLINE;
	void uninitialized ()	{ }
	void __copyctor (__object__ *x)	{ o = x; }
	void __movector (REFPTR F)	{ o = F.preserve (); }
trv	void traverse_ref ();
	void operator ~ ()			{ ctor (); }
	__object__ *operator -> ()		{ return o; }
	void operator = (__object__*);
	void __copy (REFPTR x)			{ dtor (); o = x.o; }
	void __copyobj (__object__ *x)		{ dtor (); o = x; }
	void __move (REFPTR x)			{ dtor (); o = x.preserve (); }
	void null ()				{ dtor (); o = 0; }
	void setNone ()				{ dtor (); o = &None; }
	void incref ()				{ ++o->refcnt; }
	__object__ *decref ()			{ --o->refcnt; return o; }

	/* In pyvm, functions do not return ownership of reference.  If we have a local
	   REFPTR and we want to return its object, we have to "preserve" it with the
	   two functions below.  */
	/* preserve objects from REFPTR destruction */
		/* preserve and move the reference */
	__object__ *preserve ()			{ return postfix (o, ctor ()); }
		/* preserve and decref */
	__object__ *Dpreserve ()		{ --o->refcnt; return preserve (); }

	/* Sometimes, if we know the type of the object in the refptr we can
	   ask for custom destruction (may make a difference)  */
	void strdtor ();
	void ctordtorstr (__object__ *o)	{ strdtor (); ctor (o); }
	void intdtor ();
	void ctordtorint (__object__ *o)	{ intdtor (); ctor (o); }
	void fltdtor ();
	void ctordtorflt (__object__ *o)	{ fltdtor (); ctor (o); }
	~REFPTR () nothrow;
};

// all of REFPTR methods are static inline
#include "REFPTR-inlines.h"

/* exceptions */

enum INTERRUPT
{
	/* these are the builtin longjmp/setjmp "exceptions", not to be confused with
	   the bytecode exceptions.  We'll refer to them as "interrupts" because pyvm
	   resembles a chip.  Generally, this is a good time to explain that unlike
	   CPython, pyvm uses longjmp (lwc's "throw") in case of errors.  REFPTRs are
	   destructed normally as all local objects  */
	NO_ATTRIBUTE, TYPE_ERROR, INDEX_ERROR, KEY_ERROR, TUPLE_UNPACK, NOT_IMPLEMENTED,
	IO_ERROR, VALUE_ERROR, NAME_ERROR, OS_ERROR, RUNTIME_ERROR, IMPORT_ERROR,
	SYSTEM_EXIT, EOF_ERROR, FPE_ERROR,
	RE_RAISE,
	STOP_ITERATION,
	CONTEXT_SWITCH
};

static inline class Interrupt
{
	// lwc's throw returns a void* pointer.  We really return such a class.
	// there is no reason to make this an object and mix it with Exception object
	
	INTERRUPT id;
	REFPTR obj;
	__object__ *pyexc;
   public:
	Interrupt (INTERRUPT I)			{ id = I; obj.ctor (); }

	__object__ *interrupt2exception ()	{ return pyexc; }
};

/* all these throw (longjmp) and thus are noreturn */
__object__ *RaiseStopIteration () noreturn;
__object__ *RaiseNoAttribute (__object__*) noreturn;
__object__ *RaiseNameError (__object__*) noreturn;
__object__ *RaiseImportError (__object__*) noreturn;
__object__ *RaiseKeyError () noreturn;
__object__ *RaiseKeyError (__object__*) noreturn;
__object__ *ReRaise () noreturn;
__object__ *RaiseIoError () noreturn;
__object__ *RaiseRuntimeError (char*) noreturn;
__object__ *RaiseTypeError (const char*, const char*) noreturn;
__object__ *RaiseTypeError (const char*) noreturn;
__object__ *RaiseNotImplemented (const char*) noreturn;
__object__ *RaiseIndexError () noreturn;
__object__ *RaiseListIndexOutOfRange () noreturn;
__object__ *RaiseTooManyArgs () noreturn;
__object__ *RaiseTooFewArgs () noreturn;
__object__ *RaiseValueError (const char*) noreturn;
__object__ *RaiseValueError_li () noreturn;
__object__ *RaiseSystemExit (__object__*) noreturn;
__object__ *RaiseFPE () noreturn;

/* ---* special objects *--- */

final class NoneObj : __permanent__, direct__find
{
	/* singleton */
	const char *const stype = NoneType;
	const TypeObj &type = &NoneTypeObj;
   public:
	NoneObj ()			{ __permanent__.ctor (); }
	long hash ();
	bool Bool ();
	bool cmp_EQ (__object__ *o)	{ return o == this; }
	StringObj *str ();
	void print ();
};

extern NoneObj None;

final class TypeObj : __permanent__
{
	const char *const stype = TypeType;
	const TypeObj &type = &TypeTypeObj;

	const void * typeptr;
	/* dirty lwc hack to access virtuals from a _v_p_t_r_ pointer -- non standard */
#define	TYPE2VPTR(X) ((__object__*)&X)
	__object__ *type_call (REFPTR*, int);
   public:
	TypeObj (const void*);
	void call (REFPTR, REFPTR[], int);
	bool Bool ()			{ return true; }
	__object__ *getattr (__object__*);
	void print ();
	StringObj *str ();
};

final class BoolObj : __permanent__, direct__find
{
	/* doubleton */
	const char *const stype = BoolType;
	const TypeObj &type = &BoolTypeObj;
	const unsigned int vf_flags |= VF_INTEGER;	// XXX: |VF_NUMERIC ?
	int i;		/* HACK. We can cast a BoolObj to intobj */
   public:
	BoolObj ();
	bool Bool ()			{ return this == &TrueObj; }
	bool cmp_EQ (__object__ *o)	{ return o == this; }
	void print ();
};

extern BoolObj TrueObj, FalseObj;

/* ----* numerics *---- */

#if 0
class NumericObj : __object__
{
slow	__object__ *binary_multiply (__object__*);
slow	__object__ *binary_add (__object__*);
slow	__object__ *binary_sub (__object__*);
};
#endif

final class IntObj : /*NumericObj*/__object__, personal_allocator, direct__find
{
	const char *const stype = IntType;
	const TypeObj &type = &IntTypeObj;
	const unsigned int vf_flags |= VF_INTEGER|VF_NUMERIC;

	void fenforcetype (__object__ *o)	{ if_unlikely (!isinstance (o))
							if_unlikely (!BoolObj.isinstance (o))
								RaiseTypeError (stype, o->stype);
						}
	bool permanent ();
	void make (int);
	union {
		long i;
		IntObj *fnext;
	};
	__object__ *type_call (REFPTR[], int);
   public:

	IntObj (long);
	bool Bool ()			{ return i; }
	long hash ()	{ return i; }
	int cmp_GEN (__object__*);
	bool cmp_EQ (__object__ *o)	{ return IntObj.isinstance (o) ? i == IntObj.cast (o)->i :
					  FloatObj.isinstance (o) ?
					  (double) i == FloatObj.cast (o)->f : 0; }
slow	__object__ *binary_multiply (__object__*);
slow	__object__ *binary_add (__object__*);
//slow	__object__ *binary_sub (__object__*);
	void print ();
slow	StringObj *str ();
	void __release ();
};

extern IntObj *newIntObj (int);

extern IntObj *IntObj_0, *IntObj_1;

final class FloatObj : /*NumericObj*/__object__, personal_allocator, direct__find
{
	const char *const stype = IntType + 4;
	const TypeObj &type = &FloatTypeObj;
	const unsigned int vf_flags |= VF_FLOAT|VF_NUMERIC;

	union {
		double f;
		FloatObj *fnext;
	};
	bool cmp_EQ_same (__object__ *o)	{ return ((FloatObj*) o)->f == f; }
	int cmp_GEN_same (__object__*);
	__object__ *type_call (REFPTR[], int);
   public:

	FloatObj (double);
	bool Bool ()			{ return f != 0.0; }
	int cmp_GEN (__object__*);
	long hash ()			{ return (long) f; }
	__object__ *binary_modulo (__object__*);
	void print ();
slow	StringObj *str ();
	void __release ();
};

/* ----* some bases *---- */

template class wnext
{
	// the default behavior of 'next' is to be an alias for 'xnext'.
	// use this template class to override next to preempt pyvm in the case
	// xnext may return a context switch
	__object__ *next ()
	{
		__object__ *r = xnext ();
		return r != &CtxSw ? r : preempt_pyvm (CtxSw.vm);
	}
};

class iteratorBase : __container__
{
	const char *const stype = IteratorType;
	const TypeObj &type = &IteratorTypeObj;
	const unsigned int vf_flags |= VF_ITER;

	REFPTR obj;
   public:
	iteratorBase (__object__*);
	int len	()		{ return -1; }
	__object__ *iter ()	{ return this; }
	__object__ *getattr (__object__*);
	__object__ *to_list ();
virtual	void unyield ();
	bool Bool ()			{ return true; }
	void print ();
	void trv traverse ();
};

/* -----* sequence bases *----- */

template class lenseqObj {
	const unsigned int vf_flags |= VF_ISEQ;

	int len;
	int len ()	{ return len; }
#ifdef	PYVM_CORE
inlines	int abs_index (int);
#endif
inlines	int absl_index (int i)
	{
		if (i < 0) {
			if_unlikely ((i += len) < 0) i = 0;
		} else if (i > len) i = len;
		return i;
	}
virtual	__object__ *__xgetitem__ (int) const	{ RaiseNoAttribute (Interns.__getitem__); }
static inline
autovrt	__object__ *xgetitem (int);
	__object__ *xgetitem (__object__*);
virtual	__object__ *__xgetslice__ (int, int)	{ RaiseNoAttribute (Interns.__getslice__); }
	__object__ *xgetslice (int, int);
};

template class mutableseqObj
{
	void xsetitem (int, __object__*);
	void xsetitem (__object__*, __object__*);
	void xdelitem (int);
	void xdelitem (__object__*);
	void xdelslice (int, int);
	void xsetslice (int, int, __object__*);
};

class container_sequence : __container__, lenseqObj {
	int cmp_GEN_same (__object__*);
};

class basic_sequence : __destructible__, lenseqObj
{ };

/* ----* array *---- */

extern __object__ *list_to_array (int, TupleObj*);
extern __object__ *array_to_list (__object__*);
extern bool is_array (__object__*);

// at "arrayobj.h"

/* ----* string *---- */

extern DictObj StringMethods;

final class StringObj : basic_sequence, personal_allocator, direct__find
{
	const char *const stype = StringType;
	const TypeObj &type = &StringTypeObj;
	DictObj *type_methods = &StringMethods;

	char *str;
	union {
		long phash;
		StringObj *fnext;
	};

	int _strcmp (const char *s)	{ return strcmp (str, s); }
virtual	StringObj *strcat (const char*, int);
	StringObj *strcat (const char*);
	StringObj *strcat (StringObj *);

final	bool cmp_EQ_same (__object__*);
final	int cmp_GEN_same (__object__*);
inline	long mkhash ();
	__object__ *type_call (REFPTR[], int);
   public:
	StringObj (const char*, int);
	StringObj (const char*, int, const char*, int);
	void binctor (const char*, int);
	StringObj (const char*);
	void charStringObj (char);
	void intern (const char*, int, long=0);
	void allocated (char*, int);

	bool Bool ()			{ return len; }
	StringObj *str ()		{ return this; }
	bool contains (__object__*);
	StringObj *repr ();
	__object__ *concat (__object__*);
	__object__ *__xgetitem__ (int) const;
	__object__ *__xgetslice__ (int, int);
	__object__ *binary_add (__object__*);
final	__object__ *binary_modulo (__object__*);
final	__object__ *binary_multiply (__object__*);
final	long hash ();
final	void print ();
final	void xprint ();
final	__object__ *iter ();

	ListObj *to_list ();

	~StringObj ();
};

extern __object__ *char_string (unsigned int);

extern slow StringObj *new_interned (const char*);
extern __object__ *intern_string (StringObj*);
extern __object__ *intern_string2 (const char*, int);
extern bool is_intern (const StringObj*);
extern slow StringObj *new_interned (const char*, int);

extern struct _Interns {
	// some interns. Having these here is good because we can use them from C
	StringObj *__init__, *__dict__, *im_class, *im_self, *im_func, *__builtins__, *__name__;
	StringObj *SystemExit, *__iter__, *__file__, *None, *exitfunc, *globals, *sys, *__all__;
	StringObj *acquire, *release, *__main__, *__doc__, *next, *__getitem__, *__setitem__;
	StringObj *__cmp__, *__hash__, *__delitem__, *__del__, *traceback, *format_exc, *__class__;
	StringObj *__nonzero__, *__call__, *__getattr__, *__setattr__, *__bases__, *__delattr__;
	StringObj *__len__, *__str__, *__mul__, *__add__, *__mod__, *__contains__, *__getslice__;
	StringObj *__setslice__, *__delslice__, *__iadd__, *__hasattr__, *__and__, *__xor__;
	StringObj *__or__, *__sub__, *__repr__, *__module__, *x, *y, *i, *j, *pyc, *compile;
	StringObj *compileFile, *eval_ast, *func_code, *co_filename, *exec, *eval, *__eq__;
	StringObj *compileFile_internal, *type, *str, *unyield, *func_name, *__builtin__;
	StringObj *string, *co_code, *co_lnotab, *f_locals, *f_globals, *_stdout, *write, *keys;
	StringObj *func_globals, *line, *Inf;
} Interns;

/* ----* tuple *---- */

class TupleObj : container_sequence
{
	const char *const stype = TupleType;
	const TypeObj &type = &TupleTypeObj;
	const unsigned int vf_flags |= VF_FUNPACK|VF_TUPLEOBJ;
virtual	const char __print_fmt [2] = "()";

	REFPTR *data;

static	void enforcetype (__object__ *o)	{ if_unlikely (!(o->vf_flags & VF_TUPLEOBJ))
							  RaiseTypeError (stype, o->stype); }
static	bool typecheck (__object__ *o)		{ return o->vf_flags & VF_TUPLEOBJ; }
	__object__ *type_call (REFPTR[], int);
   public:
	__object__ *__xgetitem__ (int i) const	{ return data [i].o; }
	bool contains (__object__*);
	bool Bool ()				{ return len != 0; }
	__object__ *binary_multiply (__object__*);

	void unpack (REFPTR[]);
	int index (__object__*, int, int);

	ListObj *to_list ();
slow	void print ();
slow	StringObj *str ();
	void trv traverse ();
};

class Array_Base : TupleObj
{
	int cmp_GEN_same (__object__*);
auto	bool cmp_EQ_same (__object__ *o)	{ return cmp_GEN_same (o) == 0; }
inline	void __xinititem__ (int i, __object__ *o)	{ data [i].ctor (o); }
   public:
	Array_Base (__object__ *[...]);
	void refctor (REFPTR [...]);		// alternative ctor
	void mvrefctor (REFPTR*, int);		// <<
	void mvrefarray (REFPTR [...]);		// <<
	void __sizector (int);			// <<
};

#define TUPLEVIEW

extern DictObj TupleMethods;

final class Tuplen : Array_Base, seg_allocd, direct__find
{
	const unsigned int vf_flags |= VF_NO_GC_BREAK;
	DictObj *type_methods = &TupleMethods;

inline	void __xvvitem__ (int i)			{ data [i].ctor (); }
inline	void __xputitem__ (int i, __object__ *o)	{ data [i].__copyctor (o); }
inline	void __xsetitem__ (int i, __object__ *o)	{ data [i] = o; }
	int __find (__object__*);
trv	void __clean ();

   public:

	void NoneCtor (int);

#ifdef	TUPLEVIEW
	void *tview;
	Tuplen (__object__ *o[...])		{ tview = 0; Array_Base.ctor (ov, oc); }
	void viewctor (Tuplen*, REFPTR*, int);
	void refctor (REFPTR o[...])		{ tview = 0; Array_Base.refctor (ov, oc); }
	void mvrefctor (REFPTR* r, int x)	{ tview = 0; Array_Base.mvrefctor (r, x); }
	void mvrefarray (REFPTR o[...])		{ tview = 0; Array_Base.mvrefarray (ov, oc); }
	void __sizector (int x)			{ tview = 0; Array_Base.__sizector (x); }
#endif

	__object__ *iter ();
	__object__ *__xgetslice__ (int, int);
	long hash ();
	__object__ *binary_add (__object__*);
	~Tuplen ();
};

extern TupleObj *newTuple_ref (REFPTR [...]);
extern TupleObj *newTuple (__object__* [...]);
extern Tuplen *NILTuple;

/* ----* list *---- */

extern DictObj ListMethods;

final class ListObj : Array_Base, mutableseqObj, seg_allocd
{
	const char *const stype = ListType;
	const TypeObj &type = &ListTypeObj;
	const char __print_fmt [2] = "[]";
	DictObj *type_methods = &ListMethods;

	int alloc;

	void __inititem (int i, __object__ *o)	{ data [i].ctor (o); }
	void __inititem_mr (int i, REFPTR o)	{ data [i].o = o.preserve (); }

trv	void __clean ();
	__object__ *type_call (REFPTR[], int);
   public:
	ListObj (__object__ *[...]);
	void refctor (REFPTR [...]);	// alternative ctor
	void mvrefarray (REFPTR [...]);	// <<
	void __sizector (int);		// <<

	__object__ *__xgetslice__ (int, int);
	__object__ *iter ();

	__object__ *concat (__object__*);
	void __xsetitem__ (int, __object__*);
	void __xdelitem__ (int);
	void __xdelslice__ (int, int);
	void __xsetslice__ (int, int, __object__*);
	__object__ *binary_add (__object__*);

	/* ---* common list methods *--- */
	ListObj *append (__object__*);
	__object__ *pop (int);
	ListObj *reverse ();
	ListObj *remove (__object__*);
	__object__ *riter ();
	ListObj *insert (int, __object__*);
	ListObj *sort ();
	void sort_cmp (__object__*);
	Tuplen *list_to_tuple ();

	/* ---* pyvm opt *--- */
	void append_mvref (REFPTR);
	~ListObj ();
};

/* ----* dict *---- */

#define DICT_MINSIZE 8

//#define DICT_MINSIZE 4
// DICT_MINSIZE 4 gives pretty good results and in some cases better
// but pyc bootstrap is broken and some setitem operations get into
// infinite recursion (??!?)

static inline struct dictEntry
{
	long hash;
	REFPTR key, val;

#ifdef	PYVM_CORE
	void copy (dictEntry*);
#endif
};

/* self-mutating dictionary */
class dictionary
{
	virtual inline volatile;	/*-*-*-*-*-*-*/

	auto	modular void Mutate (dictionary *d) {
		/*-- dirty lwc hack to modify inlined virtual table - non standard --*/
		memcpy (&d->_v_p_t_r_, _CLASS_._v_p_t_r_, sizeof *dictionary._v_p_t_r_);
	}
	modular	bool IsType (dictionary *d) {
		return memcmp (&d->_v_p_t_r_, dictionary._v_p_t_r_, sizeof d->_v_p_t_r_) == 0;
	}

	dictEntry *tbl;
	unsigned long mask, used, fill, max, itrn;
	dictEntry smalltbl [DICT_MINSIZE];

modular	bool cmp_key_ent (dictEntry*, __object__*);
modular	long get_hash (__object__*);
	void mutateby (__object__*);
	bool type_good (__object__*) INLINE;
auto	dictEntry *_lookup (unsigned long, __object__*) const INLINE;

	void init (int);
	void test_resize ();
	void brenton (__object__*);
   public:
auto	dictionary (int i = 0)	{ init (i); _CLASS_.Mutate (this); }
	dictionary (dictionary*);

virtual	auto dictEntry *lookup (__object__*, long*);
virtual	auto dictEntry *lookup (__object__*);
virtual	auto bool contains (__object__*);
	__object__ *get (__object__*);
	void insert (__object__*, __object__*);
	void remove (__object__*);
	__object__ *setdefault (__object__*, __object__*);

	dictEntry *__iterfast (dictEntry*) const;
	void ins_vals (ListObj) const;
	void ins_keys (ListObj) const;
	void ins_itms (ListObj) const;
	trv	void traverse_dict ();
	trv	void traverse_set ();

	/* --* as weakref *-- */
	slow	void clean_weak_vals (int = 1);
	slow	void clean_weak_set ();

	/* --* as set *-- */
	void set_ctor (dictionary);
	void set_add (__object__*);
	bool set_rmv (__object__*);
	void set_clr ();
	bool set_issubset (dictionary);
	void set_intersection_ctor (dictionary, dictionary);
	void set_union_ctor (dictionary, dictionary);
	void set_symmetric_difference_ctor (dictionary, dictionary);
	void set_union_update (dictionary);
	void set_difference_ctor_1sm (dictionary, dictionary);
	void set_difference_ctor_1bg (dictionary, dictionary);
	slow	void set_print_items ();

	~dictionary ();
};

class dictionaryStr : dictionary
{
	bool cmp_key_ent (dictEntry *E, __object__ *k) INLINE;
	long get_hash (__object__*) INLINE;
	bool type_good (__object__*) INLINE;
	void mutateby (__object__*);
   public:
};

class dictionaryInt : dictionary
{
	bool cmp_key_ent (dictEntry *E, __object__ *k) INLINE;
	long get_hash (__object__*) INLINE;
	bool type_good (__object__*) INLINE;
	void mutateby (__object__*);
   public:
};

class dictionaryStrAlways : dictionaryStr
{
	bool type_good (__object__*) INLINE;
	void mutateby (__object__*);
   public:
	__object__ *lookup_stri (__object__*) INLINE;
	void insert_stri (__object__*, __object__*);
};

struct AttrPair {
	AttrPair (const char*, __object__*);
	AttrPair (const char*, const char*);
	AttrPair (const char*, int);
	__object__ *obj;
	__object__ *idx;
};

extern DictObj DictMethods;

final class DictObj : __container__, seg_allocd
{
	const char *const stype = DictType;
	const TypeObj &type = &DictTypeObj;
	DictObj *type_methods = &DictMethods;

	dictionaryStr D;

	__object__ *type_call (REFPTR[], int);
   public:
	DictObj ();
	DictObj (const method_attribute*);
	void __attrdict ();

	void AddItems (AttrPair [...]);
	void ictor (AttrPair arg [...])		{ ctor (); AddItems (argv, argc); }

	int len ()			{ return D.used; }
	bool Bool ()			{ return (*this).len (); }
	bool contains (__object__*);
	__object__ *xgetitem (__object__*);
	void xdelitem (__object__*);
	void xsetitem (__object__*, __object__*);
	__object__ *iter ();

slow	void print ();
trv	void traverse ();
trv	void __clean ();

	/* ---* common dict methods *--- */
	__object__ *setdefault (__object__*, __object__*);
	__object__ *xgetitem_noraise (__object__*);
	ListObj *keys ();
	ListObj *values ();
	ListObj *items ();
	__object__ *iteritems ();
	__object__ *itervalues ();
	dictEntry *__iterfast (dictEntry*);
	__object__ *min_max (int);
	void update (DictObj);
slow	StringObj *str ();

	/* ---* pyvm opt *--- */
inline	__object__ *xgetitem_str (__object__*);
inline	__object__ *xgetkey_str (__object__*);
inline	void xsetitem_str (__object__*, __object__*);
};

/* ---* namespace *--- */
//
// namespace -> class
// class is a factory of instances.
// although, if you think about it, semantically (with the wrong
// meaning of the word), the distinction between class and instance
// is a restriction of statically typed languages where the class is
// the declaration and the instance real memory that obeys the decl.
//
// in dynamic languages we have a more generic schema that has just
// one thing. let's call this object. An object is a factory of
// other objects. When we request an attribute from an object, if
// it doesn't have it it looks for it in the object that generated
// this object, and this continues upwards until the root object.
// so theoretically the distinction between class and instance isn't
// needed. In reallity though, since we limit our factories to
// classes and instances cannot be factories of other objects,
// classes have certain properties which we can optimize.
//

class NamespaceObj : __container__, seg_allocd, wnext
{
	const char *const stype = NamespaceType;
	const TypeObj &type = &NamespaceTypeObj;
	const unsigned int vf_flags |= VF_ATTR;

	REFPTR __dict__;
	void __clean ();
	bool Bool ();
	int len ();
   public:
	NamespaceObj ();
	NamespaceObj (__object__*);

	bool hasattr (__object__*);
	void setattr (__object__*, __object__*);
	void delattr (__object__*);
	__object__ *getattr (__object__*);
	__object__ *binary_add (__object__*);
	__object__ *binary_multiply (__object__*);
	bool contains (__object__ *o)	{ return getattr (StringObj.fcheckedcast (o)) != 0; }

	__object__ *iter ();
	StringObj *repr ();
	StringObj *str ();
/*auto*/	__object__ *xnext ();
	__object__ *xgetitem (__object__*);
	void xsetitem (__object__*, __object__*);
	void xdelitem (__object__*);
	bool cmp_EQ (__object__*);
	int cmp_GEN (__object__*);
	long hash ();

	void print ();
trv	void traverse ();
};

enum { MTYPE_TOPLEV, MTYPE_INIT, MTYPE_SUBM };

final class ModuleObj : NamespaceObj, seg_allocd
{
	REFPTR pyc_path;
	REFPTR module_name;	/* sys.modules [module_name] == this */
	int mtype;
    public:
	ModuleObj ();
	ModuleObj (__object__*, __object__*);

	void AddAttributes (AttrPair [...]);
	void AddFuncs (const bltinfunc*);
	void AddAlias (const char**);
	void BltinModule (const char*, const bltinfunc* = 0, const char** = 0);
	void ictor (AttrPair [...]);

	void print ();
};

extern __object__ *TheObject;

final class DynClassObj : NamespaceObj, seg_allocd
{
	const char *const stype = ClassType;
	const TypeObj &type = &ClassTypeObj;

	REFPTR __bases__;
	REFPTR __name__;
	/* slots */
	REFPTR __getattr__, __del__, __setattr__;
	bool newstyle;
   public:
	DynClassObj (__object__*, __object__*, __object__*);
	DynClassObj (__object__*, __object__*, const char*);

	bool hasattr (__object__*);
	void setattr (__object__*, __object__*);
	void delattr (__object__*);
	__object__ *getattr (__object__*);
	void call (REFPTR, REFPTR [], int);

	bool isparentclass (__object__*);

	void print ();
trv	void traverse ();
trv	void __clean ();
};

final class DynMethodObj : __container__, personal_allocator
{
	const char *const stype = BoundType;
	const TypeObj &type = &BoundTypeObj;

	DynMethodObj *fnext;
	REFPTR __self__, __method__;
	void __clean ();
   public:
	DynMethodObj (__object__*, __object__*);

	bool Bool ()	{ return true; }
	void call (REFPTR, REFPTR [], int);
	__object__ *getattr (__object__*);

	void print ();
trv	void traverse ();
};

final class DynStaticMethodObj : __container__, seg_allocd
{
	const char *const stype = BoundType;	/* FIX */
	const TypeObj &type = &BoundTypeObj;

	REFPTR __callable__;
   public:
	DynStaticMethodObj (__object__*);

	void call (REFPTR, REFPTR [], int);

	void print ();
trv	void traverse ();
};

final class DynClassMethodObj : __container__, seg_allocd
{
	const char *const stype = BoundType;	/* FIX */
	const TypeObj &type = &BoundTypeObj;
	const unsigned int vf_flags |= VF_CLSMETH|VF_CALLABLE;

   public:
	DynClassMethodObj (__object__*);
	REFPTR __callable__;
	void call (REFPTR, REFPTR[], int);

	void print ();
trv	void traverse ();
};

final class DynInstanceObj : NamespaceObj, seg_allocd
{
	const char *const stype = InstanceType;
	const TypeObj &type = &InstanceTypeObj;

	REFPTR __class__;
	bool delmethod ();
   public:
	DynInstanceObj (__object__*);

	bool hasattr (__object__*);
	void setattr (__object__*, __object__*);
	void delattr (__object__*);
	__object__ *getattr (__object__*);
	void call (REFPTR, REFPTR[], int);


	void print ();
trv	void traverse ();
	void __release ();
trv	void __clean ();
};

/* ---* marshal *--- */

typedef unsigned char byte;
extern __object__ *load_compiled (char*, __object__*);
extern __object__ *r_marshal (const byte*, int, int*);

//
// So far we just have a nice dynamic library but no mention to bytecode. this is pyvm 
//

typedef void **INSTR;
#ifdef	DIRECT_THREADING
typedef	INSTR PCtype;
#else
typedef	byte *PCtype;
#endif

struct exec_stack
{
	// this has many static inline methods to push/pop, etc.
	REFPTR *STACK, *STACKTOP;
	int maxTOS;
	~exec_stack();
trv	void traverse_stack ();
};

struct vm_context : personal_allocator
{
	// this could be the frame object.
	exec_stack	S;
	int	 	LTOS;
	DictObj		*globals;
	REFPTR		*fastlocals;
#ifdef	DIRECT_THREADING
	INSTR		WPC;
#else
	const byte	*bcd, *fbcd;
#endif
	block_data *LOOPS;

	// not exported
	REFPTR		*retval;
	REFPTR		FUNC;
	int		cloned;
	union {
		vm_context	*caller;
		vm_context	*fnext;
	};

	void release_ctx ();
	__object__ *FastToLocals ();
	void traverse_vm (int = 1);
	bool after_yield ();

static	PyCodeObj *get_code ()	{ return FUNC.as_func->codeobj.as_code; }
};

extern __object__ *preempt_pyvm (vm_context*);

class ContextSwitchObj : __permanent_container__
{
	/* a singleton mostly */
	const char *const stype = "";
	vm_context *vm;
	ContextSwitchObj ()	{ __permanent_container__.ctor (); }
	void setretval (REFPTR*);
	void print ();
	void trv traverse ();
};

extern ContextSwitchObj CtxSw;

enum { TYPEBRK = 0, TYPE_HB, TYPEEXC, TYPEFIN };

struct block_data
{
	/* the bytecode exit block (see POP_BLOCK, SETUP_LOOP, SETUP_EXCEPT) */
	PCtype addr;
	void *stacktop;
	int setup_type;
};

#define TIMESLICE 340
#define GCMEGATICK 260
//#define GCMEGATICK 2500
#define VMCOST(X) vmTicks -= X

enum TH_STATUS { TH_RUNNING, TH_BLOCKED, TH_SOFTBLOCK };

extern long vmTicks;

/* co-routines */

struct preempt_link
{
	vm_context *v;
	preempt_link *outer;
};

class Task
{
	vm_context *vm;		/* current vm context */
	int ID;			/* incremental ID */
	int state;		/* enum TH_STATUS */

	/* When the Task is blocking */
	uint PID;		/* OS thread ID handling the system call */
	void *_dta;		/* C-stacktop to restore when it reclaims the GIL */

	/* lists */
	Task *next, *prev;	/* Running list */
	Task *_next, *_prev;	/* All Tasks list */

slow	void move_running();
slow	Task *move_blocked();
   public:
	int preemptive;
	preempt_link *pctx;
	Task (vm_context*, int);

trv	void traverse_task ();
	~Task ();
};

extern Task *RF, *RL, *RC, *RALL;

class inline_machine_code
{
	// this is used for things implemented in bytecode
	byte *code;
	int codesize;
	int nloops;
#ifdef	DIRECT_THREADING
	void **lcode;
#endif
   public:
	inline_machine_code ()	{ }
	void make (byte*, int, bool = false);
};

/* code, function, generator -- objects */

benum {
	PYVMFLAGS_LOCALS
};

class PyCodeObj : __container__
{
	const char *const stype = PyCodeType;
	const TypeObj &type = &PyCodeTypeObj;

#ifdef	DIRECT_THREADING
	void **lcode;
	void relocate_bytecode () noinline;
	void inline_consts ();
#endif
	short int argcount, nlocals, stacksize, flags, firstlineno, nloops, nclosure;
	short int nframe, off1, off2, pyvm_flags, self_closure;
#ifdef	ZLNOTAB
	short int lno_offset, lno_len;
#endif

	REFPTR code, consts, names, varnames, freevars, cellvars, filename, name, lnotab;
	REFPTR module;	// 'module' obsoletes 'filename'?
	void _prep ()	{ off1 = (stacksize + 1) * sizeof (REFPTR);
			  off2 = off1 + (nlocals) * sizeof (REFPTR);
			  nframe = off2 + nloops * sizeof (block_data); }
	__object__ *LineInfo (PCtype);
	__object__ *type_call (REFPTR[], int);
	void prepare_bytecode ();
	void set_varnames (Tuplen*);
	__object__ *get_const (int);
   public:
	PyCodeObj ();
	PyCodeObj (inline_machine_code, Tuplen*, int, int, int, char*,
		   Tuplen* = NILTuple, Tuplen* = NILTuple) noinline;

	__object__ *getattr (__object__*);
	void print ();
	void dprint ();
trv	void traverse ();
trv	void __clean ();
slow	void disassemble ();
	~PyCodeObj ();
};

extern DictObj *globalocals;

class PyFuncObj : __container__
{
	const char *const stype = PyFuncType;
	const TypeObj &type = &PyFuncTypeObj;
	const unsigned int vf_flags |= VF_VMEXEC|VF_CALLABLE;

	REFPTR codeobj;
	REFPTR GLOBALS;
	REFPTR LOCALS;
	REFPTR closures;
	short int ndflt, nfast, argcount;
	short int nframe, off1, off2, stacksize;
	char theglobal;

	PCtype exc_loc;
#ifdef	DIRECT_THREADING
	INSTR lcode;
#endif

virtual	void parse_args (REFPTR*, const REFPTR*, int, int);
	bool has_va, has_kw;
	bool reentring;
	vm_context cache_ctx;

   public:
	PyFuncObj (__object__*, DictObj*, DictObj* = 0) noinline;
	void call (REFPTR, REFPTR*, int);
	__object__ *getattr (__object__*);
	void print ();
trv	void traverse ();
trv	void __clean ();
	~PyFuncObj ();

	__object__ *FastToLocals (vm_context*);
};

extern __object__ *MakeFunction (__object__*, DictObj*, REFPTR* = 0, int = 0) noinline;

#define	BYTEARG(X) X&255, X>>8

extern __object__ *pyvm_exc_info();
extern void catch_stop_iteration (Interrupt*);
extern REFPTR __builtins__;

/* Py Exception objects -- also available from __builtins__ */

extern struct _DynExceptions {
	__object__ *Exception;
	__object__ *SystemExit;
	__object__ *StopIteration;
	__object__ *RuntimeError;	/* OK here? */
	__object__ *StandardError;
	  __object__ *KeyboardInterrupt;
	  __object__ *ImportError;
	  __object__ *AttributeError;
	  __object__ *NameError;
	  __object__ *TypeError;
	  __object__ *AssertionError;
	  __object__ *EOFError;
	  __object__ *EnvironmentError;
	    __object__ *IOError;
	    __object__ *OSError;
	  __object__ *RunTimeError;
	    __object__ *NotImplementedError;
	  __object__ *ValueError;
	  __object__ *LookupError;
	    __object__ *IndexError;
	    __object__ *KeyError;
	  __object__ *SyntaxError;
	  __object__ *ArithmeticError;
	    __object__ *FloatingPointError;
	__object__ *Warning;
	  __object__ *RuntimeWarning;
	  __object__ *DeprecationWarning;
} DynExceptions;

/* ---------* GIL control *--------- */

extern void *py_begin_allow_threads ();
extern void py_end_allow_threads (void*);

#define RELEASE_GIL void *_v = py_begin_allow_threads ();
/* no longjmp */
#define ACQUIRE_GIL py_end_allow_threads (_v);

/* ----* internal extending and embedding API *---- */

// the classes are at "funcwrapper.h"

extern __object__ *donothing_F;
typedef __object__ *(*no_arg_func)();
typedef __object__ *(*fixed_arg_func)(REFPTR*);
typedef __object__ *(*var_arg_func)(REFPTR*, int);

__object__ *extendFunc (const char*, int, fixed_arg_func);
__object__ *extendFunc2 (const char*, int, int, var_arg_func);

#define SETARGC(X,Y) (X + Y * 1024)
#define MINARGC(X) (X.argnum % 1024)
#define MAXARGC(X) (X.argnum / 1024)
#define INFARGC 200

struct method_attribute {
	char *name, *fname;
	int argnum;
	void *callable;
#define	MSENTINEL {0, 0, 0, 0}
};

struct bltinfunc {
	char *name;
	int argnum;
	void *fptr;
	char *doc;
#define	BSENTINEL {0, 0, 0, 0}
};

#define VSTR(X) X, sizeof X - 1
#define INTERNED(X) new_interned (VSTR (X))

extern __object__ *donothing_v (REFPTR[], int);
extern __object__ *donothing_f (REFPTR[]);

/* open/file API */

extern __object__ *open_file (const char*, int);
extern __object__ *open_file_fd (int, int);
extern __object__ *stdoutObj, *stderrObj, *stdinObj;
extern __object__ *load_marshal (REFPTR[]);

/* set API */

extern __object__ *set_obj (__object__*);
extern __object__ *set_obj ();

/* stdout */

extern void prepare_stdout (int);
extern void whereami ();
