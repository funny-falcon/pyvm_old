
#include <unistd.h>
#include <stdio.h>

int main ()
{
	{
		/* directories */
		char tmp [1000];
		strcpy (tmp, getcwd (tmp, sizeof tmp));
		strrchr (tmp, '/')[1] = 0;
		printf ("#define PYVM_HOME \"%s\"\n", tmp);
		printf ("#define LIB_DIR \"Lib/\"\n");
	}

	{
		/* endian */
		union U {
			char c [2];
			short int s;
		} u;

		short int s = 4000;
		u.c [0] = s & 0xff;
		u.c [1] = (s>>8) & 0xff;

		printf ("#define PYVM_ENDIAN_%s\n", (u.s == s) ? "LITTLE":"BIG");
	}
	{
		/* have memrchr? */
		FILE *F = fopen ("xxxtmpxxx.c", "w");
		fputs ("int main () { int a[10]; memrchr (a, 0, 10); return 0; }\n", F);
		fclose (F);
		if (!system ("gcc xxxtmpxxx.c"))
			printf ("#define HAVE_MEMRCHR\n");
		remove ("xxxtmpxxx.c");
	}

	return 0;
}
