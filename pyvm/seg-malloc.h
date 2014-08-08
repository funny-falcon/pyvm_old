
#define FASTCALL1 __attribute__ ((regparm(1)))
#define FASTCALL2 __attribute__ ((regparm(2)))

#if 1

extern void *seg_alloc (unsigned int) FASTCALL1 __attribute__ ((malloc)) nothrow;
template seg_malloc(n) {
	(__builtin_constant_p (n) ? ({
		void *r;
		switch (n) {
		case 52:
		case 56: r = seg_alloc56 (); break;
		case 28:
		case 32: r = seg_alloc32 (); break;
		case 92:
		case 96: r = seg_alloc96 (); break;
		default: fprintf (stderr, "No chandler for %i\n", n); r = 0;
		}
		r;
	}) : seg_alloc (n))
}

extern void *seg_alloc96 () FASTCALL1 __attribute__ ((malloc)) nothrow;
extern void *seg_alloc56 () FASTCALL1 __attribute__ ((malloc)) nothrow;
extern void *seg_alloc32 () FASTCALL1 __attribute__ ((malloc)) nothrow;
extern void *seg_alloc24 () FASTCALL1 __attribute__ ((malloc)) nothrow;

extern void seg_free (void*) FASTCALL1 nothrow;
extern void seg_free (void*,unsigned int) FASTCALL2 nothrow;
extern void seg_freeXX (void*) FASTCALL1 nothrow;

extern void *seg_realloc (void*, unsigned int) nothrow;
extern void *seg_realloc2 (void*, unsigned int, unsigned int) nothrow;
extern int seg_n_segments ();

#else	// enable valgrind 

#define seg_alloc malloc
#define seg_alloc56() malloc(56)
#define seg_alloc32() malloc(32)
#define seg_free free
#define seg_freeXX free
#define seg_realloc realloc
#define seg_realloc2(P,O,S) realloc (P,S)

#endif

