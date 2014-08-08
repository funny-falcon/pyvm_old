
	#include <stdio.h>
	void sleepus ()
	{
		sleep (1);
	}
	void sleepus2 (void (*f)())
	{
		sleep (1);
		f ();
		sleep (1);
	}
