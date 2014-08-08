#
# EPL frontend compiler. Reads EPL source code and generates AST
#
# ToDo:
#	- better syntax errors
#	- lambda
#	- parenthesis aren't really needed in list comprehensions (hmm)
#
# Theoretically, you could run this with python provided there is
# a function 'evalconst' in a module 'pyvm_extra'.
#
import re
import itertools
from pyc import ast
from pyc import gco
from pyc.consts import CO_VARARGS, CO_VARKEYWORDS, CO_GENERATOR
from pyc.parser import intern_if_all_chars
from pyvm_extra import evalconst

def ienumerate (x):
	for i, j in itertools.izip (itertools.count (), x):
		yield i, j

isval = re.compile (r'''r?['"]|\d|\.\d''').match
issym = re.compile (r'\w').match

RESERVED = set ((
	# removed: pass, elif, exec
	# added: method, gen
	'and', 'assert', 'break', 'class', 'continue', 'def', 'del',
	'else', 'except', 'finally', 'for', 'from', 'gen', 'global', 'if',
	'import', 'in', 'is', 'lambda', 'method', 'not', 'or', 'print', 'raise',
	'return', 'try', 'while', 'yield'
))

def ttype (x):
	if isval (x):
		return '0'
	if issym (x) and x not in RESERVED:
		return 's'
	return x

#
# The prefixer is a proxy parser between the Lexer and the expression compiler.
# It takes an iterable of tokens and returns a tuple where the tokens are
# reordered in prefix. For example, if we give it "x+y*3" or iow the tuple
# ('x', '+', 'y', '*', 3) it will return ('x', 'y', 3, '*', '+')
#
# But there are many exceptions, special cases and caveats.
# Feed it some input by running "epl.py -p file-with-expressions-only"
# to see what's generated each time.
#

POWER_PRI = 4
UNARY_PRI = 5
MULDIV_PRI = 9
ADDSUB_PRI = 10
SHIFT_PRI = 11
BITAND_PRI = 12
BITOR_PRI = 13
BITXOR_PRI = 14
COMP_PRI = 15
NOT_PRI = 16
BOOLAND_PRI = 17
BOOLOR_PRI = 18
TENARY_PRI = 19
ASSIGN_PRI = 21
KW_PRI = 22
COLON_PRI = 23

NEST_PRI = 100

RBINPRI = {
	POWER_PRI: ('**',),
	UNARY_PRI: ('~',),
	MULDIV_PRI: ('*', '/', '%'),
	ADDSUB_PRI: ('+', '-'),
	SHIFT_PRI: ('>>', '<<'),
	BITAND_PRI: ('&',),
	BITOR_PRI: ('|',),
	BITXOR_PRI: ('^',),
	COMP_PRI: ('==', '!=', '<>', '<', '>', '>=', '<=', 'is', 'is not', 'in', 'not in'),
	NOT_PRI: ('not',),
	BOOLAND_PRI: ('and',),
	BOOLOR_PRI: ('or',),
	ASSIGN_PRI: ('+=', '-=', '*=', '/=', '**=', '&=', '|=', '^=', '>>=', '<<=', '='),
	COLON_PRI: (':', ':0'),
	KW_PRI: ('=kw',),
}

BINPRI = {}
for k, v in RBINPRI.items ():
	for i in v:
		BINPRI [i] = k

del k, v, i, RBINPRI

class Prefixer:

	def error (self, op):
		raise "Unexpected token \"%s\" in current context [%s] (line %i)" %(op,
			 self.state, self.it.line)

	def nesting_is (self, n):
		return self.nests [-1][1] == n

	def nesting_is_fcall (self):
		return self.nests [-1][-1] == 'f'

	def nesting_is_subsc (self):
		return self.nests [-1][-1] == 's'

	def nesting_is_tuple (self):
		m, t = self.nests [-1][-1], self.nests [-1][1]
		return (m == '' and t == '(') or (m and m in 'sFi')

	def nesting (self):
		self = self.nests [-1]
		return self [-1], self [1]

	def set_nesting (self, m, n):
		s = list (self.nests [-1])
		s [-1], s [1] = m, n
		self.nests [-1] = tuple (s)

	def checkstate (self, s, t=None):
		if self.state != s:
			self.error (t or self.current)

	# state handlers

	def binop (self, op):
		self.checkstate ('postfix')
		pri = BINPRI [op]
		self.flush (pri)
		self.stack.append ((op, pri))
		self.state = 'prefix'

	def cmpop (self, op):
		self.checkstate ('postfix')
		self.flush (COMP_PRI - 1)
		if self.stack and self.stack [-1][1] == COMP_PRI:
			L = self.stack [-1][0]
			self.stack [-1] = L + ',' + op, COMP_PRI
		else:
			self.stack.append ((op, COMP_PRI))
		self.state = 'prefix'

	def boolop (self, op):
		self.checkstate ('postfix')
		pri = BINPRI [op]
		self.flush (pri - 1)
		if self.stack and self.stack [-1][1] == pri:
			self.stack [-1] = self.stack [-1][0] + 'x', pri
		else:
			if op == 'and': op = '&&'
			else: op = '||'
			self.stack.append ((op, pri))
		self.state = 'prefix'

	def opunamb (self, op):
		self.stack.append ((op + 'p', UNARY_PRI))

	def opun (self, op):
		self.checkstate ('prefix')
		self.stack.append ((op, BINPRI [op]))

	def member (self, s):
		self.lno (self.it.line)
		self.output (s)
		self.output ('.')
		self.state = 'postfix'

	def value (self, s):
		self.checkstate ('prefix', s)
		self.output (s)
		self.state = 'postfix'

	def symbol (self, s):
		self.checkstate ('prefix', s)
		self.lno (self.it.line)
		self.output (s)
		self.state = 'postfix'

	def dot (self, s):
		self.state = 'dot'

	def _flush_asgn (self):
		a, self.asgn = self.asgn, ''
		self.output (a)

	def comma (self, s):
		self.checkstate ('postfix')
		if not self.nesting_is_tuple () and self.asgn:
			self._flush_asgn ()
		else:
			self.flush (KW_PRI)
		if self.nesting_is ('{'):
			if self.kv:
				self.kv = False
			else:
				self.error (s)
		self.commas.append (self.i)
		self.state = 'prefix'

	def nest (self, t, m=''):
		self.nests.append ((self.commas,t,self.fors, self.tenary, self.i, self.kv, self.asgn, m))
		self.state = 'prefix'
		self.commas = []
		self.kv = 0
		self.tenary = 0
		self.fors = 0
		self.asgn = ''
		self.stack.append (('', NEST_PRI))

	def unnestc (self, te):
		self.stack.pop ()
		ff = self.fors
		self.commas,ts, self.fors, self.tenary, start, self.kv, self.asgn, mod = self.nests.pop ()
		t = ts + '%i' + te + 'L'
		if t not in ('(%i)L', '[%i]L'):
			self.error (te)
		self.state = 'postfix'
		self.output (t % ff)

	def unnest (self, te, f=0):
		# This is very complicated because of tuple context 
		self.flush (KW_PRI)
		if self.asgn:
			self._flush_tup ()
			self._flush_asgn ()
		elif self.nesting ()[0] in 'Fis' and self.nesting ()[0]:
			self._flush_tup ()
		self.flush (COLON_PRI)
		self.stack.pop ()
		commas = self.commas
		N = len (self.commas)
		if not N and f:
			return
		self.commas,ts, self.fors, self.tenary, start, self.kv, self.asgn, mod = self.nests.pop ()
		t = ts + '%i' + te
		if t not in ('(%i)', '[%i]', '{%i}'):
			self.error (te)
		if mod == 's' and self.out and self.out [-1] in (':', ':0'):
			sl = self.out.pop ()
			if self.state == 'prefix':
				sl += '1'
			mod = sl
		t += mod
		if mod and mod in 'Fi': self.state = 'comprehension'
		else: self.state = 'postfix'
		if self.i - start == 1:
			N = 0
		elif not N:
			if t == '(%i)':
				return
			N = 1
		elif commas [-1] != self.i-1:
			N += 1
		self.output (t % N)

	def argz (self, op):
		if not self.nesting_is_fcall ():
			self.error (op)
		self.stack.append ((op + 'a', UNARY_PRI))

	def _flush_tup (self):
		if self.commas and self.nesting_is_tuple ():
			if self.i - self.commas [-1] > 1:
				i = 1
			else:
				i = 0
			n, self.commas = len (self.commas), []
			self.output ('(%i)'%(n+i))

	def assign (self, op):
		if self.nesting_is_fcall () and op == '=':
			self.binop ('=kw')
		else:
			if not (self.state == 'prefix' and self.commas [-1] + 1 == self.i):
				self.checkstate ('postfix')
			self._flush_tup ()
			self.asgn += '@' + op
			self.state = 'prefix'

	def colon (self, op):
		if self.tenary:
			self.checkstate ('postfix')
			self.state = 'prefix'
			self.tenary -= 1
			self.flush (TENARY_PRI)
			self.stack.pop ()
			self.stack.append (('?:', TENARY_PRI))
			return
		if not self.kv:
			self.kv = True
		else:
			self.error (op)
		if self.nesting_is ('{'):
			if self.asgn:
				self._flush_asgn ()
			self.checkstate ('postfix')
			self.state = 'prefix'
			self.flush (KW_PRI)
		elif self.nesting_is_subsc ():
			if self.state == 'prefix':
				self.opun (':0')
			else:
				if self.asgn:
					self._flush_asgn ()
				self.binop (':')
		else:
			self.error (op)

	def the (self, op):
		self.state = 'the'

	def dothe (self, s):
		self.lno (self.it.line)
		self.output (s)
		self.output ('$')
		self.state = 'postfix'

	def globaldot (self, op):
		self.checkstate ('prefix')
		self.output (op)
		self.state = 'gdot'

	def notop (self, op):
		if self.stack and self.stack [-1][0] == 'is':
			self.stack [-1] = 'is not', COMP_PRI
		else: self.opun (op)

	def notinop (self, op):
		self.state = 'notin'

	def donotin (self, op):
		self.state = 'postfix'
		self.cmpop ('not in')

	def tenary (self, op):
		self.checkstate ('postfix')
		self.flush (TENARY_PRI - 1)
		self.state = 'prefix'
		self.tenary += 1
		self.stack.append (('', NEST_PRI))

	def forop (self, op):
		if self.state != 'comprehension':
			self.checkstate ('postfix')
			m, n = self.nesting ()
			if m or n not in '[(':
				self.error (op)
			self.flush (KW_PRI)
			if self.commas:
				self.set_nesting ('', '(')
				self._flush_tup ()
			self.set_nesting ('L', n)
		if self.itr.next () [1] != '(':
			self.error ('(')
		self.fors += 1
		self.nest ('(', 'F')

	def ifop (self, op):
		self.checkstate ('comprehension')
		if self.itr.next () [1] != '(':
			self.error (op)
		self.nest ('(', 'i')

	def inop (self, op):
		if self.nesting ()[0] != 'F':
			return self.cmpop ('in')
		self._flush_tup ()
		self.state = 'prefix'

	DFA = {
		'.': {'postfix':dot, 'gdot':dot},
		'$': the,
		'+': {'prefix':opunamb, 'postfix':binop},
		'-': {'prefix':opunamb, 'postfix':binop},
		'~': opun,
		'**': {'postfix':binop, 'prefix':argz},
		'*': {'postfix':binop, 'prefix':argz},
		'/': binop, '%': binop, '&': binop, '|': binop, '^': binop,
		'<<': binop, '>>': binop,
		'is': cmpop,
		'in': {'postfix':inop, 'notin':donotin},
		'or': boolop, 'and': boolop,
		'>=': cmpop, '<=': cmpop, '==': cmpop, '!=': cmpop,
		'=': assign,
		'>': cmpop, '<': cmpop,
		'+=': assign, '-=': assign, '*=': assign, '/=': assign, '%=': assign,
		'&=': assign, '|=': assign, '^=': assign, '<<=': assign, '>>=': assign,
		'not': {'prefix':notop, 'postfix':notinop},
		',': comma,
		'?': tenary,
		':': colon,
		'[': { 'prefix':nest, 'postfix':lambda self,x:self.nest (x,'s') },
		'(': { 'prefix':nest, 'postfix':lambda self,x:self.nest (x,'f') },
		']': { 'prefix':unnest, 'postfix':unnest, 'comprehension':unnestc },
		')': { 'prefix':unnest, 'postfix':unnest, 'comprehension':unnestc },
		'{': nest,
		'}': { 'prefix':unnest, 'postfix':unnest },
		's': { 'the':dothe, 'prefix':symbol, 'dot':member },
		'for': forop,
		'if': ifop,
		'global': globaldot,
		'0': value,
	}

	def output (self, x):
		self.out.append (x)

	def flush (self, pri):
		while self.stack and self.stack [-1][1] <= pri:
			self.output (self.stack.pop ()[0])

	def do (self, it, stopat = ';'):
		self.stack = []
		self.out = []
		nests = self.nests = []
		self.state = 'prefix'
		self.fors = self.tenary = self.i = self.commas = self.kv = 0
		self.asgn = ''
		self.nest ('(')
		self.it = it
		LNO = []
		self.lno = LNO.append
		itr = self.itr = ienumerate (it)
		for self.i, i in itr:
			self.current = i
			if len (nests) == 1 and i in stopat:
				break
			j = ttype (i)
		###	print j, i, self.state
			try:
				DFA = self.DFA [j]
				if type (DFA) is not dict:
					DFA (self, i)
				else:
					DFA [self.state] (self, i)
			except:
				self.error (i)
		else:
			self.error ('EOF')
		self.unnest (')', 1)
		return self.out, LNO

	# comprehend, lambda

if __name__ == '__main__' and '-p' in sys.argv:
	from tokenize2 import Lexer
	P = Prefixer ()
	L = Lexer (open (sys.argv [2]).read ())
	while 1:
		st, _ = P.do (L)
		print st
		print _
	raise SystemExit

#
# Generate AST from prefixed expressions.
# This class takes a tuple of tokens as generated by the Prefixer
# and returns an AST tree for the expression.
#

def streval (s):
	s = evalconst (s)
	if type (s) is not str:
		return s
	return intern_if_all_chars (s)

def assignedNode (node, operation = 'OP_ASSIGN'):
	if node.__class__ is ast.Name:
		return ast.AssName (node.name, operation, node.lineno)
	if node.__class__ is ast.Getattr:
		return ast.AssAttr (node.expr, node.attrname, operation)
	if node.__class__ is ast.Tuple:
		return ast.AssTuple ([assignedNode (x, operation) for x in node.nodes], node.lineno)
	if node.__class__ is ast.List:
		return ast.AssList ([assignedNode (x, operation) for x in node.nodes], node.lineno)
	if node.__class__ in (ast.Subscript, ast.Slice):
		node.flags = operation
		return node
	##print repr (node)
	raise SyntaxError ("Can't assign to operator")

class exprcc:

	# --- ACTIONS ---

	def dodot (self):
		r = self.pop ()
		l = self.pop ()
		self.push (ast.Getattr (l, r.name))

	def dotenary (self):
		r = self.pop ()
		l = self.pop ()
		c = self.pop ()
		self.push (ast.Conditional (c, l, r))


	def dokw (self):
		r = self.pop ()
		l = self.pop ()
		self.push (ast.Keyword (l.name, r))


	def doself (self):
		N = self.pop ()
		self.push (ast.Getattr (ast.Name ('self', N.lineno), N.name))

	ACTIONS = {
		'.': dodot,
		'=kw': dokw,
		'$': doself,
		'?:': dotenary
	}

	def mkbin (N):
		def b (self):
			r = self.pop ()
			l = self.pop ()
			self.push (N ((l, r)))
		return b

	for i, j in (('*', ast.Mul), ('/', ast.Div), ('%', ast.Mod),
		  ('+', ast.Add), ('-', ast.Sub), ('<<', ast.LeftShift), 
		  ('>>', ast.RightShift), ('**', ast.Power)):
		ACTIONS [i] = mkbin (j)

	def mkun (N):
		def u (self):
			self.push (N (self.pop ()))
		return u

	for i, j in (('+p', ast.UnaryAdd), ('-p', ast.UnarySub), ('~', ast.Invert), ('not', ast.Not)):
		ACTIONS [i] = mkun (j)

	def mkbit (N):
		def b (self):
			r = self.pop ()
			l = self.pop ()
			self.push (N ([l, r]))
		return b

	for i, j in (('&', ast.Bitand), ('|', ast.Bitor), ('^', ast.Bitxor)):
		ACTIONS [i] = mkbit (j)

	def mkcmp (OP):
		N = ast.Compare
		def c (self):
			r = self.pop ()
			l = self.pop ()
			self.push (N (l, [(OP, r)]))
		return c

	for i in ('==', '!=', '<>', '<=', '>=', '<', '>', 'is', 'is not', 'in', 'not in'):
		ACTIONS [i] = mkcmp (i)

	# --- FACTIONS ---

	def mkbool (N):
		def b (self, s):
			n = len (s)
			self.S [-n:] = [N (self.S [-n:])]
		return b

	def mkcontainer (self, C, n):
		if n: self.S [-n:] = [C (self.S [-n:])]
		else: self.push (C ([]))

	def dodict (self, s):
		n = 2 * int (s [1:-1])
		if not n: return self.mkcontainer (ast.Dict, 0)
		D = []
		t = None
		for i in self.S [-n:]:
			if not t: t = i
			else:
				D.append ((t, i))
				t = None
		self.S [-n:] = [ast.Dict (D)]

	def docomp (self, s):
		n = int (s [1:-2])
		fors = self.S [-n:]
		##print fors
		n += 1
		if s [0] == '[':
			self.S [-n:] = [ast.ListComp (self.S [-n], fors)]
		else:
			for i in fors:
				i.__class__ = ast.GenExprFor
				i.iter = i.list
				del i.list
				for i in i.ifs:
					i.__class__ = ast.GenExprIf
			self.S [-n:] = [ast.GenExpr (ast.GenExprInner (self.S [-n], fors))]


	def dobrk (self, s):
		if s [-1] == ']':
			self.mkcontainer (ast.List, int (s [1:-1]))
		elif s [3] == ':':
			s = s[4:]
			st = en = None
			if not s:
				en = self.pop ()
				st = self.pop ()
			elif s == '0':
				en = self.pop ()
			elif s == '1':
				st = self.pop ()
			self.push (ast.Slice (self.pop (), 'OP_APPLY', st, en))
		elif s [-1] == 'L':
			self.docomp (s)
		else:
			r = self.pop ()
			l = self.pop ()
			self.push (ast.Subscript (l, 'OP_APPLY', (r,)))

	def dopar (self, s):
		ss = s [-1]
		if ss == ')':
			self.mkcontainer (ast.Tuple, int (s [1:-1]))
		elif ss in 'FiL':
			if ss == 'F':
				r, l = self.pop (), assignedNode (self.pop ())
				self.push (ast.ListCompFor (l, r, []))
			elif ss == 'i':
				l = self.pop ()
				self.S [-1].ifs.append (ast.ListCompIf (l))
			else:
				self.docomp (s)
		else:
			n = int (s [1:-1]) + 1
			s = self.S [-n:][1:]
			star = dstar = None
			if s and type (s [-1]) is tuple:
				star = s.pop ()
				if star [0] == '*a':
					star = star [1]
				else:
					dstar = star [1]
					if s and type (s [-1]) is tuple:
						star = s.pop ()
						if star [0] == '*a':
							star = star [1]
						else:
							raise "Error"
					else:
						star = None
			self.S [-n:] = [ast.CallFunc (self.S [-n], s, star, dstar)]
			
	def doargz (self, s):
		self.push ((s, self.pop ()))

	def doassign (self, s):
		for i in reversed (s.split ('@')[1:]):
			r = self.pop ()
			l = self.pop ()
			if i == '=':
				l = ast.Assign ([assignedNode (l)], r)
			else:
				l = ast.AugAssign (l, i, r)
			self.push (l)

	FACTIONS = {
		'&': mkbool (ast.And),
		'|': mkbool (ast.Or),
		'{': dodict,
		'[': dobrk,
		'(': dopar,
		'*': doargz,
		'@': doassign,
	}

	def domcmp (self, op):
		L = [(j, self.pop ()) for j in reversed (op.split (','))]
		L.reverse ()
		self.push (ast.Compare (self.pop (), L))
		
	for i in "<>=!":
		FACTIONS [i] = domcmp

	del mkbin, mkun, mkbit, i, j, dodot, dotenary, mkcmp, mkbool
	del doargz, dokw, dopar, domcmp, dodict, doassign, doself

	##### main loop ########

	def do (self, (pex, lno)):
		try:
			return self._do ((pex, lno))
		except:
			raise "Some error near line %i" %lno [0]

	def _do (self, (pex, lno)):
	##	print "DO:", pex, lno
		lno = iter (lno)
		self.S = S = []
		def push (x):
			S.append (x)
		def pop ():
			return S.pop ()
		self.push, self.pop = push, pop
		Name, Const = ast.Name, ast.Const
		is_val = isval
		ACTIONS, FACTIONS = self.ACTIONS, self.FACTIONS

		for i in pex:
		##	print 'next:', i, type (i);
			if i in ACTIONS:
				ACTIONS [i] (self)
			elif i [0] in FACTIONS:
				FACTIONS [i [0]] (self, i)
			else:
				if not is_val (i): push (Name (i, lno.next ()))
				else: push (Const (streval (i)))
		S, = S
		return S

	# "is,=="
	# global., lambda

#
# Toplevel statement parser. Invokes exprcc and Prefixer for expressions.
#

class eplcc:

	def __init__ (self, filename):
		from tokenize2 import Lexer
		L = self.L = Lexer (open (filename).read ())
		P = self.P = Prefixer ()
		E = self.E = exprcc ()
		Edo, Pdo = E.do, P.do
		def getexpr (t):
			return Edo (Pdo (L, t))
		self.getexpr = getexpr
		self.nextc = L.nextc
		self.ungetc = L.ungetc

		# build the dispatcher
		def NA ():
			print "NOT IMPLEMENTED STATEMENT"
		def else_error ():
			raise "SyntaxError: else without if/for/while/except at %i" % L.line
		def mkn (N):
			def f ():
				self.expect (';')
				return N ()
			return f
		self.dispatcher = {
			'{': self.compound_statement,
			';': ast.Pass,
			'if': self.if_statement,
			'while': self.while_statement,
			'return': self.return_statement,
			'yield': self.yield_statement,
			'for': self.for_statement,
			'def': self.def_statement,
			'gen': self.gen_statement,
			'class': self.class_statement,
			'with': self.with_statement,
			'try': self.try_statement,
			'@': NA,
			'break': mkn (ast.Break),
			'continue': mkn (ast.Continue),
			'del': self.del_statement,
			'global': self.global_statement,
			'import': self.import_statement,
			'from': self.from_statement,
			'assert': NA,
			'raise': self.raise_statement,
			'print': self.print_statement,
			'method': self.method_statement,
			'else': else_error,
		}

		# do it
		self.tree = ast.Module (self.translation_unit ())

	# handy

	def expect (self, t):
		if self.nextc () != t:
			raise "Syntax Error, expected %s at line %i"% (t, self.L.line)

	def mustbe (self, a, b):
		if a != b:
			raise "Syntax Error, expected %s got %s (line %i)" % (a, b, self.L.line)

	def nextis (self, t):
		try:
			if self.nextc () == t:
				return True
			self.ungetc ()
		except StopIteration:
			pass
		return False

	def next_oneof (self, *t):
		x = self.nextc ()
		if x in t:
			return x
		raise "Syntax Error in line %i, expected %s" %(self.L.line, t)

	# statement states

	def expression_statement (self):
		e = self.getexpr (';')
		if not isinstance (e, ast.Assign) and not isinstance (e, ast.AugAssign):
			e = ast.Discard (e)
		return e

	def compound_statement (self):
		S = []
		while 1:
			if self.nextis ('}'):
				return ast.Stmt (S)
			S.append (self._statement ())

	def if_statement (self):
		self.expect ('(')
		T = self.getexpr (')')
		S = self.statement ();
		if self.nextis ('else'): E = self.statement ()
		else: E = None
		return ast.If ([(T, S)], E)

	def while_statement (self):
		self.expect ('(')
		T = self.getexpr (')')
		S = self.statement ();
		if self.nextis ('else'): E = self.statement ()
		else: E = None
		return ast.While (T, S, E)

	def for_statement (self):
		self.expect ('(')
		V = assignedNode (self.getexpr (('in',)))
		I = self.getexpr (')')
		S = self.statement ();
		if self.nextis ('else'): E = self.statement ()
		else: E = None
		return ast.For (V, I, S, E)

	def with_statement (self):
		self.expect ('(')
		T = self.getexpr (')')
		return ast.With (T, None, self.statement ())

	def get_comma_expr (self, endchar):
		if self.nextis (endchar):
			return ()
		self.ungetc ()
		t = endchar + ','
		L = [self.getexpr (t)]
		while self.P.current == ',':
			a = self.getexpr (t)
			L.append (a)
		return L

	def try_statement (self):
		T = self.statement ()
		if self.next_oneof ('finally', 'except') == 'finally':
			return ast.TryFinally (T, self.statement ())
		H = []
		while 1:
			self.expect ('(')
			t = a = None
			L = self.get_comma_expr (')')
			if len (L) == 1:
				t, = L
			elif L:
				t, a = L
				a = assignedNode (a)
			H.append ((t, a, self.statement ()))
			if self.nextis ('except'):
				continue
			if self.nextis ('else'): E = self.statement ()
			else: E = None
			return ast.TryExcept (T, H, E)

	def get_defargs (self):
		# XXXXX: do checks that argument names are symbols and that
		# '$' is allowed only for methods. Right now "def foo (+,-,/)" is allowed!!
		nextc, nextis, next_oneof = self.nextc, self.nextis, self.next_oneof
		a, d, f = [], [], 0
		if not nextis (')'):
			while 1:
				n = nextc ()
				if n[0] == '*':
					a.append (nextc ())
					if n == '*': f |= CO_VARARGS
					else: f |= CO_VARKEYWORDS
				else:
					if n[0] == '(':
						t = []
						while 1:
							n = nextc ()
							if n == '$':
								n = '$' + nextc ()
							t.append (n)
							if next_oneof (')', ',') == ')':
								n = tuple (t)
								break
					elif n == '$':
						n = '$' + nextc ()
					a.append (n)
					if nextis ('='):
						d.append (self.getexpr (',)'))
						if self.P.current == ')':
							break
						continue
				if next_oneof (')', ',') == ')':
					break
		return a, d, f

	def def_statement (self):
		N, n = self.get_dotted_name ()
		if n != '(':
			self.error ('(')
		A, D, F = self.get_defargs ()
		return ast.Function (None, N, A, D, F, self.statement (), self.L.line)

	def gen_statement (self):
		F = self.def_statement ()
		F.flags |= CO_GENERATOR
		return F

	def method_statement (self):
		F = self.def_statement ()
		F.argnames.insert (0, 'self')
		return F

	def class_statement (self):
		n = self.nextc ()	# checkname
		B = []
		if self.next_oneof ('(', '{') != '{':
			B = self.get_comma_expr (')')
			self.expect ('{')
		return ast.Class (n, B, self.compound_statement (), self.L.line)

	def return_statement (self):
		if self.nextis (';'): E = ast.Const (None)
		else: E = self.getexpr (';')
		return ast.Return (E)

	def yield_statement (self):
		return ast.Yield (self.getexpr (';'))

	def raise_statement (self):
		# raise class, inst: not allowed
		if self.nextis (';'): E = None
		else: E = self.getexpr (';')
		return ast.Raise (E, None, None, self.L.line)

	def del_statement (self):
		return assignedNode (self.getexpr (';'), 'OP_DELETE')

	def print_statement (self):
		S = []
		if self.nextis (';'):
			return ast.Printnl (S, None)
		while 1:
			if self.nextis (';'):
				return ast.Print (S, None)
			S.append (self.getexpr (';,'))
			if self.P.current == ';':
				return ast.Printnl (S, None)

	def get_dotted_name (self):
		nextc = self.nextc
		n, d = nextc (), nextc ()	# check symbol
		# supposing we're called from def_statement and in method ...
		if n == '$':
			return 'self.' + d, nextc ()
		while d == '.':
			n += '.' + nextc ()
			d = nextc ()
		return n, d

	def import_statement (self):
		P = []
		nextc = self.nextc
		while 1:
			n, d = self.get_dotted_name ()
			a = None
			if d == 'as':
				a, d = nextc (), nextc ()
			P.append ((n, a))
			if d == ';':
				return ast.Import (P)
			self.mustbe (d, ',')

	def from_statement (self):
		I, d = self.get_dotted_name ()
		self.mustbe (d, 'import')
		N = []
		nextc = self.nextc
		while 1:
			n, d = nextc (), nextc ()
			a = None
			if d == 'as':
				a, d = nextc (), nextc ()
			N.append ((n, a))
			if d == ';':
				return ast.From (I, N)
			self.mustbe (d, ',')

	def global_statement (self):
		N = []
		while 1:
			N.append (self.nextc ())
			if self.next_oneof (';', ',') == ';':
				return ast.Global (N)

	def _statement (self):
		ft = self.nextc ()
		if ft in self.dispatcher:
			return self.dispatcher [ft] ()
		else:
			self.ungetc ()
			return self.expression_statement ()

	def statement (self):
		s = self._statement ()
		if not isinstance (s, ast.Stmt):
			s = ast.Stmt ([s])
		return s

	def translation_unit (self):
		S = []
		try:
			while 1:
				S.append (self._statement ())
		except StopIteration:
			pass
		return ast.Stmt (S)

def parse (filename):
	return eplcc (filename).tree

if __name__ == '__main__':
	gco.GCO.new_compiler ()
	try:
		E = eplcc (sys.argv [1])
		print repr (E.tree)
	except:
		print sys.exc_info ()
	gco.GCO.pop_compiler ()
