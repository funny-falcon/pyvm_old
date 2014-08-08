#
# Modified for use in pyvm by Stelios Xanthakis
#
#	- removed subclassing 'dict'. Subclass 'UserDict' instead.
#	- change the _quote algorithm to avoid using translate() and map()
#	- removed docstrings
#	- reindent with tabs
#
# Original Copyright:
####
#
# Copyright 2000 by Timothy O'Malley <timo@alum.mit.edu>
#
#                All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software
# and its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Timothy O'Malley  not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# Timothy O'Malley DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Timothy O'Malley BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#

import string

try:
	from cPickle import dumps, loads
except ImportError:
	from pickle import dumps, loads

import re

__all__ = ["CookieError","BaseCookie","SimpleCookie","SerialCookie",
           "SmartCookie","Cookie"]

_nulljoin = ''.join
_spacejoin = ' '.join

#
# Define an exception visible to External modules
#
class CookieError(Exception):
	pass


# These quoting routines conform to the RFC2109 specification, which in
# turn references the character definitions from RFC2068.  They provide
# a two-way quoting algorithm.  Any non-text character is translated
# into a 4 character sequence: a forward-slash followed by the
# three-digit octal equivalent of the character.  Any '\' or '"' is
# quoted with a preceeding '\' slash.
#
# These are taken from RFC2068 and RFC2109.
#       _LegalChars       is the list of chars which don't require "'s
#       _Translator       hash-table for fast quoting
#
ilLegalChars = re.compile (r".*[^A-Za-z0-9_!#$%&'*+.^`|~]").match

def allLegalChars (s):
	return not ilLegalChars (s)

_Translator       = {}
for i in range (32) + range (127, 256):
	_Translator [chr (i)] = '\\0'+oct (i)
for i in xrange (32, 127):
	_Translator [chr (i)] = chr (i)
_Translator.update ({'"' : '\\"', '\\' : '\\\\'})

def _quote(str):
	if allLegalChars (str):
		return str
	return '"' + ''.join ([_Translator [x] for x in str]) + '"'


_OctalPatt = re.compile(r"\\[0-3][0-7][0-7]").search
_QuotePatt = re.compile(r"[\\].").search

def _unquote(str):
	# If there aren't any doublequotes,
	# then there can't be any special characters.  See RFC 2109.
	if len(str) < 2:
		return str
	if str[0] != '"' or str[-1] != '"':
		return str

	# We have to assume that we must decode this string.
	# Down to work.

	# Remove the "s
	str = str[1:-1]

	# Check for special sequences.  Examples:
	#    \012 --> \n
	#    \"   --> "
	#
	i = 0
	n = len(str)
	res = []
	while 0 <= i < n:
		Omatch = _OctalPatt (str, i)
		Qmatch = _QuotePatt (str, i)
		if not Omatch and not Qmatch:              # Neither matched
			res.append(str[i:])
			break
		# else:
		j = k = -1
		if Omatch: j = Omatch.start(0)
		if Qmatch: k = Qmatch.start(0)
		if Qmatch and ( not Omatch or k < j ):     # QuotePatt matched
			res.append(str[i:k])
			res.append(str[k+1])
			i = k+2
		else:                                      # OctalPatt matched
			res.append(str[i:j])
			res.append( chr( int(str[j+1:j+4], 8) ) )
			i = j+4
	return _nulljoin(res)
# end _unquote

# The _getdate() routine is used to set the expiration time in
# the cookie's HTTP header.      By default, _getdate() returns the
# current time in the appropriate "expires" format for a
# Set-Cookie header.     The one optional argument is an offset from
# now, in seconds.      For example, an offset of -3600 means "one hour ago".
# The offset may be a floating point number.
#

_weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

_monthname = [None,
              'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def _getdate(future=0, weekdayname=_weekdayname, monthname=_monthname):
	from time import gmtime, time
	now = time()
	year, month, day, hh, mm, ss, wd, y, z = gmtime(now + future)
	return "%s, %02d-%3s-%4d %02d:%02d:%02d GMT" % \
           (weekdayname[wd], day, monthname[month], year, hh, mm, ss)


#
# A class to hold ONE key,value pair.
# In a cookie, each such pair may have several attributes.
#       so this class is used to keep the attributes associated
#       with the appropriate key,value pair.
# This class also includes a coded_value attribute, which
#       is used to hold the network representation of the
#       value.  This is most useful when Python objects are
#       pickled for network transit.
#

from UserDict import UserDict

class Morsel(UserDict):
	# RFC 2109 lists these attributes as reserved:
	#   path       comment         domain
	#   max-age    secure      version
	#
	# For historical reasons, these attributes are also reserved:
	#   expires
	#
	# This dictionary provides a mapping from the lowercase
	# variant on the left to the appropriate traditional
	# formatting on the right.
	_reserved = { "expires" : "expires",
                   "path"        : "Path",
                   "comment" : "Comment",
                   "domain"      : "Domain",
                   "max-age" : "Max-Age",
                   "secure"      : "secure",
                   "version" : "Version",
                   }

	def __init__(self):
		# Set defaults
		self.key = self.value = self.coded_value = None

		# Set default attributes
		UserDict.__init__ (self)
		for K in self._reserved:
			UserDict.__setitem__(self, K, "")

	def __setitem__(self, K, V):
		K = K.lower()
		if not K in self._reserved:
			raise CookieError("Invalid Attribute %s" % K)
		UserDict.__setitem__(self, K, V)

	def isReservedKey(self, K):
		return K.lower() in self._reserved

	def set(self, key, val, coded_val):
		# First we verify that the key isn't a reserved word
		# Second we make sure it only contains legal characters
		if key.lower() in self._reserved:
			raise CookieError("Attempt to set a reserved key: %s" % key)
		if not allLegalChars (key):
			raise CookieError("Illegal key value: %s" % key)

		# It's a good key, so save it.
		self.key                 = key
		self.value               = val
		self.coded_value         = coded_val

	def output(self, attrs=None, header = "Set-Cookie:"):
		return "%s %s" % ( header, self.OutputString(attrs) )

	__str__ = output

	def __repr__(self):
		return '<%s: %s=%s>' % (self.__class__.__name__,
                                self.key, repr(self.value) )

	def js_output(self, attrs=None):
		# Print javascript
		return """
        <SCRIPT LANGUAGE="JavaScript">
        <!-- begin hiding
        document.cookie = \"%s\"
        // end hiding -->
        </script>
        """ % ( self.OutputString(attrs), )

	def OutputString(self, attrs=None):
		# Build up our result
		#
		result = []

		# First, the key=value pair
		result.append ("%s=%s;" % (self.key, self.coded_value))

		# Now add any defined attributes
		if attrs is None:
			attrs = self._reserved
		for K,V in sorted (self.items ()):
			if V == "": continue
			if K not in attrs: continue
			if K == "expires" and type(V) is int:
				result.append ("%s=%s;" % (self._reserved[K], _getdate(V)))
			elif K == "max-age" and type(V) is int:
				result.append ("%s=%d;" % (self._reserved[K], V))
			elif K == "secure":
				result.append ("%s;" % self._reserved[K])
			else:
				result.append ("%s=%s;" % (self._reserved[K], V))

		return _spacejoin(result)



#
# Pattern for finding cookie
#
# This used to be strict parsing based on the RFC2109 and RFC2068
# specifications.  I have since discovered that MSIE 3.0x doesn't
# follow the character rules outlined in those specs.  As a
# result, the parsing rules here are less strict.
#

_LegalCharsPatt  = r"[\w\d!#%&'~_`><@,:/\$\*\+\-\.\^\|\)\(\?\}\{\=]"
_CookiePattern = re.compile(
    r"(?x)"                       # This is a Verbose pattern
    r"(?P<key>"                   # Start of group 'key'
    ""+ _LegalCharsPatt +"+?"     # Any word of at least one letter, nongreedy
    r")"                          # End of group 'key'
    r"\s*=\s*"                    # Equal Sign
    r"(?P<val>"                   # Start of group 'val'
    r'"(?:[^\\"]|\\.)*"'            # Any doublequoted string
    r"|"                            # or
    ""+ _LegalCharsPatt +"*"        # Any word or empty string
    r")"                          # End of group 'val'
    r"\s*;?"                      # Probably ending in a semi-colon
    )


# At long last, here is the cookie class.
#   Using this class is almost just like using a dictionary.
# See this module's docstring for example usage.
#
class BaseCookie(UserDict):
	# A container class for a set of Morsels
	#

	def value_decode(self, val):
		return val, val

	def value_encode(self, val):
		strval = str(val)
		return strval, strval

	def __init__(self, input=None):
		UserDict.__init__ (self)
		if input: self.load(input)

	def __set(self, key, real_value, coded_value):
		M = self.get(key, Morsel())
		M.set(key, real_value, coded_value)
		UserDict.__setitem__(self, key, M)

	def __setitem__(self, key, value):
		rval, cval = self.value_encode(value)
		self.__set(key, rval, cval)

	def output(self, attrs=None, header="Set-Cookie:", sep="\n"):
		result = []
		for K,V in sorted (self.items ()):
			result.append( V.output(attrs, header) )
		return sep.join(result)

	__str__ = output

	def __repr__(self):
		L = []
		for K,V in sorted (self.items ()):
			L.append( '%s=%s' % (K,repr(V.value) ) )
		return '<%s: %s>' % (self.__class__.__name__, _spacejoin(L))

	def js_output(self, attrs=None):
		result = []
		for K,V in sorted (self.items ()):
			result.append( V.js_output(attrs) )
		return _nulljoin(result)

	def load(self, rawdata):
		if type(rawdata) == type(""):
			self.__ParseString(rawdata)
		else:
			self.update(rawdata)
		return

	def __ParseString(self, str, patt=_CookiePattern):
		i = 0            # Our starting point
		n = len(str)     # Length of string
		M = None         # current morsel

		while 0 <= i < n:
			# Start looking for a cookie
			match = patt.search(str, i)
			if not match: break          # No more cookies

			K,V = match.group("key"), match.group("val")
			i = match.end(0)

			# Parse the key, value in case it's metainfo
			if K[0] == "$":
				# We ignore attributes which pertain to the cookie
				# mechanism as a whole.  See RFC 2109.
				# (Does anyone care?)
				if M:
					M[ K[1:] ] = V
			elif K.lower() in Morsel._reserved:
				if M:
					M[ K ] = _unquote(V)
			else:
				rval, cval = self.value_decode(V)
				self.__set(K, rval, cval)
				M = self[K]
	# end __ParseString
# end BaseCookie class

class SimpleCookie(BaseCookie):
	def value_decode(self, val):
		return _unquote( val ), val
	def value_encode(self, val):
		strval = str(val)
		return strval, _quote( strval )

class SerialCookie(BaseCookie):
	def __init__(self, input=None):
		BaseCookie.__init__(self, input)
	def value_decode(self, val):
		return loads( _unquote(val) ), val
	def value_encode(self, val):
		return val, _quote( dumps(val) )

class SmartCookie(BaseCookie):
	def __init__(self, input=None):
		BaseCookie.__init__(self, input)
	def value_decode(self, val):
		strval = _unquote(val)
		try:
			return loads(strval), val
		except:
			return strval, val
	def value_encode(self, val):
		if type(val) is str:
			return val, _quote(val)
		else:
			return val, _quote( dumps(val) )
