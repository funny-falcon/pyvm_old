class NotifyObj
{
	inline virtual const;
	Task *T;
	void set_retval (__object__*);
    public:
	NotifyObj ();
virtual void do_notify (int);
virtual ~NotifyObj () {}
};

extern __object__ *vmpollin (NotifyObj*, int, int);
extern __object__ *vmpollout (NotifyObj*, int, int);
