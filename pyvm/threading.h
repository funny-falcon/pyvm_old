#define TAKE_OVER (void*)1

extern int nthreads;
extern bool multitasking;

bool fork_thread ();
void begin_allow_threads (bool);
void end_allow_threads ();
void main_thread (void*);
bool have_pending ();
bool am_GIL_owner ();
