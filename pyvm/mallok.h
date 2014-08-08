
/*
 *	We'll be using Doug Lea's malloc again.
 *
 * Glibc's malloc really sucks.  If you link with lpthread malloc becomes like
 * 500% slower and there is no way to request non-locking malloc.  In pyvm
 * mallocs are already protected by the GIL.
 *
 * Moreover, if we link with other applications, they can use the libc malloc
 * without interferring with pyvm's allocations.  So this actually turns out
 * to be perfect for our purpose.
 *
 * Thanks Doug Lea!
 */

#if 0
#include <malloc.h>
#define __malloc malloc
#define __free free
#define __realloc realloc
#define __memalign memalign
#define __calloc calloc
#else
_lwc_config_ {
	new = dlmalloc;
	delete = dlfree;
};

static inline void *__malloc (unsigned int x)
{
	return dlmalloc (x);
}

static inline void __free (void *p)
{
	return dlfree (p);
}

static inline void *__realloc (void *p, unsigned int x)
{
	return dlrealloc (p, x);
}

static inline void *__memalign (unsigned int a, unsigned int x)
{
	return dlmemalign (a, x);
}

static inline void *__calloc (unsigned int i, unsigned int j)
{
	return dlcalloc (i, j);
}

extern void *dlmalloc (unsigned int) __attribute__ ((malloc)) nothrow;
extern void dlfree (void*) nothrow;
extern void *dlrealloc (void*, unsigned int) nothrow;
extern void *dlmemalign (unsigned int, unsigned int) nothrow;
extern void *dlcalloc (unsigned int, unsigned int) __attribute__ ((malloc)) nothrow;
#endif
