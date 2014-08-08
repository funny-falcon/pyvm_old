
/*
 * libcallback
 *
 * So, you want to dlopen and link DLL libraries...
 * Which libraries and what APIs is not known until runtime.
 *
 * Some of these libraries may need callbacks so that would
 * mean that we have to generate C code and compile this code.
 *
 * libcallback is a library which helps us avoid this. It can
 * generate callback functions and then multiplex them into
 * the callback handler with a personal token per function.
 * For example, when a DLL calls a registered callback 'f'
 * provided by libcallback, what happens is this:
 *
 * 	f = new_callback (token);
 *	DLL.setKeyBoardFunc (f);
 *	// later
 *	DLL -> f (1,2)
 *	f -> vm_callback (token, 1, 2)
 *
 * The vm_callback should know what action to take from the value
 * of the token.
 * 
 * In the simple case the library can provide 32 callback functions
 * (pre compiled).  If we need more the library includes the binary
 * dump of itself.  This is copied to a temporary file and linked 
 * with the application to provide 32 new callbacks, etc.
 *
 */

/* RESTRICTION: at most 6 long (3 double in 32-bit) arguments max */

typedef long (*callback_t) (long, long, long, long, long, long);
typedef long (*vm_callback_t) (long, ...);

static vm_callback_t vm_callback;

struct cbpair
{
	callback_t T;
	int token;
};

#define CBPROTO(X) static long callback_ ## X (long, long, long, long, long, long);

CBPROTO(0)  CBPROTO(1)  CBPROTO(2)  CBPROTO(3)
CBPROTO(4)  CBPROTO(5)  CBPROTO(6)  CBPROTO(7)
CBPROTO(8)  CBPROTO(9)  CBPROTO(10) CBPROTO(11)
CBPROTO(12) CBPROTO(13) CBPROTO(14) CBPROTO(15)
CBPROTO(16) CBPROTO(17) CBPROTO(18) CBPROTO(19)
CBPROTO(20) CBPROTO(21) CBPROTO(22) CBPROTO(23)
CBPROTO(24) CBPROTO(25) CBPROTO(26) CBPROTO(27)
CBPROTO(28) CBPROTO(29) CBPROTO(30) CBPROTO(31)

static struct cbpair hooks [] = {
#define CBSET(X) {callback_ ## X, 0},
	CBSET (0)  CBSET (1)  CBSET (2)  CBSET (3)
	CBSET (4)  CBSET (5)  CBSET (6)  CBSET (7)
	CBSET (8)  CBSET (9)  CBSET (10) CBSET (11)
	CBSET (12) CBSET (13) CBSET (14) CBSET (15)
	CBSET (16) CBSET (17) CBSET (18) CBSET (19)
	CBSET (20) CBSET (21) CBSET (22) CBSET (23)
	CBSET (24) CBSET (25) CBSET (26) CBSET (27)
	CBSET (28) CBSET (29) CBSET (30) CBSET (31)
};

/*
 * Assume that the callback takes 6 longs.
 * As we have already seen, it's no problem to pass more arguments
 * in C.  This is a primitive __builtin_apply()
 * However, valgrind will complain this time.
 * 
 */

#define CBDEF(X) \
	static long callback_ ## X (long a, long b, long c, long d, long e, long f)\
	{\
		return vm_callback (hooks [X].token, a, b, c, d, e, f);\
	}


CBDEF(0)  CBDEF(1)  CBDEF(2)  CBDEF(3)
CBDEF(4)  CBDEF(5)  CBDEF(6)  CBDEF(7)
CBDEF(8)  CBDEF(9)  CBDEF(10) CBDEF(11)
CBDEF(12) CBDEF(13) CBDEF(14) CBDEF(15)
CBDEF(16) CBDEF(17) CBDEF(18) CBDEF(19)
CBDEF(20) CBDEF(21) CBDEF(22) CBDEF(23)
CBDEF(24) CBDEF(25) CBDEF(26) CBDEF(27)
CBDEF(28) CBDEF(29) CBDEF(30) CBDEF(31)

static int n;

// interface

void *new_callback (int token)
{
	if (n >= sizeof hooks / sizeof hooks [0])
		return 0;
	hooks [n].token = token;
	return hooks [n++].T;
}

void init_callbacks (void *v)
{
	vm_callback = v;
}
