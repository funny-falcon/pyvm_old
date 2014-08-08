
static inline __object__.~__object__ ()
{
#ifdef	DEBUG_RELEASE
	print ("Destroy:"COLS, typeid, COLE" ", (void*) this, "\n");
#endif
}

double __object__.todouble ()
{
	return FloatObj.isinstance (this) ? FloatObj.cast (this)->f :
		(double) IntObj.fcheckedcast (this)->i;
}

double __object__.todouble_nocheck ()
{
	return FloatObj.isinstance (this) ? FloatObj.cast (this)->f :
		(double) IntObj.cast (this)->i;
}

/* ----* REFPTR *---- */

inline REFPTR.REFPTR (__object__ *x)
{
	o = x;
	++x->refcnt;
}

REFPTR.REFPTR ()
{
	o = &None;
}

void REFPTR.__swap (REFPTR x)
{
	__object__ *t = o;
	o = x.o;
	x.o = t;
}

static inline void REFPTR.ptraverse_ref ()
{
	c->sticky |= STICKY_TRAVERSE;
}

void REFPTR.operator = (__object__ *x)
{
	++x->refcnt;
	dtor ();
	o = x;
}

static inline void REFPTR.operator += (__object__ *x)
{
	/* When 'x' is already referenced by another REFPTR in a location where
	 * it cannot be affected by decrefing (and possibly freeing) some object. 
	 */
	dtor ();
	(o = x)->refcnt++;
}

static inline void REFPTR.breakref ()
{
	/* decref the object, but before doing that set the reference to None.
	 * That's useful for REFPTRs which are contained in other objects:
	 * decrefing the object may do a cycle and release the object containing
	 * this one. Thus if this happens we don't want to re-dtor the object.
	 * This doesn't happen in normal bytecode execution where everything
	 * is referenced on the stack. It can happen in GC-cleanup.
	 */
	__object__ *_o = o;
	o = &None;
	if_unlikely (!--_o->refcnt) {
		_o->__release ();
	}
}

REFPTR.~REFPTR ()
{
	/* actually, the branch is 50-50.
	 * we consider likely that refcnt is not zero in order to
	 * have a fast do-nothing case.  If extra destruction code
	 * is to be executed, we missed the super fast path anyway.
	 */
	if_unlikely (!--o->refcnt)
		o->__release ();
}

void REFPTR.strdtor ()
{
	if_unlikely (!--o->refcnt)
		(*(StringObj*)o).__release ();
}

void REFPTR.intdtor ()
{
	if_unlikely (!--o->refcnt)
		(*(IntObj*)o).__release ();
}

void REFPTR.fltdtor ()
{
	if_unlikely (!--o->refcnt)
		(*(FloatObj*)o).__release ();
}

static inline StringObj *REFPTR.check_string ()
{
	return StringObj.checkedcast (o);
}

static inline IntObj *REFPTR.check_int ()
{
	return IntObj.fcheckedcast (o);
}

void REFPTR.traverse_ref ()
{
#ifdef	DEBUG_GC_TRV
static	int depth;
	if (_debug_traverse && o->vf_flags & VF_TRAVERSABLE
	 && !(((__container__*)o)->sticky & STICKY_TRAVERSE)) {
		for (int i = 0; i < depth; i++)
			print (" ");
		print (COLS"*"COLE"DEPTH", depth, "to traverse:", o/*->typeid*/, NL);
	}
	depth++;
#endif
	if_unlikely (o->vf_flags & VF_TRAVERSABLE) {
		__container__ *c = (__container__*) o;
		if (!(c->sticky & STICKY_TRAVERSE)) {
#ifdef	DEBUG_GC_TRV
			if (_debug_traverse) {
				for (int i = 0; i < depth; i++)
					print (" ");
				print ("traversing:", o, NL);
			}
#endif
			c->sticky |= STICKY_TRAVERSE;
			c->traverse ();
		}
	}
#ifdef	DEBUG_GC_TRV
	--depth;
#endif
}
