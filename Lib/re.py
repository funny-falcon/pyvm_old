#
# high level wrapper of the builtin _re module
#

from binascii import evalstr

import _re

S = DOTALL = _re.DOTALL
M = MULTILINE = _re.MULTILINE
I = IGNORECASE = _re.IGNORECASE
X = VERBOSE = _re.VERBOSE

def mk_template (s):
	# We get a string with backreferences '% \1' and convert it to
	# a string interpolation template '%% %(1)s'. Then we return a
	# function which substitutes the groups of the match in this
	# string. In order for this to work the match object must
	# support getitem as:
	#	M [x] == M.group (x)
	# that's nice and we'd do it even if it wasn't needed by this
	# code. The interpolation additionally requires that: if 'x' is
	# a string and x.isdigit(), convert to integer.
	#
	more_complex = False
	i = 0
	while 1:
		i = s.find ('\\', i)
		if i == -1:
			break
		i += 1
		if not s [i].isdigit ():
			more_complex = True
			break
	if more_complex:
		raise NotImplemented ("sub (replacement-with-escaped-chars)")

	s = s.replace ('%', '%%')
	def mapnum (M):
		return '%%(%s)s' %M.group (1)[1:]
	s = backref_to_mapping.sub (mapnum, s)
	return lambda M: s % M

def template_escape (s):
	# in sub the replacement may use \1, \2 for groups
	# convert to function
	e = 0
	for i in s:
		if i == '\\':
			e += 1
		else:
			if e % 2:
				if i.isdigit ():
					return mk_template (s)
				if i == 'g':
					raise NotImplemented ("\\g in replacement")
			e = 0
	return evalstr (s)

class Regex:
	def __init__ (self, ire, pattern):
		self._match = ire.match
		self._search = ire.search
		self.pattern = pattern
		self._reg = ire
	def search (self, string, start=0, endpos=None):
		return self._search (string, start, endpos)
	def match (self, string, start=0, endpos=None):
		return self._match (string, start, endpos)
	def findalliter (self, string):
		return self._reg.findalliter (string)
	def findall (self, string, pos=0, endpos=None):
		# X: this is wrong for groups > 1
		# This thing with the number of subgroups is horribly uncomprehensible
		L = []
		ng = self._reg.ngroup ()
		if ng == 1:
			if endpos == None: endpos = len (string)
			while 1:
				M = self._search (string, pos, endpos)
				if not M:
					break
				L.append (M.group ())
				pos = M.end ()
		elif ng <= 2:
			n = self._reg.ngroup ()-1
			while 1:
				M = self._search (string, pos, endpos)
				if not M:
					break
				L.append (M.group (n))
				pos = M.end ()
		else:
			while 1:
				M = self._search (string, pos, endpos)
				if not M:
					break
				L.append (M.groups ())
				pos = M.end ()
		return L
	def sub(self, repl, text):
		# --UNOPTIMIZED--
		#
		# If the replacement is not a callable it may be
		# better to gather all spans in an array ('i') and
		# use a new builtin multi_replace (array_with_slices, text, repl).
		#
		if type (repl) is str and '\\' in repl:
			repl = template_escape (repl)
		if type (repl) is str:
			L = []
			pos = 0
			while 1:
				M = self._search (text, pos, None)
				if not M:
					break
				span = M.span ()
				L.append (span)
				pos = span [1]
				if span [0] == pos:
					pos += 1
			S = []
			pos = 0
			for i, j in L:
				S.append (text [pos:i])
				S.append (repl)
				pos = j
			S.append (text [pos:])
			return ''.join (S)
		else:
			L, R = [], []
			pos = 0
			while 1:
				M = self._search (text, pos, None)
				if not M:
					break
				L.append (M.span ())
				pos = M.end ()
				R.append (repl (M))
			S = []
			pos = 0
			for (i, j), r in zip (L, R):
				S.append (text [pos:i])
				S.append (r)
				pos = j
			S.append (text [pos:])
			return ''.join (S)
	def split (self, string):
		S = []
		e = pos = 0
		while 1:
			M = self._search (string, pos, None)
			if not M:
				break
			s, e = M.span ()
			S.append (string [pos:s])
			pos = e
		S.append (string [e:])
		return S

def _compile (s, f=0, dojit=False):
	if s.startswith ('(?') and s [2] in 'iLmsux':
		i = s.find (')')
		if i != -1:
			f2 = s [2:i]
			s = s [i+1:]
			for i in f2:
				if i in 'smix':
					f = f | globals()[i.upper ()]
	if f & VERBOSE:
		s = deverbose (s)
	if '\\Z' in s:
		s = dezed (s)
	if dojit:
		import rejit
		dojit = rejit.compile (s, f)
		if dojit:
			return Regex (dojit, s)
	return Regex (_re.compile (s, f), s)

compile = _compile

backref_to_mapping = compile (r'(\\\d+)')

def deverbose (p):
	# assume that the end of line is not inside a character class
	s = p.split ('\n')
	for n, l in enumerate (s):
		l = list (l.strip ())
		cc = e = 0
		R = []
		for i, c in enumerate (l):
			if c == '\\':
				e += 1
			else:
				ee, e = e % 2, 0
				if ee:
					continue
				if cc:
					if c == ']':
						cc = False
					continue
				if c == '[':
					cc = True
				elif c.isspace ():
					R.append (i)
				elif c == '#':
					l = l [:i]
					break
		for i in reversed (R):
			del l [i]
		s [n] = ''.join (l)
	return ''.join (s)

def dezed (s):
	# python's \Z is the same as perl's \z.
	# Convert \Z to \z for compatibility with SRE/PCRE
	x = 0
	while 1:
		x = s.find ('\Z', x)
		if x == -1:
			return s
		if (x - len (s[:x].rstrip ('\\'))) % 2:
			x += 2
		else:
			s = s [:x] + '\\z' + s [x+2:]

ALNUM = set ('0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')

def escape(pattern):
	"Escape all non-alphanumeric characters in pattern."
	s = list(pattern)
	for i in range(len(pattern)):
		c = pattern[i]
		if c not in ALNUM:
			if c == "\000":
				s[i] = "\\000"
			else:
				s[i] = "\\" + c
	return ''.join(s)

def match (pattern, string, flags=0):
	R = compile (pattern, flags)
	return R.match (string)

def search (pattern, string, flags=0):
	R = compile (pattern, flags)
	return R.search (string)

def findall (pattern, string):
	return compile (pattern, 0).findall (string)

def split (pattern, string):
	return compile (pattern, 0).split (string)

def sub (pattern, repl, text):
	return compile (pattern, 0).sub (repl, text)
