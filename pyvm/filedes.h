#ifndef FILEDES
#define FILEDES
/*
 * 1) object orientation of filedescriptor handling
 * 2) portability and wrapping (memfs)
 *
 * Details:
 * - If the mode is readonly, the file is mmaped if possible
 * - The files are opened in non-blocking mode by default.
 */
enum
{
	FD_BAD,
	FD_READ,
	FD_WRITE,
	FD_RW,
	FD_READ_MMAP,
};

__unwind__
class filedes
{
	short int type, memfsd;
	int fd;
	char *mm_start;
	int len;
    public:
	filedes (const char*, int, bool=true, bool=true);
	filedes (int, int, bool=true);
	unsigned int read (void*, unsigned int);
	unsigned int write (const void*, unsigned int);
	void wait_to_read ();
	void wait_to_write ();
	bool blocked;
	~filedes ();
};

int fs_access (const char*, int);
#endif
