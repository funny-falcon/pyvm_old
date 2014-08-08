
final class PyGeneratorFuncObj : __container__
{
	const char *const stype = PyFuncType;
	const TypeObj &type = &PyFuncTypeObj;
	const unsigned int vf_flags |= VF_CALLABLE;

	REFPTR GTOR;
   public:
	PyGeneratorFuncObj (__object__*);
	void call (REFPTR, REFPTR [], int);
slow	void print ();
trv	void traverse ();
};

final class PyGeneratorObj : __container__, seg_allocd
{
	const char *const stype = PyFuncType;
	const TypeObj &type = &PyFuncTypeObj;
	const unsigned int vf_flags |= VF_ITER;

	vm_context *vm;
   public:
	PyGeneratorObj (vm_context *v)	{ vm = v; __container__.ctor (); }
	int len ()			{ return -1; }
	bool contains (__object__*);
	__object__ *iter ()		{ return this; }
	__object__ *xnext ()		{ CtxSw.vm = vm; return &CtxSw; }
	__object__ *next ()		{ return preempt_pyvm (vm); }
	__object__ *getattr (__object__*);
slow	void print ();
trv	void traverse ();
	~PyGeneratorObj ();
};
