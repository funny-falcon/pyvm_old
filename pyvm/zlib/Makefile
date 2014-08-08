CC = gcc -c -O2 -Wall

OBJ = adler32.o compress.o crc32.o deflate.o infback.o inffast.o inflate.o\
	 inftrees.o trees.o uncompr.o zutil.o

all: $(OBJ)
	@rm -f libz.a
	ar cq libz.a $(OBJ)
	ranlib libz.a
	wc -c libz.a
	@echo "zlib ok"
	@echo

adler32.o: adler32.c
	$(CC) adler32.c
compress.o: compress.c
	$(CC) compress.c
crc32.o: crc32.c
	$(CC) crc32.c
deflate.o: deflate.c
	$(CC) deflate.c -Os
infback.o: infback.c
	$(CC) infback.c
inffast.o: inffast.c
	$(CC) inffast.c -O3
inflate.o: inflate.c
	$(CC) inflate.c -O2
inftrees.o: inftrees.c
	$(CC) inftrees.c
trees.o: trees.c
	$(CC) trees.c -Os
uncompr.o: uncompr.c
	$(CC) uncompr.c
zutil.o: zutil.c
	$(CC) zutil.c

clean:
	rm -f *.o libz.a
