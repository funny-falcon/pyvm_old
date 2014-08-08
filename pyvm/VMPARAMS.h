#if 0
#define DEBUGVM 1
#define TRACEVM
//#define HAVE_TYPEID
#else
#define DEBUGVM 0
//#define HAVE_TYPEID
#define OPTIMIZEVM
//#define TRACEVM
#define DIRECT_THREADING
#endif

// Use gcc's cleanup attribute which uses EH section for
// exceptions. Unfortunatelly, EH exceptions are slower.
// If you enable this, you must also edit the makefile and
// change `CC=gcc` to `CC=gcc -fexceptions`.
//#define CPPUNWIND
