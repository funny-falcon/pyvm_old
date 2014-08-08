
#define dstdout stdout

#include "VMPARAMS.h"

#include "threading.h"
#include "IO.h"
extern "limits.h" {
#include <limits.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <ctype.h>
#include <semaphore.h>
}
extern "sys/mman.h" { }
extern "sys/stat.h" { }
extern "errno.h" { }
extern "fcntl.h" { }
extern "sys/types.h" { }
extern "unistd.h" { }
extern "stdio.h" { }
extern "string.h" { }
extern "stdlib.h" { }
extern "time.h" { }
extern "ctype.h" { }
extern "semaphore.h" { }

_lwc_config_ {
#ifdef	CPPUNWIND
	gcc34cleanup;
#else
	no_gcc34cleanup;
#endif


//	lwcdebug PARSE_ERRORS_SEGFAULT;
//	lwcdebug EXPR_ERRORS_FATAL;

//	lwcdebug DCL_TRACE;
//	lwcdebug PEXPR;
//	lwcdebug FUNCPROGRESS;
//	lwcdebug PROGRESS;
//	onebigfile;
//	x86stdcalls;
}

#include "mallok.h"

#define STRL(X) (X, sizeof X - 1)
#define ncase break; case
#define ndefault break; default
#define noreturn __attribute__ ((noreturn, __noinline__))
#define noinline __attribute__ ((noinline))
#define autovrt auto virtual
#define inlines static inline
#define automod	auto modular
#define constant(X) __builtin_constant_p(X)
#define APAIR(X) X, sizeof X
typedef unsigned int uint;

/* DOES NOT WORK. lwc as a preprocessor doesn't know about __OPTIMIZE__ */
#if defined __OPTIMIZE__
#define INLINE __attribute__((always_inline))
#else
#define INLINE
#endif

#define unlikely(...) __builtin_expect (__VA_ARGS__, 0)
#define likely(...) __builtin_expect (__VA_ARGS__, 1)
#define if_unlikely(...) if (__builtin_expect (__VA_ARGS__, 0))
#define if_likely(...) if (__builtin_expect (__VA_ARGS__, 1)) 
#define slow __section__ (".text.slowzone")
#define slowcold __section__ ("neverused")
#define once \
	static bool _once;\
	if_unlikely (!_once && (_once = true))
#define modsection __section__ (".text.modules")
#define _module modsection static
#define trv __section__ (".text.traversals")
#define CRASH *(int*)0=0;
#define COLS "\033[01;37m"
#define COLB "\033[01;34m"
#define COLR "\033[01;31m"
#define COLX "\033[01;35m"
#define COLE "\033[0m"
#define OCC (__object__*)
#define NL "\n"
#define NN "\n"

static inline int max (int a, int b)	{ return a > b ? a : b; }
static inline int min (int a, int b)	{ return a < b ? a : b; }
static inline bool in2 (int a, int b, int c) { return a == b || a == c; }
static inline bool in3 (int a, int b, int c, int d) { return a == b || a == c || a == d; }

static inline int nz (int x)		{ return x ?: 1; }

extern int mytoa10 (char*, int);

static inline
class sem
{
	sem_t s;
    public:
	sem ()		{ sem_init (&s, 0, 0); }
	void post ()	{ sem_post (&s); }
	void wait ()	{ sem_wait (&s); }
};

__unwind__
static class bytearray
{
	char *str;
	int len, alloc;
    public:
	bytearray ()	{ str = (char*) __malloc (alloc = 256); len = 0; }
	void addstr (char *s, int l)
	{
		while (len + l > alloc)
			str = (char*) __realloc (str, alloc *= 2);
		memcpy (str + len, s, l);
		len += l;
	}
	~bytearray ()	{ __free (str); }
};

#define CC const
/* MT19937ar */
