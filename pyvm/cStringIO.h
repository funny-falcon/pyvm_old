//
// cStringIO can also be used in a local declaration to sum
// up string concatenations (interpolation, join, str(tuple), etc)
//
#define cSTRING_CHUNK 252

struct cStringIO_chunk
{
	char data [cSTRING_CHUNK];
	cStringIO_chunk *next;
};

__unwind__
class cStringIO
{
	int avail, used;
	cStringIO_chunk first, *last;
    public:
	cStringIO ();
	void write (StringObj*) nothrow;
	void strcat (const char*, int) nothrow;
	StringObj *getvalue () nothrow;
	~cStringIO ();
};
