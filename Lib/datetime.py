#
# datetime in py
#
# based on -complex- datetime.c 
#
# basically, pyRacerz needs datetime.now().seconds
# and we go as far as providing this...
#

# DLL libc.so

import DLL, os
from array import array
from time import strftime

Clib = DLL.dllopen ('/lib/libc.so.6')

def DF (name, spec, ret='', blocking=False):
    print "ADD NAME:", name
    globals() [name] = Clib.get ((ret, name, spec), blocking)

DF ('gettimeofday', 'p32', 'i')
DF ('gmtime', 'p32', 'i')
DF ('localtime', 'p32', 'i')

# private classes

def struct_access (ns, memb):
    for i, tm in enumerate (memb):
	gettm = lambda self, i=i: self.c_array [i]
	def settm (self, x, i=i):
	    self.c_array [i] = x
	ns [tm] = property (gettm, settm)

class struct_timeval:
    def __init__ (self, tv_array):
	self.c_array = tv_array
    struct_access (locals (), ('tv_sec', 'tv_usec'))
    new = staticmethod (lambda : array ('i', 2*[0]))

class struct_tm:
    def __init__ (self, tm_array):
	self.c_array = tm_array
    struct_access (locals (), ('tm_sec', 'tm_min', 'tm_hour', 'tm_mday', 'tm_mon',
		'tm_year', 'tm_wday', 'tm_yday', 'tm_isdst'))
    new = staticmethod (lambda : array ('i', 9*[0]))

def py_gettimeofday ():
    c = struct_timeval.new ()
    gettimeofday (c)
    return struct_timeval (c)

def py_gmtime (timet):
    tm = gmtime ((timet,))
    if not tm:
	return 0
    tm2 = struct_tm.new ()
    MemcpyInts (tm2, tm, 9)
    return struct_tm (tm2)

def py_localtime (timet):
    tm = localtime ((timet,))
    if not tm:
	return 0
    tm2 = struct_tm.new ()
    MemcpyInts (tm2, tm, 9)
    return struct_tm (tm2)

# public classes

class error:
    pass

class tzinfo:
    def from_utc (self, dt):
	if dt.tzinfo is not self:
	    raise "?"
	# ?????? call_utcoffset, calls tzinfo_nogo ('utcoffset')
	# and consequently this code path raises an error???????
	raise error

class datetime:
    def __init__ (self, year, month, day, hour=0, minute=0, second=0, usecond=0, tzinfo=None):
	self.year = year
	self.month = month
	self.day = day
	self.hour = hour
	self.minute = minute
	self.second = second
	self.unsecond = usecond
	self.tzinfo = tzinfo

    def now (cls, tz=None):
	if tz is not None and not isinstance (tz, tzinfo):
	    raise error
	self = datetime.best_possible (tz)
	if tz:
	    self = tz.from_utc (self)
	return self
    now = classmethod (now)

    @classmethod
    def best_possible (cls, tz=None):
	t = py_gettimeofday ()
	return cls.datetime_from_timet_and_us (t.tv_sec, t.tv_usec, tz)

    @classmethod
    def datetime_from_timet_and_us (cls, timet, usec, tz):
	if tz is None:
	    tm = py_localtime (timet)
	else:
	    tm = py_gmtime (timet)
	if tm:
	    if tm.tm_sec > 59:
		tm.tm_sec = 59
	    return datetime (tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour,
			     tm.tm_min, tm.tm_sec, usec, tz)
	else:
	    raise error

def is_leap (y):
	return y%4 == 0 and (y%100 != 0 or y%400 == 0)
def days_before_year (y):
	return y * 365 + y / 4 - y / 100 + y / 400
def days_before_month (year, month):
	_days_before_month = 0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334
	days = _days_before_month [month]
	if month > 2 and is_leap (year):
		days += 1
	return days
def ymd_to_ord (year, month, day):
	return days_before_year (year) + days_before_month (year, month) + day
	

class date:
	def __init__ (self, year, month, day):
		self.year, self.month, self.day = year, month, day
	def weekday (self):
		return (ymd_to_ord (self.year, self.month, self.day) + 6) % 7
	def toordinal (self):
		return ymd_to_ord (self.year, self.month, self.day)
	def strftime (self, fmt):
		# some problems with %z? (scan for %z and warn)
		w = self.weekday ()
		yd = self.toordinal () - date (self.year, 1, 1).toordinal () + 1
		T = self.year, self.month, self.day, 0, 0, 0, w, yd, -1
		return strftime (fmt, T)

	def __str__ (self):
		return '%i-%i-%i' % (self.year, self.month, self.day)

#########################################################################

MemcpyInts = DLL.MemcpyInts
