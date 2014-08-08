
OBJS = objdir/seg-malloc.o objdir/libdlmalloc.o objdir/threading.o objdir/IO.o objdir/module.sys.o\
       objdir/module.posix.o objdir/module.time.o objdir/module.thread.o\
       objdir/module.__builtins__.o objdir/libmt19937ar.o objdir/module._random.o\
       objdir/marshal.o objdir/util.o objdir/file.o objdir/module.silly.o\
       objdir/module.math.o objdir/module.binascii.o objdir/cold.o \
       objdir/interned.o objdir/sort.o objdir/pyby.o objdir/module.string.o\
       objdir/module._itertools.o objdir/module.gc.o objdir/module.JIT.o objdir/module.marshal.o\
       objdir/module.array.o objdir/module.re.o objdir/libmd5.o objdir/dict2.o\
       objdir/module._bisect.o objdir/module.md5.o objdir/module.sha.o\
       objdir/module.pyvm_extra.o objdir/importfile.o objdir/module.__socket.o\
       objdir/module.cStringIO.o objdir/poller.o objdir/vmpoll.o\
       objdir/stdout.o objdir/filedes.o objdir/memfs.o objdir/boot.o

CFILES = cdir/seg-malloc.c cdir/threading.c cdir/file.c cdir/util.c cdir/marshal.c cdir/IO.c\
	cdir/module.sys.c cdir/module.posix.c cdir/module.time.c cdir/module.md5.c cdir/pyvm.c\
	cdir/module.sha.c cdir/module.thread.c cdir/module.__builtins__.c cdir/module.silly.c\
	cdir/module.math.c cdir/module._random.c cdir/module.binascii.c\
	cdir/cold.c cdir/interned.c cdir/dict2.c cdir/sort.c cdir/pyby.c cdir/module.string.c\
	cdir/module._itertools.c cdir/module._bisect.c cdir/module.gc.c cdir/module.JIT.c\
	cdir/module.marshal.c cdir/module.array.c cdir/module.re.c cdir/module.pyvm_extra.c\
	cdir/importfile.c cdir/module.__socket.c cdir/module.cStringIO.c\
	cdir/poller.c cdir/vmpoll.c cdir/stdout.c cdir/filedes.c cdir/memfs.c cdir/boot.c

LWC=../lwc/objdir/lwc
CC =gcc
#CC =gcc4.0
ifeq (1,1)
CFL = -c -O3 -g -Wall
CFLs = -c -Os -g -Wall
CFL2 = -c -O2 -g -Wall
else
CFL = -c -Wall -g -O0
CFLs = -c -O0 -g -Wall
CFL2 = -c -O0 -g -Wall
endif

all: pcre/libpcre.a zlib/libz.a $(OBJS) objdir/pyvm.o
	$(CC) $(OBJS) objdir/pyvm.o -g -lpthread -lm -ldl pcre/libpcre.a zlib/libz.a
	size a.out
	mv a.out ~/bin/pyvm

cygwin: pcre/libpcre.a zlib/libz.a $(OBJS) cdir/pyvm.c 
	$(CC) -Wall cdir/pyvm.c -g -O3 -o objdir/pyvm.o -c
	$(CC) $(OBJS) objdir/pyvm.o -g -lpthread -lm pcre/libpcre.a zlib/libz.a
	size a.exe
	mv a.exe /usr/bin/pyvm.exe

os: pcre/libpcre.a $(OBJS) cdir/pyvm.c 
	$(CC) -Wall cdir/pyvm.c -g -Os -o objdir/pyvm.o -c
	$(CC) $(OBJS) objdir/pyvm.o -g -lpthread -lm -ldl pcre/libpcre.a -Os zlib/libz.a
	size a.out
	mv a.out ~/bin/pyvm

cfiles: config.h $(CFILES)
	@echo "lwc OK."
	@echo

cdir/pyvm.c: dynlib.h *.h.c+ oputil.h VMPARAMS.h
	$(LWC) main.c+ > cdir/pyvm.c

objdir/pyvm.o: dynlib.h *.h.c+ oputil.h VMPARAMS.h cdir/pyvm.c
	$(CC) cdir/pyvm.c -c -g -o objdir/pyvm.o -Wall

o3: pcre/libpcre.a zlib/libz.a cfiles $(OBJS)
	$(CC) -Wall cdir/pyvm.c -g -O3 -o objdir/pyvm.o -c
	@#$(CC) -Wall cdir/pyvm.c -g -O3 -funroll-loops -o objdir/pyvm.o -c
	$(CC) -Wall -g -O3 $(OBJS) objdir/pyvm.o -Q -lpthread -lm -ldl pcre/libpcre.a zlib/libz.a
	size a.out
	mv a.out ~/bin/pyvm

pcre/libpcre.a:
	cd pcre && make

zlib/libz.a:
	cd zlib && make

clean:
	rm objdir/*.o

config.h: config.c pyconfig.py
	gcc config.c -o configure
	./configure > config.h
	rm -f configure
	python pyconfig.py >> config.h

cdir/seg-malloc.c: seg-malloc.c+ mallok.h
	$(LWC) seg-malloc.c+ > cdir/seg-malloc.c
objdir/seg-malloc.o: cdir/seg-malloc.c
	$(CC) cdir/seg-malloc.c $(CFL) -o objdir/seg-malloc.o

objdir/libdlmalloc.o: libdlmalloc.c
	$(CC) libdlmalloc.c $(CFL2) -o objdir/libdlmalloc.o

objdir/libmd5.o: libmd5.c
	$(CC) libmd5.c $(CFL) -o objdir/libmd5.o

cdir/threading.c: threading.c+
	$(LWC) threading.c+ > cdir/threading.c
objdir/threading.o: cdir/threading.c
	$(CC) $(CFL2) cdir/threading.c -o objdir/threading.o 

cdir/poller.c: poller.c+
	$(LWC) poller.c+ > cdir/poller.c
objdir/poller.o: cdir/poller.c
	$(CC) $(CFL2) cdir/poller.c -o objdir/poller.o 

cdir/vmpoll.c: vmpoll.c+
	$(LWC) vmpoll.c+ > cdir/vmpoll.c
objdir/vmpoll.o: cdir/vmpoll.c
	$(CC) $(CFL2) cdir/vmpoll.c -o objdir/vmpoll.o 

cdir/stdout.c: stdout.c+
	$(LWC) stdout.c+ > cdir/stdout.c
objdir/stdout.o: cdir/stdout.c
	$(CC) $(CFLs) cdir/stdout.c -o objdir/stdout.o

cdir/memfs.c: memfs.c+
	$(LWC) memfs.c+ > cdir/memfs.c
objdir/memfs.o: cdir/memfs.c
	$(CC) $(CFLs) cdir/memfs.c -o objdir/memfs.o

frozen:
	$(LWC) boot.c+ -DICECUBE> cdir/boot.c
	$(CC) $(CFLs) cdir/boot.c -o objdir/boot.o

cdir/boot.c: boot.c+
	$(LWC) boot.c+ > cdir/boot.c
objdir/boot.o: cdir/boot.c
	$(CC) $(CFLs) cdir/boot.c -o objdir/boot.o

cdir/filedes.c: filedes.c+
	$(LWC) filedes.c+ > cdir/filedes.c
objdir/filedes.o: cdir/filedes.c
	$(CC) $(CFLs) cdir/filedes.c -o objdir/filedes.o

cdir/file.c: file.c+
	$(LWC) file.c+ > cdir/file.c
objdir/file.o: cdir/file.c
	$(CC) $(CFL) cdir/file.c -o objdir/file.o

cdir/util.c: util.c+ oputil.h
	$(LWC) util.c+ > cdir/util.c
objdir/util.o: cdir/util.c
	$(CC) $(CFL2) cdir/util.c -o objdir/util.o

cdir/marshal.c: marshal.c+ VMPARAMS.h
	$(LWC) marshal.c+ > cdir/marshal.c
objdir/marshal.o: cdir/marshal.c
	$(CC) $(CFL) cdir/marshal.c -o objdir/marshal.o 

cdir/IO.c: IO.c+ threading.h
	$(LWC) IO.c+ > cdir/IO.c
objdir/IO.o: cdir/IO.c
	$(CC) $(CFL2) -Wno-parentheses cdir/IO.c -o objdir/IO.o

cdir/module.sys.c: config.h module.sys.c+ VMPARAMS.h
	$(LWC) module.sys.c+ > cdir/module.sys.c
objdir/module.sys.o: cdir/module.sys.c
	$(CC) $(CFLs) cdir/module.sys.c -o objdir/module.sys.o

cdir/module.__socket.c: config.h module.__socket.c+
	$(LWC) module.__socket.c+ > cdir/module.__socket.c
objdir/module.__socket.o: cdir/module.__socket.c
	$(CC) $(CFLs) cdir/module.__socket.c -o objdir/module.__socket.o

cdir/module.pyvm_extra.c: module.pyvm_extra.c+ VMPARAMS.h fya.c+
	$(LWC) module.pyvm_extra.c+ > cdir/module.pyvm_extra.c
objdir/module.pyvm_extra.o: cdir/module.pyvm_extra.c
	$(CC) $(CFL2) cdir/module.pyvm_extra.c -o objdir/module.pyvm_extra.o

cdir/module.posix.c: module.posix.c+
	$(LWC) module.posix.c+ > cdir/module.posix.c
objdir/module.posix.o: cdir/module.posix.c
	$(CC) $(CFLs) cdir/module.posix.c -o objdir/module.posix.o

cdir/module.time.c: module.time.c+
	$(LWC) module.time.c+ > cdir/module.time.c
objdir/module.time.o: cdir/module.time.c
	$(CC) $(CFLs) -Os cdir/module.time.c -o objdir/module.time.o

cdir/module.md5.c: module.md5.c+
	$(LWC) module.md5.c+ > cdir/module.md5.c
objdir/module.md5.o: cdir/module.md5.c
	$(CC) $(CFL) cdir/module.md5.c -o objdir/module.md5.o

cdir/module.sha.c: module.sha.c+
	$(LWC) module.sha.c+ > cdir/module.sha.c
objdir/module.sha.o: cdir/module.sha.c
	$(CC) $(CFL) cdir/module.sha.c -o objdir/module.sha.o

cdir/module.cStringIO.c: module.cStringIO.c+ cStringIO.h
	$(LWC) module.cStringIO.c+ > cdir/module.cStringIO.c
objdir/module.cStringIO.o: cdir/module.cStringIO.c
	$(CC) $(CFL) cdir/module.cStringIO.c -o objdir/module.cStringIO.o

cdir/module.thread.c: module.thread.c+ VMPARAMS.h
	$(LWC) module.thread.c+ > cdir/module.thread.c
objdir/module.thread.o: cdir/module.thread.c
	$(CC) $(CFL2) cdir/module.thread.c -o objdir/module.thread.o

cdir/importfile.c: importfile.c+
	$(LWC) importfile.c+ > cdir/importfile.c
objdir/importfile.o: cdir/importfile.c
	$(CC) $(CFLs) cdir/importfile.c -o objdir/importfile.o

cdir/module.__builtins__.c: module.__builtins__.c+ VMPARAMS.h
	$(LWC) module.__builtins__.c+ > cdir/module.__builtins__.c
objdir/module.__builtins__.o: cdir/module.__builtins__.c
	$(CC) $(CFL2) cdir/module.__builtins__.c -o objdir/module.__builtins__.o

cdir/module.silly.c: module.silly.c+
	$(LWC) module.silly.c+ > cdir/module.silly.c
objdir/module.silly.o: cdir/module.silly.c
	$(CC) $(CFL2) cdir/module.silly.c -o objdir/module.silly.o

cdir/module.math.c: module.math.c+
	$(LWC) module.math.c+ > cdir/module.math.c
objdir/module.math.o: cdir/module.math.c
	$(CC) $(CFL2) cdir/module.math.c -o objdir/module.math.o

objdir/libmt19937ar.o: libmt19937ar.c
	$(CC) $(CFL) libmt19937ar.c -o objdir/libmt19937ar.o

cdir/module._random.c: module._random.c+
	$(LWC) module._random.c+ > cdir/module._random.c
objdir/module._random.o: cdir/module._random.c
	$(CC) $(CFLs) cdir/module._random.c -o objdir/module._random.o

cdir/module.binascii.c: module.binascii.c+
	$(LWC) module.binascii.c+ > cdir/module.binascii.c
objdir/module.binascii.o: cdir/module.binascii.c
	$(CC) $(CFL) cdir/module.binascii.c -o objdir/module.binascii.o

cdir/cold.c: cold.c+ VMPARAMS.h config.h
	$(LWC) cold.c+ > cdir/cold.c
objdir/cold.o: cdir/cold.c
	$(CC) $(CFLs) cdir/cold.c -o objdir/cold.o

cdir/interned.c: interned.c+
	$(LWC) interned.c+ > cdir/interned.c
objdir/interned.o: cdir/interned.c
	$(CC) $(CFL2) cdir/interned.c -o objdir/interned.o

cdir/dict2.c: dict2.c+
	$(LWC) dict2.c+ > cdir/dict2.c
objdir/dict2.o: cdir/dict2.c
	$(CC) $(CFL) cdir/dict2.c -o objdir/dict2.o

cdir/sort.c: sort.c+
	$(LWC) sort.c+ > cdir/sort.c
objdir/sort.o: cdir/sort.c
	$(CC) $(CFL) cdir/sort.c -o objdir/sort.o

cdir/pyby.c: pyby.c+ VMPARAMS.h
	$(LWC) pyby.c+ > cdir/pyby.c
objdir/pyby.o: cdir/pyby.c
	$(CC) $(CFLs) cdir/pyby.c -o objdir/pyby.o

cdir/module.string.c: module.string.c+
	$(LWC) module.string.c+ > cdir/module.string.c
objdir/module.string.o: cdir/module.string.c
	$(CC) $(CFL) cdir/module.string.c -o objdir/module.string.o

cdir/module._itertools.c: module._itertools.c+
	$(LWC) module._itertools.c+ > cdir/module._itertools.c
objdir/module._itertools.o: cdir/module._itertools.c
	$(CC) $(CFL) cdir/module._itertools.c -o objdir/module._itertools.o

cdir/module._bisect.c: module._bisect.c+
	$(LWC) module._bisect.c+ > cdir/module._bisect.c
objdir/module._bisect.o: cdir/module._bisect.c
	$(CC) $(CFL) cdir/module._bisect.c -o objdir/module._bisect.o

cdir/module.gc.c: module.gc.c+
	$(LWC) module.gc.c+ > cdir/module.gc.c
objdir/module.gc.o: cdir/module.gc.c
	$(CC) $(CFL) cdir/module.gc.c -o objdir/module.gc.o

cdir/module.JIT.c: module.JIT.c+
	$(LWC) module.JIT.c+ > cdir/module.JIT.c
objdir/module.JIT.o: cdir/module.JIT.c
	$(CC) $(CFL) cdir/module.JIT.c -o objdir/module.JIT.o

cdir/module.marshal.c: module.marshal.c+ VMPARAMS.h
	$(LWC) module.marshal.c+ > cdir/module.marshal.c
objdir/module.marshal.o: cdir/module.marshal.c
	$(CC) $(CFL2) cdir/module.marshal.c -o objdir/module.marshal.o

cdir/module.array.c: module.array.c+ VMPARAMS.h
	$(LWC) module.array.c+ > cdir/module.array.c
objdir/module.array.o: cdir/module.array.c
	$(CC) $(CFL) cdir/module.array.c -o objdir/module.array.o

cdir/module.re.c: module.re.c+ VMPARAMS.h
	$(LWC) module.re.c+ > cdir/module.re.c
objdir/module.re.o: cdir/module.re.c
	$(CC) $(CFL) cdir/module.re.c -o objdir/module.re.o

backup:
	tar c *.c *.c+ *.h.c+ *.h > DD.tar
	bzip2 DD.tar

distclean:
	rm -f objdir/*.o a.out cdir/*.c config.h .preprocfile
	cd pcre && make clean
	cd zlib && make clean

BIOS:
#	pyvm ../Lib/pyc/pyc.pyc BIOS.py
#
# 	This assumes a working BIOS.pyc:
	pyvm -cc BIOS.py
