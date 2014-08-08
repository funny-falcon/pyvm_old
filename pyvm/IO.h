/******************************************************************************
	simple I/O
******************************************************************************/

#include "filedes.h"

enum RTYPE { RSTR, RLONG, RFLOAT, RADDR, RBUFF, RCHAR, REXT };

struct _CHAR {
	int c;
	_CHAR (int x)	{ c = x; }
};

struct __object__;

class Rdata
{
	/* This class's purpose is to resolve operator overloading and
	 * demultiplex it to its apropriate printing function.
	 */
	int type;
	union {
		__object__ *o;
		char c;
		const char *s;
		long i;
		double f;
		void *p;
		struct {
			const void *p;
			int s;
		} b;
	};
   public:
	Rdata (_CHAR x)			{ type = RCHAR; c = x.c; }
	Rdata (const char *x)		{ type = RSTR; s = x; }
	Rdata (long x)			{ type = RLONG; i = x; }
	Rdata (double x)		{ type = RFLOAT; f = x; }
	Rdata (void *x)			{ type = RADDR; p = x; }
	Rdata (__object__ *x)		{ type = REXT; o = x; }
	Rdata (const char *x, int y)	{ type = RBUFF; b.p = x; b.s = y; }
	Rdata (Rdata R)			{ type = type; b = R.b; }
};

struct chunka
{
	int pos;
	char *buffer;
	int dirty;
volatile int locked;
};

class FDout
{
	bool istty;
	chunka *C;
	filedes *FD;
	void writedt (const char*, int);
   public:
	FDout (filedes*);
	void flush ();
	void print (Rdata [...]);
	void pprint (Rdata [...]);
	void chr (char c)			{ writedt (&c, 1); }
	void softspace ();
	~FDout ();
};

struct IOline
{
	char *s;
	int len;
};

class FDin
{
	char buffer [8192];
	filedes *FD;
	int pos, end;
	bool locked;
   public:
	FDin (filedes*);
	int readline (IOline);
	char *readn (int*);
	~FDin ();
};

/* print subsystem */

extern void probj (__object__*);
extern FDout *OUT, *ERR;
extern FDin *IN;

//void print (Rdata arg [...]);
void pprint (Rdata arg [...]);
void print_out (Rdata arg [...]);

#define err ERR->print
