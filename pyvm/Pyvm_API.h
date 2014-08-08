/*
 * Pyvm's public API for embedding libpyvm.  -version 1.0-
 *
 * This basic API is guaranteed to work for all future versions
 * of the library.
 *
 * This file is in the public domain.
 */

#define PYVM_OK		0
#define PYVM_EXCEPTION	1

typedef void *PyvmObj;

int Pyvm_Init ();

void Pyvm_IncrRefCount (PyvmObj);
void Pyvm_DecrRefCount (PyvmObj);

int Pyvm_Exec (const char*, PyvmObj, PyvmObj);
int Pyvm_Eval (const char*, PyvmObj, PyvmObj, PyvmObj*);
int Pyvm_StoreName (const char*, PyvmObj, PyvmObj);

int	Pyvm_ToInt (PyvmObj);
double	Pyvm_ToDouble (PyvmObj);
char*	Pyvm_ToString (PyvmObj);

PyvmObj	Pyvm_FromInt (int);
PyvmObj	Pyvm_FromDouble (double);
PyvmObj	Pyvm_FromString (const char*);

typedef void *(*PyvmGetSym) (const char*);

PyvmObj	Pyvm_InternDLL (PyvmGetSym);

int Pyvm_CompileExec (const char*, PyvmObj*);
int Pyvm_CompileEval (const char*, PyvmObj*);
int Pyvm_ExecCompiled (PyvmObj, PyvmObj, PyvmObj);
int Pyvm_EvalCompiled (PyvmObj, PyvmObj, PyvmObj, PyvmObj*);
