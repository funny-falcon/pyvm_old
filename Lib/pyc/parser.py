#
#  Copyright (C) 2005, Stelios Xanthakis
#
# This file is distributed under the terms of the GNU General Public
# License.
#

try:
	HAVEPARSERCONSTS
except:
	from parserconsts import *

try:
	set
except:
	from sets import Set as set

import sys
import string

PYVM = sys.copyright.startswith ('pyvm')

def rawstr (tok):
	if len (tok) > 5 and tok[0]==tok[1]==tok[2]:
		return tok [3:-3]
	return tok [1:-1]

def intern_if_all_chars (STR):
	if len (STR) > 15 or ' ' in STR or type (STR) is not str:
		return STR
	return intern (STR)

if not PYVM:
	def streval (tok, raw):
		if 'r' == raw:
			return rawstr (tok)
		return intern_if_all_chars (eval (raw+tok))
else:
	from binascii import evalstr
	def streval (tok, raw):
		if 'r' in raw:
			return intern_if_all_chars (rawstr (tok))
		return intern_if_all_chars (evalstr (rawstr (tok)))

#

symtable = dict ((
	('if', STMT_IF),
	('for',STMT_FOR),
	('while',STMT_WHILE),
	('return',STMT_RETURN),
	('def',STMT_DEF),
	('break',STMT_BREAK),
	('import',STMT_IMPORT),
	('try',STMT_TRY),
	('else',STMT_ELSE),
	('except',STMT_EXCEPT),
	('finally',STMT_FINALLY),
	('class',STMT_CLASS),
	('continue',STMT_CONTINUE),
	('yield',STMT_YIELD),
	('global',STMT_GLOBAL),
	('raise',STMT_RAISE),
	('from',STMT_FROM),
	('del',STMT_DEL),
	('elif',STMT_ELIF),
	('print',STMT_PRINT),
	('exec',STMT_EXEC),
	('pass',STMT_PASS),
	('assert',STMT_ASSERT),
	('with',STMT_WITH),

	('+',OP_ADD), ('-',OP_SUB), ('*',OP_MUL), ('/',OP_DIV), ('**',OP_POW),
	('&',OP_AND), ('|',OP_OR), ('^',OP_XOR), ('<<',OP_LSH), ('>>',OP_RSH),
	('~',OP_CPL), ('==',OP_EQ), ('!=',OP_NEQ), ('<>',OP_NEQ), ('>',OP_GR),
	('>=',OP_GRQ), ('<',OP_LE), ('<=',OP_LEQ), (',',OP_COMMA), ('and',OP_BAND),
	('or',OP_BOR), ('=',OP_ASSIGNMENT), ('+=',OP_IADD), ('-=',OP_ISUB),
	('*=',OP_IMUL), ('/=',OP_IDIV), ('**=',OP_IPOW), ('&=',OP_IAND),
	('|=',OP_IOR), ('^=',OP_IXOR), ('>>=',OP_IRSH), ('<<=',OP_ILSH),
	('~=',OP_ICPL), ('%',OP_MOD), ('%=',OP_IMOD), ('not',OP_NOT), ('in',OP_IN),
	('is',OP_IS), ('//',OP_FDIV), ('//=',OP_IFDIV), ('lambda', OP_LAMBDA),
	('.',OP_DOT), (':',OP_COLON), (';',OP_STMT), ('@',OP_AT), ('`',OP_BQT),
	('(',OP_OPAR), (')',OP_CPAR), ('{',OP_OBRK), ('}',OP_CBRK), ('[',OP_OSQB),
	(']',OP_CSQB), ('$', OP_SELF)
))

def inv_dict (d):
	D = {}
	for k, v in d.iteritems ():
		if v not in D:
			D [v] = k
	return D

exptable = {}

def mkexptable ():
    exptable.update (inv_dict (symtable))

################### line readers ###########################

from itertools import izip, count

#enumerate = lambda x: izip (count (), x)
enumerate1 = lambda x: izip (count (1), x)

def splitlines (string):
	return string.split ('\n')

def source_generator (source):
	for LINENO, line in enumerate1 (splitlines (source)):
		yield LINENO, line+'\n'

def readline_generator (filename):
	for LINENO, line in enumerate1 (file (filename)):
		yield LINENO, line

def line_generator (source_generator):
	for LINENO, line in source_generator:
		sline = line.lstrip ()
		if sline == '' or sline [0] == '#':
			continue
		yield LINENO, line

def rawline_generator (source_generator):
	for LINENO, line in source_generator:
		yield LINENO, line.lstrip ()
	raise SyntaxError ("Unexpected end of file")

class unyielding_generator:
	def __init__ (self, g):
		self.pushback = 0
		self.g = g
	def __call__ (self):
		for i in self.g:
			yield i
			while self.pushback:
				self.pushback = 0
				yield i
	def unyield (self):
		self.pushback = 1

##################### line tokenizers #########################
# this tokenizer kinda sucks and we should better replace it
# with the regex tokenizer from tokenize2.py
# however, this also works well with the indent.py program
# so, ...

from JITS import count_idnt

def gettk (linestr,
	    goodset = set ('abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_')):
	ii = 0
	ll = len (linestr)
	while ii < ll and linestr [ii] in goodset:
		ii += 1
	return linestr [:ii], linestr [ii:]

def getnum (linestr,
	    EDIGIT = set ('0123456789'),
	    XDIGIT = set ('0123456789abcdefABCDEF')):
	ll = len (linestr)
	if linestr.startswith ('0x'):
		ii = 2
		while ii < ll and linestr [ii] in XDIGIT:
			ii += 1
		if ii < ll and linestr [ii] in 'Ll':
			return long (linestr [:ii], 16), linestr [ii+1:]
		return int (linestr [:ii], 16), linestr [ii:]
	ii = 0
	dec = False
	while 1:
		while ii < ll and linestr [ii] in EDIGIT:
			ii += 1
		if ii < ll:
			if linestr [ii] == '.': ii += 1
			elif linestr [ii] in 'eE':
				ii += 1
				if linestr [ii] in '-+': ii+= 1
			else: break
			dec = True
			continue
		break
	if dec:
		if ii < ll and linestr [ii] == 'j':
			return complex (linestr [:ii+1]), linestr [ii+1:]
		return float (linestr [:ii]), linestr [ii:]
	if linestr [0] == '0': radix = 8
	else: radix = 10
	if ii < ll:
		if linestr [ii] in 'Ll':
			return long (linestr [:ii], radix), linestr [ii+1:]
		if linestr [ii] == 'j':
			return complex (linestr [:ii+1]), linestr [ii+1:]
	return int (linestr [:ii], radix), linestr [ii:]
def count_besc (linestr, ii):
	# Is the character at position ii escaped?
	cnt = 0
	while linestr [ii] == '\\':
		cnt += 1
		ii -= 1
	return cnt % 2
def get_rest (linestr, qtype):
	# linestr contains the rest of a tripple-quoted string?
	ii = 0
	while 1:
		ii = linestr.find (qtype, ii) + 3
		if ii == 2:
			return linestr, None
		if linestr [ii - 4] == '\\' and count_besc (linestr, ii - 4):
			ii -= 2
			continue
		return linestr [:ii], linestr [ii:]

############################ Lexical analyser ###########################


characterize = { }

for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
	characterize [i] = CHAR_TOK
for i in '0123456789':
	characterize [i] = CHAR_NUM
for i in '!@%^&*-=+|<;>,/~:.`$':
	characterize [i] = CHAR_OPR
characterize ["'"] = characterize ['"'] = CHAR_STR
characterize ['#'] = CHAR_COM
for i in '({[':
	characterize [i] = CHAR_OPN
for i in ')}]':
	characterize [i] = CHAR_CLS
characterize ['r'] = characterize ['u'] = CHAR_MAYSTR
characterize ['.'] = CHAR_MAYOPR


# the Lexer is a generator that yields tokenized statements + line info.
# additionally, the Lexer guarantees that '(', '{', '[' are properly
# paired with corresponding ')', '}', ']'. Whenever one of these opens
# it is also closed within the statement. 
# They cannot be intermixed like ([x)], either
#
# The Lexer works on a text line generator.
#

class Lexer:
	def __init__ (self, filename=None, source=None):
		if source is not None:
			self.SOURCEGEN = source_generator (source)
		else:
			self.SOURCEGEN = readline_generator (filename)
		self.LG1 = line_generator (self.SOURCEGEN)
		self.LG2 = rawline_generator (self.SOURCEGEN)

    ###################################################

	def getstk (self, linestr):
		"""Get a string token"""
		ii = 1
		zz = ''
		qt = linestr [0]
		while 1:
			ii = linestr.find (qt, ii) + 1
			if ii == 0:
				if linestr [-2] == '\\' and not count_besc (linestr, len (linestr) - 3):
					zz += linestr [:-2]
					linestr = self.SOURCEGEN.next () [1]
					ii = 0
					continue
				raise SyntaxError ("Unclosed string literal")
			if linestr [ii - 2] == '\\' and count_besc (linestr, ii - 2):
				continue
			return zz+linestr [:ii], linestr [ii:]

	def getmltk (self, linestr):
		"""Get a multi-line token from a multiline string like this comment.
	   Returns a tuple (the_string, rest_of_line, lineno)"""
		qtp = linestr [:3]
		ss, rr = get_rest (linestr [3:], qtp)
		if rr != None:
			return qtp + ss, rr, -1
		SS = qtp + ss
		for LINENO, LINE in self.SOURCEGEN:
			ss, rr = get_rest (LINE, qtp)
			if rr != None:
				return SS + ss, rr, LINENO
			SS += LINE
		raise SyntaxError ("Unclosed tripple quoted string literal")

    #########################################################

	def tokenize (self, line, LINENO,
	    gettk = gettk, 
	    characterize = characterize, symtable = symtable,
	    CNESTS={')':'(', ']':'[', '}':'{'},
	    DIGIT = set ('0123456789')):

		nestor = []
		tokens = []
		while 1:
			line = line.lstrip ()

			if not line:
				if not nestor:
					return tokens
				LINENO, line = self.LG2.next ()
				continue
			if line == '\\\n' or line == '\\\r\n':
				LINENO, line = self.LG2.next ()
				continue

			ctype = characterize [line [0]]

			if ctype >= CHAR_MAYSTR:
				if ctype == CHAR_MAYOPR:
					if not (len (line) > 1 and line [1] in DIGIT):
						tokens.append ((OP_DOT, LINENO))
						line = line [1:]
						continue
					ctype = CHAR_NUM
				else:
					if not (len (line) > 1 and line [1] in """"'"""):
						if line [1] in characterize and characterize [line [1]] == 108:
							if not (len (line) > 2 and line [2] in """"'"""):
								ctype = CHAR_TOK
							else:
								raw, line = line [:2], line [2:]
						else:
							ctype = CHAR_TOK
					else:
						raw, line = line [0], line [1:]

			if ctype <= CHAR_OPR:

				if ctype == CHAR_TOK:
					tok, line = gettk (line)
					if tok in symtable:
						tokens.append ((symtable [tok], LINENO))
					else:
						tokens.append ((SYM_BASE, intern (tok), LINENO))
					continue

				if ctype == CHAR_NUM:
					num, line = getnum (line)
					tokens.append ((VAL_BASE, num, LINENO))
					continue

				if len (line) == 1 or (len (line) >= 2 and line [:2] not in symtable):
					tokens.append ((symtable [line [0]], LINENO))
					line = line [1:]
				elif len (line) >= 3 and line [:3] in symtable:
					tokens.append ((symtable [line [:3]], LINENO))
					line = line [3:]
				else:
					tokens.append ((symtable [line [:2]], LINENO))
					line = line [2:]

				continue

			if CHAR_STR < ctype <= CHAR_CLS:
				if ctype == CHAR_OPN:
					nestor.append (line [0])
					tokens.append ((symtable [line [0]], LINENO))
					line = line [1:]
					continue
				if ctype == CHAR_CLS:
					if nestor [-1] != CNESTS [line [0]]:
						raise SyntaxError ("Bad %s nesting" % line [0])
					nestor.pop ()
					tokens.append ((symtable [line [0]], LINENO))
					line = line [1:]
					continue
				line = ''
				continue

			if ctype != CHAR_MAYSTR:
				raw = ''

			if line.startswith (3 * line [0]):
				tok, line, lineno = self.getmltk (line)
				if lineno != -1:
					LINENO = lineno
			else:
				tok, line = self.getstk (line)

			if tokens and tokens [-1][0] == STR_BASE:
				tokens [-1] = ((STR_BASE, tokens [-1][1] + streval (tok, raw), LINENO))
			else:
				tokens.append ((STR_BASE, streval (tok, raw), LINENO))

    ############## single statement generator ############

	def yield_stmt (self):
		for lno, lstr in self.LG1:
			yield count_idnt (lstr), self.tokenize (lstr, lno)

################## nested statement generator ######################

# the statement_generator is an iterable object which yields
# statements from a Lexer but also checks the correct identation.
# That's what the 'next' method does (or when invoked
# from 'for').
#
# It also has the method 'subsuite' which returns a
# new statement_generator instance which yields statements with
# deeper identation -- *from the same Lexer*
#
# Finally it has a method 'peek' which peeks into the Lexer
# to see if there is another statement with the same identation
# which starts with a certain token.
# The behaviour of 'peek' can be implemented manually with the
# "unyield" method of the statement_generator.
#

class statement_generator:
	def __init__ (self, lexer, itr = None, idlev = -1):
		if not itr:
			# toplevel statement generator
			# 'lexer' is actually the iterable that yields statements
			lexer = unyielding_generator (lexer)
			itr = lexer ()
		self.idlev = idlev
		self.lexer = lexer
		self.itr = itr
		self.next = self.generator ().next
		self.unyield = lexer.unyield
	def generator (self):
		try:
			stmt = self.itr.next ()
		except StopIteration:
			if self.idlev == -1:
				raise
			raise SyntaxError ("missing suite")
		if stmt [0] <= self.idlev:
			raise SyntaxError ("Bad identation (less)")
		idlev = self.idlev = stmt [0]
		yield stmt [1]
		for i in self.itr:
			if i [0] == idlev:
				yield i [1]
			elif i [0] < idlev:
				self.lexer.unyield ()
				return
			else:
				raise SyntaxError ("Bad identation (more)")
	def peek (self, tok):
		try:
			stmt = self.next ()
			self.unyield ()
			return stmt and stmt [0][0] == tok
		except StopIteration:
			return False
	def __iter__ (self):
		return self
	def subsuite (self):
		return statement_generator (self.lexer, self.itr, self.idlev)


# testing the statement_generator/tokenizer with a *correct* program

if 0 and __name__ == '__main__':
	def print_all (G, n=0):
		for i in G:
			print n*'\t', i
			if i[-1][0] == OP_COLON:
				print_all (G.subsuite (), n + 1)
	filename = 'ptest.py'
	print_all (statement_generator (Lexer (filename).yield_stmt ()))
	import gc
	gc.collect ()
	gc.collect ()
	raise SystemExit

############################### AST generator ################################

from consts import OP_DELETE, OP_APPLY, OP_ASSIGN, CO_VARARGS, CO_VARKEYWORDS
import ast

def assignedNode (node, operation):
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
	raise SyntaxError ("Can't assign to operator")

AUGASSIGN = {
	OP_IADD:'+=', OP_ISUB:'-=', OP_IMUL:'*=', OP_IDIV:'/=', OP_IPOW:'**=', OP_IOR:'|=',
	OP_IXOR:'^=', OP_IRSH:'>>=', OP_ILSH:'<<=', OP_ICPL:'~=', OP_IMOD:'%=', OP_IFDIV:'//=',
	OP_IAND:'&='
}

###########################################################
# ********************* DFA PARSER ***********************
#############  WARNING: Mindboggling parser ###############

def half_list (lst):
	l = []
	b = True
	for i in lst:
		if b: p = i
		else: l.append ((p, i))
		b = not b
	return l

def clauses (lst):
	for i, j in half_list (lst):
		if not len (i):
			yield None, None, j
		elif len (i) == 1:
			yield i [0], None, j
		else:
			yield i [0], assignedNode (i [1], OP_ASSIGN), j

assNode = lambda x : assignedNode (x, OP_ASSIGN)

def mergedict (D1, D2):
	d = dict (D1)
	d.update (D2)
	return d

def asnamtup (x):
	if type (x) is tuple: return x
	return x, None

#############  WARNING: Mindboggling parser ###############

# '-not x' is allowed!!!
# x[1:2:] is turned to slice and not sliceobj
# ast.{Bitand,Bitor,Bitxor,And,Or} must complain if their list has just 1 element
# ast.CallFunc must check that there are no args after keyword args
# problem with x[1:,2] at the comma

class DFA_parser:
	# never put a human to do a computer's job
	Lexer_class = Lexer
	st0 = None

	def __init__ (self, filename, source, isexpr=False):
		self.stack = []
		self.pending = []
		self.pendings = []
		self.dfas = []
		if isexpr:
			expr = Lexer (filename=None, source=source).yield_stmt ().next () [1]
			self.outcome, more = self.parse_expr (expr)
			if more:
				self.error ("Multiple expressions in eval")
			return

		self.STG = statement_generator (self.Lexer_class (filename=filename, source=source).yield_stmt ())
		self.globals = []
		self.generators = []
		self.bqt = self.mlcnt = 0
		self.tnest = self.ingen = self.st0 = self.DFA0 = self.DFATRAIL = self.DFALINE = None
		self.forfail = None
		self.flushl = self.flushl
		self.flush = self.flush
		self.parse (self.STG)
		assert len (self.stack) == 1
		self.outcome = ast.Module (self.stack [0])
		# circular references
		del self.flushl
		del self.flush

	def error (self, msg = None):
		if not exptable:
			mkexptable ()
		if not msg:
			if self.current [0] in exptable:
				tk = exptable [self.current [0]]
			else: tk = self.current [1]
			msg = "DFA(%s) unexpected token '%s' in line %i"%(
				self.dfa [NAME_OF_DFA], tk, self.current [-1])
		else:
			msg = 'Line %i:%s' % (self.current [-1], msg)
		raise SyntaxError (msg)

	def nest (self, dfa0=0, dfa_trail=0, nest=None, forfail=None):
		self.pendings.append (self.pending)
		self.pending = []
		self.dfas.append ((self.DFA0, self.DFATRAIL, self.DFALINE, self.st0, self.ingen,
				 self.tnest, self.forfail))
		self.tnest = nest
		self.dfa = self.DFA0 = dfa0
		self.DFATRAIL = dfa_trail
		self.forfail = forfail

	def unnest (self):
#		self.flush (ENDALL_PRI)
		self.pending = self.pendings.pop ()
		self.DFA0, self.DFATRAIL, self.DFALINE, self.st0, self.ingen, self.tnest, self.forfail\
		 = self.dfas.pop ()

	def flush (self, pri):
		while self.pending and self.pending [-1][2] <= pri:
			x = self.pending.pop ()
			x [0] (*x [1])

	def flushl (self, pri):
		while self.pending and self.pending [-1][2] < pri:
			x = self.pending.pop ()
			x [0] (*x [1])

    # ////// exec stack entries ///////
    # these functions are placed on the self.pending along with their priority (this whole
    # DFA parser is based on the PRIORITY values).  When flush() is called, they are executed
    # and pop things from the self.stack and push new things afterwards.

	def do_unaryop (self, astnode):
		self.stack [-1] = astnode (self.stack [-1])

	def do_binop (self, astnode):
		right = self.stack.pop ()
		self.stack [-1] = astnode ((self.stack [-1], right))

	def do_bitop (self, astnode, stk):
		self.stack [stk:] = [astnode (self.stack [stk:])]

	def do_cmpop (self, lno, stk):
		self.stack [stk:] = [ast.Compare (self.stack [stk], half_list (self.stack [stk+1:]), lno)]

	def do_kw (self, lno):
		v = self.stack.pop ()
		if v.__class__ == ast.Keyword or self.stack [-1].__class__ != ast.Name:
			self.error ("invalid keyword argument")
		self.stack [-1] = ast.Keyword (self.stack [-1].name, v, lno)

	def do_slice (self, n0, n1, n2):
		self.stack.append (ast.Sliceobj ([n0, n1, n2]))

	def do_del (self, lno):
		self.stack [-1] = assignedNode (self.stack [-1], OP_DELETE)

	def topif (self, x):
		if x: return self.stack.pop ()
		return None

	def do_while (self, lno, stk):
		el = self.topif (len (self.stack) - stk == 3)
		st = self.stack.pop ()
		self.stack [-1] = ast.While (self.stack [-1], st, el, lno)

	def do_with (self, lno):
		self.stack [-2:] = [ast.With (self.stack [-2], None, self.stack [-1], lno)]

	def do_stmt (self, stk):
		self.stack [stk:] = [ast.Stmt (self.stack [stk:])]

	def do_if (self, lno, stk):
		el = self.topif ((len (self.stack) - stk) % 2)
		self.stack [stk:] = [ast.If (half_list (self.stack [stk:]), el, lno)]

	def do_for (self, lno, stk):
		el = self.topif (len (self.stack) - stk == 4)
		self.stack [stk:] = [ast.For (assignedNode (self.stack [stk], OP_ASSIGN),
				 self.stack [stk + 1], self.stack [stk + 2], el)]

	def do_try (self, lno, stk):
		n = len (self.stack) - stk
		if n == 2:
			self.stack [stk:] = [ast.TryFinally (self.stack [-2], self.stack [-1], lno)]
		else:
			el = self.topif (not n % 2)
			self.stack [stk:] = [ast.TryExcept (self.stack [stk],
			 list (clauses (self.stack [stk+1:])), el)]

	def do_aug (self, op, lno):
		lv = self.stack.pop ()
		self.stack [-1] = ast.AugAssign (self.stack [-1], AUGASSIGN [op], lv, lno)

	def do_ass (self, lno, stk):
		lv = self.stack.pop ()
		self.stack [stk:] = [ast.Assign (map (assNode, self.stack [stk:]), lv, lno)]

	def do_global (self, lno):
		self.stack [-1] = ast.Global (self.stack [-1], lno)

	def do_import (self, lno, stk):
		self.stack [stk:] = [ast.Import ([asnamtup (i) for i in self.stack [stk:]], lno)]

	def do_from (self, lno, stk):
		self.stack [stk:] = [ast.From (self.stack [stk],
				 [asnamtup (i) for i in self.stack [stk+1:]], lno)]

	def do_asrt (self, lno, stk):
		n2 = self.topif (len (self.stack) - stk == 2)
		self.stack [-1] = ast.Assert (self.stack [-1], n2, lno)

	def do_raise (self, lno, stk):
		n = len (self.stack) - stk
		n3, n2, n1 = self.topif (n == 3), self.topif (n >= 2), self.topif (n)
		self.stack.append (ast.Raise (n1, n2, n3, lno))

	def do_gfor (self, lno, stk):
		if self.tnest == '[': ctor = ast.ListCompFor
		else: ctor = ast.GenExprFor
		ifs, n2, self.stack = self.stack [stk+2:], self.stack [stk + 1], self.stack [:stk+1]
		self.stack [-1] = ctor (assignedNode (self.stack [-1], OP_ASSIGN), n2, ifs, lno)

	def do_gexp (self, stk, lno):
		self.ingen = 0
		if self.tnest == '[':
			self.stack [stk:] = [ast.ListComp (self.stack [stk], self.stack [stk+1:], lno)]
		else: self.stack [stk:] = [ast.GenExpr (ast.GenExprInner (self.stack [stk],
				 self.stack [stk+1:]), lno)]

	def do_gif (self, lno):
		if self.tnest == '[': self.stack [-1] = ast.ListCompIf (self.stack [-1], lno)
		else: self.stack [-1] = ast.GenExprIf (self.stack [-1], lno)

	def do_cls (self, lno, stk):
		self.stack [stk:] = [ast.Class (self.stack [stk], self.stack [stk+1:-1], self.stack [-1], lno)]

	def do_exec (self, lno, stk):
		n = len (self.stack) - stk
		lc = self.topif (n == 3)
		gl = self.topif (n >= 2)
		self.stack [-1] = ast.Exec (self.stack [-1], gl, lc, lno)

	def do_bqt (self):
		self.stack [-1] = ast.Backquote (self.stack [-1])

    # ////// DFA entry points ///////
    # usually, we try to make those entry points very independent and small;
    # they usually only set up the next DFA and optionally add a handler
    # to the pending handlers.  occasionaly, they may also flush the
    # pending stack.
    # entries that return a true value force the main loop to re-run
    # the current token with the new DFA.
    #
    # yet, some entry points may manipulate the stack, although that should be rare.
    # this definitelly happens for entry points which terminate 'postfix operators'.
    #
    # in order to compress the size of the program somewhat, in some cases the behaviour
    # of a DFA entry point depends on the current state of the instance.  Members that
    # matter to this are self.mlcnt and self.tnest; with these two we manage to compress
    # list_comprehensions+generator_expressions in the same DFA, and raise+assert+return
    # in the same DFA as well.  We also use self.okdfa for DFA_NAME.  But such hacks
    # should be avoided if we want the code to remain deterministic.

	def unaryop (self, astnode, pri = UNARY_PRI):
		self.pending.append ((self.do_unaryop, (astnode,), pri))

	def symbol (self):
		self.stack.append (ast.Name (self.current [1], self.current [2]))
		self.dfa = self.DFATRAIL

	def constant (self):
		self.stack.append (ast.Const (self.current [1], self.current [2]))
		self.dfa = self.DFATRAIL

	def dotop (self):
		self.dfa = self.DFA_MEMBER

	def member (self):
		self.dfa = self.DFATRAIL
		self.stack [-1] = ast.Getattr (self.stack [-1], self.current [1])

	def binop (self, pri, astnode):
		self.flush (pri)
		self.pending.append ((self.do_binop, (astnode,), pri))
		self.dfa = self.DFA0

	def power (self):
		self.flushl (POWER_PRI)
		self.pending.append ((self.do_binop, (ast.Power,), POWER_PRI))
		self.dfa = self.DFA0

	def bitop (self, pri, astnode):
		self.flushl (pri)
		if not (self.pending and self.pending [-1][2] == pri):
			self.pending.append ((self.do_bitop, (astnode, len (self.stack) -1),
				pri))
		self.dfa = self.DFA0

	def cmpop (self, cmpf):
		self.flushl (COMP_PRI)
		if not (self.pending and self.pending [-1][2] == COMP_PRI):
			self.pending.append ((self.do_cmpop, (self.current [-1], len (self.stack) - 1),
				 COMP_PRI))
		self.stack.append (cmpf)
		self.dfa = self.DFA0

	def notin (self):
		self.dfa = self.DFA_NOTIN

	def isop (self):
		self.dfa = self.DFA_ISOP

	def not_isnot (self):
		self.cmpop ('is')
		return 1

		# --* function call - argument list *--

	def opar (self):
		self.nest (self.DFA_0, self.DFA_TESTGENFOR, forfail=self.DFA_TRAIL)
		self.dfa = self.DFA_ISETUP

	def cpar (self):
		self.eos ()
		self.unnest ()
		self.dfa = self.DFATRAIL

	def fcall (self):
		self.stack.append ([[], None, None, self.current [1]])
		self.nest (self.DFA_0ARGL, self.DFA_TESTGENFOR_CALL, forfail = self.DFA_TRAILARGL)

	def acomma (self):
		self.flush (LSTMT_PRI)

		x = self.stack.pop ()
		self.stack [-1][0].append (x)
		self.dfa = self.DFA0

	def akw (self):
		self.flushl (COMMA_PRI)
		self.pending.append ((self.do_kw, (self.current [1],), KW_PRI))
		self.dfa = self.DFA0

	def do_call (self):
		self.unnest ()
		argl = self.stack.pop ()
		self.stack [-1] = ast.CallFunc (self.stack [-1], *argl)
		self.dfa = self.DFATRAIL

	def cparf (self):
		self.acomma ()
		self.do_call ()

	def dstar (self):
		self.dfa = self.DFA0 = self.DFA_0ARGLkw
		self.DFATRAIL = self.DFA_TRAILARGLkw

	def star (self):
		self.dfa = self.DFA0 = self.DFA_0ARGLva
		self.DFATRAIL = self.DFA_TRAILARGLva

	def cparfkw (self, i=2):
		self.flushl (COMMA_PRI)
		x = self.stack.pop ()
		self.stack [-1][i] = x
		self.do_call ()

	cparfva = lambda self: self.cparfkw (1)

	def vacomma (self):
		self.flushl (COMMA_PRI)
		x = self.stack.pop ()
		self.stack [-1][1] = x
		self.dfa = self.DFA_KW

	def eos (self, p = END_PRI):
		self.flush (p)

		# --* some DFAs *--

	def not_genfor (self):
		self.dfa = self.DFA_TRAIL
		return 1

	def stop_genfor (self):
		self.dfa = self.DFATRAIL = self.forfail
		return 1

	def noetup (self):
		self.dfa = self.DFA0
		return 1

	def nonoarg (self):
		self.dfa = self.DFA0
		return 1

	def noarg (self):
		self.unnest ()
		self.stack [-1] = ast.CallFunc (self.stack [-1], [], None, None, self.current [1])
		self.dfa = self.DFATRAIL

		# --* small statements *--

	def rdsml (self):
		self.dfa = self.DFA0 = self.DFA_0_SMALL
		self.DFATRAIL = self.DFA_TRAIL_SMALL
		return 1

	def rdexp (self):
		self.dfa = self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILASS
		self.pending.append ((self.do_unaryop, (ast.Discard,), DISCARD_PRI))
		return 1

	def tlhandle (self):
		self.DFA0 = self.DFA_0_SMALL
		self.dfa = self.DFATRAIL = self.DFA_TRAIL_SMALL
		return 1

	def sstmt (self, astnode):
		self.stack.append (astnode (self.current [1]))
		self.dfa = self.DFATRAIL = self.DFA_TRAIL_SMALL

	def yld_stmt (self):
		self.dfa = self.DFA_YLD

	def yld_stmta (self):
		# "yield *expr" form
		self.dfa = self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILEXP
		self.pending.append ((self.do_unaryop, (ast.YieldIter,), SSTMT_PRI))

	def yld_stmtc (self):
		self.dfa = self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILEXP
		self.pending.append ((self.do_unaryop, (ast.Yield,), SSTMT_PRI))
		return 1

	def rtn_stmt (self):
		self.mlcnt = 0
		self.dfa = self.DFA_MAYEXPR
		self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILEXP
		self.pending.append ((self.do_unaryop, (ast.Return,), SSTMT_PRI))

	def dflt (self):
		self.dfa = self.DFA0
		return 1

	def noexp (self):
		# This is used by: return, raise and print
		if not self.mlcnt:
			self.stack.append (ast.Const (None))
		elif self.mlcnt > 10:
			self.stack.append ('\n')
		return self.tlhandle ()

		# --* compound statements *--

	def add_small (self):
		self.flush (SSTMT_PRI)
		self.dfa = self.DFA_0_SMALL

	def whl_stmt (self):
		self.dfa = self.DFA0 = self.DFA_0NEEDEXPR
		self.DFATRAIL = self.DFA_TRAILSEXP
		self.pending.append ((self.do_while, (self.current [1], len (self.stack)), CSTMT_PRI))
		self.st0 = STMT_WHILE

	def if_stmt (self):
		self.dfa = self.DFA0 = self.DFA_0NEEDEXPR
		self.DFATRAIL = self.DFA_TRAILSEXP
		self.pending.append ((self.do_if, (self.current [1], len (self.stack)), CSTMT_PRI))
		self.st0 = STMT_IF

	def for_stmt (self):
		self.dfa = self.DFA0 = self.DFA_0NEEDEXPR
		self.DFATRAIL = self.DFA_TRAILFEXP
		if self.ingen:
			self.pending.append ((self.do_gfor, (self.current [1], len (self.stack)), SSTMT_PRI))
		else:
			self.pending.append ((self.do_for, (self.current [1], len (self.stack)), CSTMT_PRI))
		self.st0 = STMT_FOR

	def try_stmt (self):
		self.dfa = self.DFA_COLONSUITE
		self.pending.append ((self.do_try, (self.current [1], len (self.stack)), CSTMT_PRI))
		self.st0 = STMT_TRY

	def infor (self):
		self.flush (COMMA_PRI)
		self.dfa = self.DFA0 = self.DFA_0NEEDEXPR
		if self.ingen: self.DFATRAIL = self.DFA_TRAILFORIF
		else: self.DFATRAIL = self.DFA_TRAILSEXP

	def suite0 (self):
		self.flush (ASSIGN_PRI)
		self.dfa = self.DFA_MAYSUITE

	def push_subsuite (self):
		self.parse (self.generators [-1].subsuite ())
		self.DFALINE = self.DFA_SUITE2

	def line_subsuite (self):
		self.dfa = self.DFA_0_SMALL
		self.DFATRAIL = self.DFA_TRAIL_SMALL
		self.DFALINE = self.DFA_FLUSHL
		self.pending.append ((self.do_stmt, (len (self.stack),), LSTMT_PRI))
		return 1

	def dflt_tl (self):
		self.flush (CSTMT_PRI)
		self.dfa = self.DFALINE = self.DFA_TOPLEV
		return 1

	def stelse (self):
		if self.st0 not in (STMT_WHILE, STMT_ELIF, STMT_FOR, STMT_EXCEPT, STMT_IF):
			self.error ()
		self.dfa = self.DFA_COLONSUITE
		self.st0 = STMT_ELSE

	def stelif (self):
		if self.st0 not in (STMT_ELIF, STMT_IF):
			self.error ()
		self.dfa = self.DFA0 = self.DFA_0NEEDEXPR
		self.DFATRAIL = self.DFA_TRAILSEXP
		self.st0 = STMT_ELIF

	def stfin (self):
		if self.st0 != STMT_TRY:
			self.error ()
		self.dfa = self.DFA_COLONSUITE
		self.st0 = STMT_FINALLY

	def stexc (self):
		if self.st0 not in (STMT_EXCEPT, STMT_TRY):
			self.error ()
		self.stack.append ([])
		self.dfa = self.DFA_EXC1
		self.st0 = STMT_EXCEPT

	def dflush (self):
		self.flush (LSTMT_PRI)
		self.dfa = self.DFA_SUITE2
		return 1

	def exc00 (self):
		self.dfa = self.DFA0 = self.DFA_0NEEDEXPR
		self.DFATRAIL = self.DFA_TRAILx0EXP
		return 1

	def exc01 (self):
		self.suite0 ()
		x = self.stack.pop ()
		self.stack [-1].append (x)

	def exc11 (self):
		x = self.stack.pop ()
		self.stack [-1].append (x)
		self.dfa = self.DFA0 = self.DFA_0NEEDEXPR
		self.DFATRAIL = self.DFA_TRAILx1EXP

		# --* assignments *--

	def augass (self):
		self.flushl (DISCARD_PRI)
		if self.pending [-1][2] == DISCARD_PRI:
			self.pending.pop ()
		self.pending.append ((self.do_aug, self.current, ASSIGN_PRI))
		self.DFATRAIL = self.DFA_TRAILEXP
		self.dfa = self.DFA0 = self.DFA_0	# redux?

	def assign (self):
		self.flushl (DISCARD_PRI)
		if not (self.pending and self.pending [-1][2] == ASSIGN_PRI):
			self.pending [-1] = (self.do_ass, (self.current [1], len (self.stack)-1), ASSIGN_PRI)
		self.DFATRAIL = self.DFA_TRAILASG
		self.dfa = self.DFA0 = self.DFA_0	# redux?

	def del_stmt (self):
		self.pending.append ((self.do_del, (self.current [1],), SSTMT_PRI))
		self.DFATRAIL = self.DFA_TRAILEXP
		self.dfa = self.DFA0 = self.DFA_0	# redux?

		# --* global *--

	def glb_stmt (self):
		self.pending.append ((self.do_global, (self.current [1],), SSTMT_PRI))
		self.stack.append ([])
		self.dfa = self.DFA_GLOB0

	def gatom (self):
		self.dfa = self.DFA_GLOBEX

	def gexdot (self):
		self.dfa = self.DFA_GLOBNAM

	def gdot (self):
		self.stack.pop ()
		self.pending.pop ()
		self.dfa = self.DFA_GLOBATTR

	def gmemb (self):
		self.globals.append (self.current [1])
		self.dfa = self.DFA_0_SMALL
		return 1

	def gexmemb (self):
		self.globals.append (self.current [1])
		self.dfa = self.DFA_0
		return 1

	def gname (self):
		self.stack [-1].append (self.current [1])
		self.dfa = self.DFA_GLOB1

	def dflt_tr (self):
		self.dfa = self.DFATRAIL
		return 1

	def gnext (self):
		self.dfa = self.DFA_GLOB0

		# --* imports *--

	def imp_stmt (self):
		self.pending.append ((self.do_import, (self.current [1], len (self.stack)), SSTMT_PRI))
		self.dfa = self.DFA_NAME
		self.okdfa = self.DFA_IMP1

	def dotnam (self):
		self.dfa = self.DFA_IMP2

	def impnam2 (self):
		self.stack [-1] += '.' + self.current [1]
		self.dfa = self.DFA_IMP1

	def asname (self):
		if self.current [1] != 'as':
			self.error ()
		self.dfa = self.DFA_IMP3

	def impasnam (self):
		self.stack [-1] = (self.stack [-1], self.current [1])
		self.dfa = self.DFA_IMP4

	def impnext (self):
		self.dfa = self.DFA_NAME
		self.okdfa = self.DFA_IMP1

	def frm_stmt (self):
		self.pending.append ((self.do_from, (self.current [1], len (self.stack)), SSTMT_PRI))
		self.dfa = self.DFA_NAME
		self.okdfa = self.DFA_FROM1

	def fromimp (self):
		self.dfa = self.DFA_FROM2

	def allfrom (self):
		self.stack.append (('*', None))
		self.dfa = self.DFATRAIL

	def frmdot (self):
		self.dfa = self.DFA_FROM3

	def frmdotn (self):
		self.stack [-1] += '.' + self.current [1]
		self.dfa = self.DFA_FROM1

	def frmnames (self):
		self.stack.append (self.current [1])
		self.dfa = self.DFA_FROM4

	def frmnmsep (self):
		if self.current [1] != 'as':
			self.error ()
		self.dfa = self.DFA_FROM5

	def frmasnam (self):
		self.stack [-1] = (self.stack [-1], self.current [1])
		self.dfa = self.DFA_FROM6

	def nextfromnam (self):
		self.dfa = self.DFA_NAME
		self.okdfa = self.DFA_FROM4

		# --* asserts & raise *--

	def asrt_stmt (self):
		self.pending.append ((self.do_asrt, (self.current [1], len (self.stack)), SSTMT_PRI))
		self.mlcnt = 1
		self.dfa = self.DFA_0NEEDEXPR
		self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILmlEXP	 # restore old DFATRAIL ?

	def raise_stmt (self):
		self.pending.append ((self.do_raise, (self.current [1], len (self.stack)), SSTMT_PRI))
		self.mlcnt = 2
		self.dfa = self.DFA_MAYEXPR
		self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILmlEXP	 # restore old DFATRAIL ?

	def mlcoma (self):
		if not self.mlcnt:
			self.error ()
		self.flush (COMMA_PRI)
		self.mlcnt -= 1
		if self.mlcnt < 100: self.dfa = self.DFA_0NEEDEXPR
		else: self.dfa = self.DFA_MAYEXPR
		self.DFATRAIL = self.DFA_TRAILmlEXP

		# --* listen comprehensionen und generatorsprahen expressionen *--

	def genfor (self):
		self.eos ()
		self.pending.append ((self.do_gexp, (len (self.stack) - 1, self.current [1]), LSTMT_PRI))
		self.ingen = 1
		self.dfa = self.DFA_FORIF
		return 1

	def morefor (self):
		self.flush (SSTMT_PRI)
		self.dfa = self.DFA_FORIF
		return 1

	def moreif (self):
		self.flush (GENIF_PRI)
		self.pending.append ((self.do_gif, (self.current [1],), GENIF_PRI))
		self.dfa = self.DFA_0NEEDEXPR

	def endlch (self):
		self.eos ()
		self.unnest ()
		self.pending.pop ()
		self.dfa = self.DFATRAIL

		# --* dict/list makers  *--

	def ocbr (self):
		# OK????
		self.pending.append ((len (self.stack), self.current [1]))
		self.nest (self.DFA_0, self.DFA_TRAILDICT1)
		self.dfa = self.DFA_EDICT

	def sepok (self):
		self.eos ()
		self.dfa = self.DFA0
		self.DFATRAIL = self.DFA_TRAILDICT2

	def sep2ok (self):
		self.eos ()
		self.dfa = self.DFA0
		self.DFATRAIL = self.DFA_TRAILDICT1

	def ccbr (self):
		self.eos ()
		self.unnest ()
		stk, lno = self.pending.pop ()
		self.stack [stk:] = [ast.Dict (tuple (half_list (self.stack [stk:])), lno)]
		self.dfa = self.DFATRAIL

	def edict (self, astnode = ast.Dict):
		self.unnest ()
		self.pending.pop ()
		self.stack.append (astnode ((), self.current [1]))
		self.dfa = self.DFATRAIL

	elist = lambda self: self.edict (ast.List)

	def osqb (self):
		# OK???
		self.pending.append ((len (self.stack), self.current [1]))
		self.nest (self.DFA_0, self.DFA_TESTGENFOR, forfail = self.DFA_TRAILLIST)
		self.tnest = '['
		self.dfa = self.DFA_EDICT

	def csqb (self):
		self.eos ()
		self.unnest ()
		stk, lno = self.pending.pop ()
		self.stack [stk:] = [ast.List (tuple (self.stack [stk:]), lno)]
		self.dfa = self.DFATRAIL

	def lsepok (self):
		self.eos ()
		self.dfa = self.DFA0

	def etup (self):
		self.unnest ()
		self.stack.append (ast.Tuple ((), self.current [1]))
		self.dfa = self.DFATRAIL

	def class_stmt (self):
		self.pending.append ((self.do_cls, (self.current [1], len (self.stack)), CSTMT_PRI))
		self.dfa = self.DFA_NAME
		self.okdfa = self.DFA_CLBASE

	def cbase0 (self):
		self.mlcnt = -1
		self.dfa = self.DFA_0NEEDEXPR
		self.DFATRAIL = self.DFA_TRAILmlEXP	 # restore old DFATRAIL ?

	def nbase (self):
		self.dfa = self.DFA_COLONSUITE

	def okname (self):
		self.stack.append (self.current [1])
		self.dfa = self.okdfa

		# --* funcdef *--

	def fdef (self, decos = None):
		self.stack.append (decos)
		self.dfa = self.DFA_NAME
		self.okdfa = self.DFA_FUNCP

	def lambdef (self):
		self.vargl ()
		self.tnest = OP_LAMBDA

	def vargl (self):
		self.stack.append ([[], [], 0])
		self.nest (self.DFA_FARG)

	def parg (self):
		self.stack [-1][0].append (self.current [1])
		self.dfa = self.DFA_ARGSEP

	def do_def (self, lno):
		if self.globals:
			self.stack [-1].add_globals (self.globals)
			self.globals = []
		self.stack [-4:] = [ast.Function (self.stack [-4], self.stack [-3], self.stack [-2][0],
			 self.stack [-2][1], self.stack [-2][2], self.stack [-1], lno)]

	def do_lamb (self, lno):
		self.stack [-2:] = [ast.Lambda (self.stack [-2][0], self.stack [-2][1],
				self.stack [-2][2], self.stack [-1], lno)]

	def lambend (self):
		if self.tnest != OP_LAMBDA:
			self.error ()
		self.unnest ()
		self.pending.append ((self.do_lamb, (self.current [1],), LAMBDA_PRI))
		self.dfa = self.DFA0

	def vaend (self):
		self.unnest ()
		self.pending.append ((self.do_def, (self.current [1],), CSTMT_PRI))
		self.dfa = self.DFA_COLONSUITE

	def vsep (self):
		if self.stack [-1][1]:
			self.error ("Non-kwarg follows kwarg")
		self.dfa = self.DFA_FARG

	def vatup (self):
		self.stack.append (0x1234)
		self.stack.append ([])
		self.dfa = self.DFA_ARGTUP

	def vvtup (self):
		self.stack.append ([])

	def vtp1 (self):
		self.stack [-1].append (self.current [1])
		self.dfa = self.DFA_ARGTUP2

	def vtp2 (self):
		self.dfa = self.DFA_ARGTUP

	def vtend (self):
		if self.stack [-2] != 0x1234:
			self.dfa = self.DFA_ARGTUP2
			x = tuple (self.stack.pop ())
			self.stack [-1].append (x)
		else:
			self.dfa = self.DFA_ARGSEP
			x = tuple (self.stack.pop ())
			self.stack.pop ()
			self.stack [-1][0].append (x)

	def kwdef (self):
		self.dfa = self.DFA0 = self.DFA_0KWDEF
		self.DFATRAIL = self.DFA_TRAILKWDEF

	def endvargl (self):
		if self.current [0] == OP_CPAR: self.vaend ()
		else: self.lambend ()

	def sepkwok (self):
		self.flush (END_PRI)
		x = self.stack.pop ()
		self.stack [-1][1].append (x)
		if self.current [0] == OP_COMMA: self.dfa = self.DFA_FARG
		else: self.endvargl ()

	def vararg (self):
		self.dfa = self.DFA_NAME
		self.okdfa = self.DFA_VARKW2

	def varend (self):
		x = self.stack.pop ()
		self.stack [-1][0].append (x)
		self.stack [-1][2] = CO_VARARGS
		if self.current [0] == OP_COMMA: self.dfa = self.DFA_NEEDKWA
		else: self.endvargl ()

	def kwargok (self):
		self.dfa = self.DFA_NAME
		self.okdfa = self.DFA_DEFEND

	def defend (self):
		x = self.stack.pop ()
		self.stack [-1][0].append (x)
		self.stack [-1][2] |= CO_VARKEYWORDS
		self.endvargl ()

	def deco (self):
		self.stack.append ('@')
		self.deco2 ()

	def deco2 (self):
		self.dfa = self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAIL
		self.DFALINE = self.DFA_DECO

	def decodef (self):
		i = 1
		while self.stack [-i] != '@': i -= 1
		dl = ast.Decorators (self.stack [1-i:])
		del self.stack [-i:]
		self.fdef (dl)

	def exstmt (self):
		self.pending.append ((self.do_exec, (self.current [1], len (self.stack)), SSTMT_PRI))
		self.dfa = self.DFA_0NEEDEXPR
		self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILeEXP

	def execin (self):
		self.flushl (ASSIGN_PRI)
		self.mlcnt = 1
		self.dfa = self.DFA_0NEEDEXPR
		self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILmlEXP

	def do_printd (self, lno, stk):
		if self.stack [-1] == '\n':
			pr = ast.Print
			self.stack.pop ()
		else: pr = ast.Printnl
		self.stack [stk:] = [pr (self.stack [stk+1:], self.stack [stk], lno)]

	def do_print (self, lno, stk):
		if self.stack [-1] == '\n':
			pr = ast.Print
			self.stack.pop ()
		else: pr = ast.Printnl
		self.stack [stk:] = [pr (self.stack [stk:], None, lno)]

	def prn_stmt (self):
		self.dfa = self.DFA_PRNDEST

	def prdst (self):
		self.pending.append ((self.do_printd, (self.current [-1], len (self.stack)), SSTMT_PRI))
		self.mlcnt = 10000
		self.dfa = self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILmlEXP

	def prnodst (self):
		self.pending.append ((self.do_print, (self.current [-1], len (self.stack)), SSTMT_PRI))
		self.mlcnt = 10000
		self.dfa = self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILmlEXP
		return 1

	def prnuth (self):
		self.stack.append (ast.Printnl ([], None, self.current [1]))
		self.dfa = self.DFATRAIL
		return 1

		# --* subscript *--

	def osubsc (self):
		self.pending.append (len (self.stack) - 1)
		self.nest (self.DFA_0SUBSC, self.DFA_TRAILSUBSC)

	def csubsc (self):
		self.eos ()
		self.unnest ()
		self.dfa = self.DFATRAIL
		p = self.pending.pop ()
		if len (self.stack) - p == 2 and type (self.stack [-1]) is list:
			self.stack [-2:] = [ast.Slice (self.stack [-2], OP_APPLY, *self.stack [-1])]
		else:
			self.stack [p:] = [ast.Subscript (self.stack [p], OP_APPLY, self.stack [p+1:])]

	def do_sli (self, lno, stk, sobj):
		n = len (self.stack) - stk
		if n == 2 and not sobj: self.stack [stk:] = [self.stack [stk:]]
		elif n <= 3: self.stack [stk:] = [ast.Sliceobj (self.stack [stk:])]
		else: self.error ("too many slices")

	def sli (self):
		self.flushl (SLICE_PRI)
		if not (self.pending and self.pending [-1][2] == SLICE_PRI):
			self.pending.append ((self.do_sli, (self.current [1], len (self.stack)-1,
				 bool (self.pending)), SLICE_PRI))
		self.dfa = self.DFA0

	def bsli (self):
		self.stack.append (None)
		self.sli ()

	def zsli (self):
		if not (self.pending and self.pending [-1][2] == SLICE_PRI):
			self.error ("Missing subscript")
		self.stack.append (None)
		self.csubsc ()

	def opbqt (self):
		'A wasted operator?'
		if self.bqt:
			self.error ()
		self.bqt = 1
		self.nest (self.DFA0, self.DFATRAIL)
		self.pending.append ((self.do_bqt, (), BACKQUOTE_PRI))

	def clbqt (self):
		if not self.bqt:
			self.error ()
		self.bqt = 0
		self.eos ()
		self.unnest ()
		self.dfa = self.DFATRAIL

    # ----* these folks take care of nested assignments. Convert to self.error if you want *----

	def nest_asgn (self):
		self.pending.append ((self.do_ass, (self.current [1], len (self.stack)-1), ASSIGN_PRI))
		self.dfa = self.DFA0 = self.DFA_0	# redux?

	def nest_augass (self):
		self.pending.append ((self.do_aug, self.current, ASSIGN_PRI))
		self.dfa = self.DFA0 = self.DFA_0	# redux?

	def subsc_comma (self):
		self.flushl (SLICE_PRI)
		if self.pending and self.pending [-1][2] == SLICE_PRI:
			f, (a1, a2, a3), pri = self.pending [-1]
			self.pending [-1] = f, (a1, a2, True), pri
		self.bitop (COMMA_PRI, ast.Tuple)

    # with

	def with_stmt (self):
		self.dfa = self.DFA0 = self.DFA_0NEEDEXPR
		self.DFATRAIL = self.DFA_TRAILSEXP
		self.pending.append ((self.do_with, (self.current [1],), CSTMT_PRI))

    ########### DFA tables ###########

	DFA_PRNDEST = {
		OP_RSH: prdst,
		DEFAULT: prnodst,
		END_OF_STMT: prnuth,
		OP_STMT: prnuth,
		NAME_OF_DFA: 'print_dest'
	}

	DFA_DECO = {
		OP_AT: deco2,
		STMT_DEF: decodef,
		DEFAULT: error,
		NAME_OF_DFA: 'decorators'
	}

	DFA_DEFEND = {
		OP_CPAR: defend,
		OP_COLON: defend,
		DEFAULT: error,
		NAME_OF_DFA: 'end_funcdef'
	}

	DFA_NEEDKWA = {
		OP_POW: kwargok,
		DEFAULT: error,
		NAME_OF_DFA: 'want_kws'
	}

	DFA_VARKW2 = {
		OP_CPAR: varend,
		OP_COMMA: varend,
		OP_COLON: varend,
		DEFAULT: error,
		NAME_OF_DFA: 'after_var_arg'
	}

	DFA_ARGTUP = {
		SYM_BASE: vtp1,
		OP_CPAR: vtend,
		OP_OPAR: vvtup,
		DEFAULT: error,
		NAME_OF_DFA: 'nest_arg_tup'
	}

	DFA_ARGTUP2 = {
		OP_COMMA: vtp2,
		OP_CPAR: vtend,
		DEFAULT: error,
		NAME_OF_DFA: 'nest_arg_sep'
	}

	DFA_ARGSEP = {
		OP_COMMA: vsep,
		OP_CPAR: vaend,
		DEFAULT: error,
		OP_COLON: lambend,
		OP_ASSIGNMENT: kwdef,
		NAME_OF_DFA: 'arg_sep'
	}

	DFA_FARG = {
		SYM_BASE: parg,
		OP_CPAR: vaend,
		OP_OPAR: vatup,
		OP_MUL: vararg,
		OP_POW: kwargok,
		OP_COLON: lambend,
		DEFAULT: error,
		NAME_OF_DFA: 'func_arg'
	}

	DFA_FUNCP = {
		OP_OPAR: vargl,
		DEFAULT: error,
		NAME_OF_DFA: 'def_arglist'
	}

	DFA_CLBASE = {
		OP_COLON: suite0,
		OP_OPAR: cbase0,
		DEFAULT: error,
		NAME_OF_DFA: 'class_bases'
	}

	DFA_NAME = {
		SYM_BASE: okname,
		DEFAULT: error,
		NAME_OF_DFA: 'want_name'
	}

	DFA_EDICT = {
		OP_CBRK: edict,
		OP_CSQB: elist,
		DEFAULT: dflt,
		NAME_OF_DFA: 'dict_list-0'
	}

	DFA_FORIF = {
		OP_CPAR: dflt_tr,
		OP_CSQB: dflt_tr,
		STMT_FOR: for_stmt,
		DEFAULT: error,
		NAME_OF_DFA: 'for/if_expr'
	}

	DFA_FROM6 = {
		OP_COMMA: nextfromnam,
		DEFAULT: dflt_tr,
		NAME_OF_DFA: 'next_from_as'
	}

	DFA_FROM5 = {
		SYM_BASE: frmasnam,
		DEFAULT: error,
		NAME_OF_DFA: 'from_as_name'
	}

	DFA_FROM4 = {
		SYM_BASE: frmnmsep,
		OP_COMMA: nextfromnam,
		OP_CPAR: lambda x: None,
		DEFAULT: dflt_tr,
		NAME_OF_DFA: 'from_names'
	}

	DFA_FROM3 = {
		SYM_BASE: frmdotn,
		DEFAULT: error,
		NAME_OF_DFA: 'from_dotted_name'
	}

	DFA_FROM2 = {
		OP_MUL: allfrom,
		OP_OPAR: lambda x: None,
		SYM_BASE: frmnames,
		DEFAULT: error,
		NAME_OF_DFA: 'from_what'
	}

	DFA_FROM1 = {
		STMT_IMPORT: fromimp,
		OP_DOT: frmdot,
		DEFAULT: error,
		NAME_OF_DFA: 'from_name_trailer'
	}

	DFA_IMP4 = {
		OP_COMMA: impnext,
		DEFAULT: dflt_tr,
		NAME_OF_DFA: 'import_comma'
	}

	DFA_IMP3 = {
		SYM_BASE: impasnam,
		DEFAULT: error,
		NAME_OF_DFA: 'name_after_as'
	}

	DFA_IMP2 = {
		SYM_BASE: impnam2,
		DEFAULT: error,
		NAME_OF_DFA: 'name_after_dot'
	}

	DFA_IMP1 = {
		OP_DOT: dotnam,
		SYM_BASE: asname,
		OP_COMMA: impnext,
		DEFAULT: dflt_tr,
		NAME_OF_DFA: 'import_comma'
	}

	DFA_GLOBEX = {
		OP_DOT: gexdot,
		DEFAULT: error,
		NAME_OF_DFA: 'global_dot'
	}

	DFA_GLOB1 = {
		OP_COMMA: gnext,
		DEFAULT: dflt_tr,
		NAME_OF_DFA: 'global_comma'
	}

	DFA_GLOB0 = {
		SYM_BASE: gname,
		OP_DOT: gdot,
		DEFAULT: error,
		NAME_OF_DFA: 'global_name'
	}

	DFA_GLOBATTR = {
		SYM_BASE: gmemb,
		DEFAULT: error,
		NAME_OF_DFA: 'global_member'
	}

	DFA_GLOBNAM = {
		SYM_BASE: gexmemb,
		DEFAULT: error,
		NAME_OF_DFA: 'global_member_expr'
	}

	DFA_EXC1 = {
		OP_COLON: suite0,
		DEFAULT: exc00,
		NAME_OF_DFA:'except_expr'
	}

	DFA_FLUSHL = {
		DEFAULT: dflush,
		NAME_OF_DFA: 'flush_it'
	}

	DFA_SUITE2 = {
		STMT_ELSE: stelse,
		STMT_ELIF: stelif,
		STMT_FINALLY: stfin,
		STMT_EXCEPT: stexc,
		DEFAULT: dflt_tl,
		NAME_OF_DFA:'optional suites'
	}

	DFA_MAYSUITE = {
		END_OF_STMT: push_subsuite,
		DEFAULT: line_subsuite,
		NAME_OF_DFA: 'where_is_the_suite'
	}

	DFA_COLONSUITE = {
		OP_COLON: suite0,
		DEFAULT: error,
		NAME_OF_DFA:'colon_suite'
	}

	DFA_MAYEXPR = {
		OP_STMT: noexp,
		END_OF_STMT: noexp,
		DEFAULT: dflt,
		NAME_OF_DFA:'optional_expression'
	}

	DFA_ISNOARG = {
		OP_CPAR: noarg,
		DEFAULT: nonoarg,
		NAME_OF_DFA:'noarg'
	}

	DFA_ISETUP = {
		OP_CPAR: etup,
		DEFAULT: noetup,
		NAME_OF_DFA:'maybe_etup'
	}

	DFA_TESTGENFOR = {
		STMT_FOR: genfor,
		OP_COMMA: stop_genfor,
		OP_CPAR: stop_genfor,
		DEFAULT: not_genfor,
		NAME_OF_DFA:'test_genfor'
	}

	DFA_TESTGENFOR_CALL = dict (DFA_TESTGENFOR)
	DFA_TESTGENFOR_CALL [OP_ASSIGNMENT] = stop_genfor
	DFA_TESTGENFOR_CALL [NAME_OF_DFA] = 'test_genfor_in_call'

	DFA_KW = {
		OP_POW: dstar,
		DEFAULT: error,
		NAME_OF_DFA:'need_kw'
	}

	DFA_ISOP = {
		OP_NOT: lambda self: self.cmpop ('is not'),
		DEFAULT: not_isnot,
		NAME_OF_DFA:'is not?'
	}

	DFA_NOTIN = {
		OP_IN: lambda self: self.cmpop ('not in'),
		DEFAULT: error,
		NAME_OF_DFA:'not in'
	}

	DFA_MEMBER  = {
		SYM_BASE: member,
		DEFAULT: error,
		NAME_OF_DFA:'member'
	}

	def wrap_binop (priority, node, binop=binop):
		return lambda self: binop (self, priority, node)

	def wrap_bitop (priority, node, bitop=bitop):
		return lambda self: bitop (self, priority, node)

	DFA_TRAIL = {
		OP_DOT: dotop,
		OP_POW: power,
		OP_OSQB: osubsc,
		OP_OPAR: fcall,

		OP_ADD: wrap_binop (ADDSUB_PRI, ast.Add),
		OP_SUB: wrap_binop (ADDSUB_PRI, ast.Sub),
		OP_MUL: wrap_binop (MULDIV_PRI, ast.Mul),
		OP_DIV: wrap_binop (MULDIV_PRI, ast.Div),
		OP_MOD: wrap_binop (MULDIV_PRI, ast.Mod),
		OP_FDIV: wrap_binop (MULDIV_PRI, ast.FloorDiv),
		OP_RSH: wrap_binop (SHIFT_PRI, ast.RightShift),
		OP_LSH: wrap_binop (SHIFT_PRI, ast.LeftShift),

		OP_AND: wrap_bitop (BITAND_PRI, ast.Bitand),
		OP_XOR: wrap_bitop (BITXOR_PRI, ast.Bitxor),
		OP_OR: wrap_bitop (BITOR_PRI, ast.Bitor),
		OP_BAND: wrap_bitop (BOOLAND_PRI, ast.And),
		OP_BOR: wrap_bitop (BOOLOR_PRI, ast.Or),
		OP_COMMA: wrap_bitop (COMMA_PRI, ast.Tuple),

		OP_NOT: notin,
		OP_IS: isop,
		OP_ASSIGNMENT: nest_asgn,
		OP_CPAR: cpar,
		OP_CBRK: ccbr,
		OP_CSQB: csqb,
		OP_BQT: clbqt,
		END_OF_STMT: eos,
		DEFAULT: error,
		NAME_OF_DFA:'trailer'
	}
	del wrap_binop, wrap_bitop, binop

	for i in ('==', '!=', '<', '>', '<=', '>=', 'in'):
		DFA_TRAIL [symtable [i]] = lambda self, i=i: self.cmpop (i)
	for i in AUGASSIGN:
		DFA_TRAIL [i] = nest_augass

	DFA_0 = {
		OP_SUB: lambda self: self.unaryop (ast.UnarySub),
		OP_ADD: lambda self: self.unaryop (ast.UnaryAdd),
		OP_CPL: lambda self: self.unaryop (ast.Invert),
		OP_NOT: lambda self: self.unaryop (ast.Not, NOT_PRI),
		OP_LAMBDA: lambdef,
		OP_OPAR: opar,
		OP_CPAR: dflt_tr,
		OP_OBRK: ocbr,
		OP_OSQB: osqb,
		OP_CBRK: ccbr,
		OP_CSQB: csqb,
		OP_ASSIGNMENT: dflt_tr,
		SYM_BASE: symbol,
		VAL_BASE: constant,
		STR_BASE: constant,
		OP_BQT: opbqt,
		END_OF_STMT: eos,
		STMT_GLOBAL: gatom,
		DEFAULT: error,
		NAME_OF_DFA:'boot'
	}

		# the comma after a kwarg def goes to next arg
	DFA_TRAILKWDEF = dict (DFA_TRAIL)
	DFA_TRAILKWDEF [OP_COMMA] = sepkwok
	DFA_TRAILKWDEF [OP_CPAR] = sepkwok 
	DFA_TRAILKWDEF [OP_COLON] = sepkwok 
	DFA_TRAILKWDEF [NAME_OF_DFA] = 'kwargdef_trail'
	DFA_0KWDEF = dict (DFA_0)
	DFA_0KWDEF [OP_ASSIGNMENT] = DFA_0KWDEF [OP_CPAR] = DFA_0KWDEF [END_OF_STMT] = error
	DFA_0KWDEF [NAME_OF_DFA] = 'kwarg_boot'

		# the comma in a dictionary sure does not make a tuple
	DFA_TRAILDICT2 = dict (DFA_TRAIL)
	DFA_TRAILDICT2 [OP_COMMA] = sep2ok
	DFA_TRAILDICT2 [NAME_OF_DFA] = 'in_dict2'
	DFA_TRAILDICT1 = dict (DFA_TRAIL)
	DFA_TRAILDICT1 [OP_COMMA] = error
	DFA_TRAILDICT1 [OP_COLON] = sepok
	DFA_TRAILDICT1 [NAME_OF_DFA] = 'in_dict0'

		# neither does in a list
	DFA_TRAILLIST = dict (DFA_TRAIL)
	DFA_TRAILLIST [OP_COMMA] = lsepok
	DFA_TRAILLIST [NAME_OF_DFA] = 'in_list'

		# argument list
	DFA_0ARGL = dict (DFA_0)
	DFA_0ARGL [OP_CPAR] = do_call
	DFA_0ARGL [OP_MUL] = star
	DFA_0ARGL [OP_POW] = dstar
	DFA_0ARGL [NAME_OF_DFA] = 'arglist_boot'
	DFA_TRAILARGL = dict (DFA_TRAIL)
	DFA_TRAILARGL [OP_COMMA] = acomma
	DFA_TRAILARGL [OP_CPAR] = cparf
	DFA_TRAILARGL [OP_ASSIGNMENT] = akw
	DFA_TRAILARGL [NAME_OF_DFA] = 'arglist_trailer'
	DFA_0ARGLkw = dict (DFA_0)
	DFA_0ARGLkw [OP_CPAR] = error
	DFA_0ARGLkw [NAME_OF_DFA] = 'arglist_kw_boot'
	DFA_TRAILARGLkw = dict (DFA_TRAIL)
	DFA_TRAILARGLkw [OP_COMMA] = error
	DFA_TRAILARGLkw [OP_CPAR] = cparfkw
	DFA_TRAILARGLkw [NAME_OF_DFA] = 'arglist_kw_trailer'
	DFA_0ARGLva = dict (DFA_0)
	DFA_0ARGLva [OP_CPAR] = error
	DFA_0ARGLva [OP_POW] = dstar
	DFA_0ARGLva [NAME_OF_DFA] = 'arglist_va_boot'
	DFA_TRAILARGLva = dict (DFA_TRAIL)
	DFA_TRAILARGLva [OP_COMMA] = vacomma
	DFA_TRAILARGLva [OP_CPAR] = cparfva
	DFA_TRAILARGLva [NAME_OF_DFA] = 'arglist_va_trailer'

		# subscript expression and slices
	DFA_0SUBSC = dict (DFA_0)
	DFA_0SUBSC [OP_COLON] = bsli
	DFA_0SUBSC [OP_COMMA] = subsc_comma
	DFA_0SUBSC [OP_CSQB] = zsli
	DFA_0SUBSC [NAME_OF_DFA] = 'subscript_boot'
	DFA_TRAILSUBSC = dict (DFA_TRAIL)
	DFA_TRAILSUBSC [OP_CSQB] = csubsc
	DFA_TRAILSUBSC [OP_COLON] = sli
	DFA_TRAILSUBSC [OP_COMMA] = subsc_comma
	DFA_TRAILSUBSC [NAME_OF_DFA] = 'subscript_trailer'
	# don't allow '=' in subscript
	for i in AUGASSIGN:
		del DFA_TRAILSUBSC [i]
	del DFA_TRAILSUBSC [OP_ASSIGNMENT]

		# expression that may end in ';'
	DFA_TRAILEXP = dict (DFA_TRAIL)
	DFA_TRAILEXP [OP_STMT] = tlhandle
	DFA_TRAILEXP [END_OF_STMT] = tlhandle
	DFA_TRAILEXP [NAME_OF_DFA] = 'trail_expr'

		# assignments
	DFA_TRAILASS = mergedict (DFA_TRAILEXP, {
		OP_ASSIGNMENT: assign,
		NAME_OF_DFA: 'assignment_trailer'
	})
	DFA_TRAILASG = dict (DFA_TRAILASS)
	for i in AUGASSIGN:
		DFA_TRAILASS [i] = augass

		# expression is a must
	DFA_0NEEDEXPR = dict (DFA_0)
	DFA_0NEEDEXPR [END_OF_STMT] = error
	DFA_0NEEDEXPR [NAME_OF_DFA] = 'need_expr'

		# expression that must end in ':'
	DFA_TRAILSEXP = dict (DFA_TRAIL)
	DFA_TRAILSEXP [OP_STMT] = error
	DFA_TRAILSEXP [END_OF_STMT] = error
	DFA_TRAILSEXP [OP_COLON] = suite0
	DFA_TRAILSEXP [NAME_OF_DFA] = 'while/if/elif/etc_expr'

		# expression that may end in 'for' or 'if'
	DFA_TRAILFORIF = dict (DFA_TRAIL)
	DFA_TRAILFORIF [STMT_FOR] = morefor
	DFA_TRAILFORIF [STMT_IF] = moreif
	DFA_TRAILFORIF [OP_CSQB] = endlch
	DFA_TRAILFORIF [OP_STMT] = error
	def dflt_ft (self):
		self.dfa = self.DFATRAIL = self.forfail
		return 1
	DFA_TRAILFORIF [OP_CPAR] = dflt_ft
	DFA_TRAILFORIF [END_OF_STMT] = error
	DFA_TRAILFORIF [OP_COLON] = error
	DFA_TRAILFORIF [NAME_OF_DFA] = 'more_genexpr_trail'

		# expression that must end in ':' or ','
	DFA_TRAILx0EXP = dict (DFA_TRAILSEXP)
	DFA_TRAILx0EXP [OP_COLON] = exc01
	DFA_TRAILx0EXP [OP_COMMA] = exc11
	DFA_TRAILx0EXP [NAME_OF_DFA] = 'except_first'
	DFA_TRAILx1EXP = dict (DFA_TRAILx0EXP)
	DFA_TRAILx1EXP [OP_COMMA] = error
	DFA_TRAILx1EXP [NAME_OF_DFA] = 'except_second'

		# list of expressions for 'raise', 'assert'
	DFA_TRAILmlEXP = dict (DFA_TRAILEXP)
	DFA_TRAILmlEXP [OP_COLON] = error
	DFA_TRAILmlEXP [OP_COMMA] = mlcoma
	DFA_TRAILmlEXP [NAME_OF_DFA] = 'multiple_tests'

	DFA_TRAILmlpEXP = dict (DFA_TRAILmlEXP)
	DFA_TRAILmlEXP [OP_CPAR] = nbase
	DFA_TRAILmlEXP [NAME_OF_DFA] = 'bases_tests'

		# expression must end in 'in'
	DFA_TRAILFEXP = mergedict (DFA_TRAIL, {
		OP_IN: infor,
		OP_STMT: error,
		END_OF_STMT: error,
		NAME_OF_DFA: 'for_expr'
	})

		# may end in 'in'
	DFA_TRAILeEXP = dict (DFA_TRAIL)
	DFA_TRAILeEXP [OP_IN] = execin
	DFA_TRAILeEXP [OP_STMT] = tlhandle
	DFA_TRAILeEXP [END_OF_STMT] = tlhandle
	DFA_TRAILeEXP [NAME_OF_DFA] = 'exec_trail'

	DFA_TRAIL_SMALL = {
		OP_STMT: add_small,
		END_OF_STMT: add_small,
		DEFAULT: error,
		NAME_OF_DFA: 'small_stmt'
	}

	DFA_YLD = {
		OP_MUL: yld_stmta,
		DEFAULT: yld_stmtc,
		NAME_OF_DFA: 'what_yield?'
	}

	DFA_0_SMALL = {
		OP_STMT:error,
		STMT_BREAK: lambda self: self.sstmt (ast.Break),
		STMT_CONTINUE: lambda self: self.sstmt (ast.Continue),
		STMT_PASS: lambda self: self.sstmt (ast.Pass),
		STMT_YIELD: yld_stmt,
		STMT_RETURN: rtn_stmt,
		STMT_DEL: del_stmt,
		STMT_GLOBAL: glb_stmt,
		STMT_IMPORT: imp_stmt,
		STMT_FROM: frm_stmt,
		STMT_ASSERT: asrt_stmt,
		STMT_RAISE: raise_stmt,
		STMT_EXEC: exstmt,
		STMT_PRINT: prn_stmt,
		END_OF_STMT: lambda x: None,
		DEFAULT: rdexp,
		NAME_OF_DFA:'0_tl'
	}

	DFA_TOPLEV = {
		STMT_WHILE: whl_stmt,
		STMT_IF: if_stmt,
		STMT_FOR: for_stmt,
		STMT_TRY: try_stmt,
		STMT_CLASS: class_stmt,
		STMT_DEF: fdef,
		STMT_WITH: with_stmt,
		OP_AT: deco,
		DEFAULT: rdsml,
		NAME_OF_DFA:'toplev'
	}

	###### main loop ######

	def parse (self, stgen):
		self.generators.append (stgen)
		self.nest ()
		sp = len (self.stack)
		self.DFALINE = self.DFA_TOPLEV
		for stmt in stgen:
			stmt.append ((END_OF_STMT, 0))
			self.dfa = self.DFALINE
			for i in stmt:
				self.current = i
				while 1:
					#print self.dfa [NAME_OF_DFA], strtok (i), i[-1], 40*' '
					##print self.dfa [NAME_OF_DFA], i, 40*' '
					if i [0] in self.dfa:
						if self.dfa [i [0]] (self):
							continue
					else:
						if self.dfa [DEFAULT] (self):
							continue
					break
		self.eos (ENDALL_PRI)
		self.stack [sp:] = [ast.Stmt (self.stack [sp:])]
		self.unnest ()
		self.generators.pop ()

	###### main loop for eval #####

	def parse_expr (self, expr):
		self.ingen = self.tnest = self.forfail = None
		self.DFALINE = self.dfa = self.DFA0 = self.DFA_0
		self.DFATRAIL = self.DFA_TRAILASS
		for i in expr:
			self.current = i
			op = i [0]
			while 1:
				##print self.dfa [NAME_OF_DFA], strtok (i), i[-1], 40*' '
				if op in self.dfa:
					if self.dfa [op] (self):
						continue
				else:
					if self.dfa [DEFAULT] (self):
						continue
				break
			# in the reduced parser won't be needed cos ';' will
			# be unacceptable chararcter...
			if op == OP_STMT:
				expr = expr [expr.index (i)+1:]
				break
		else:
			expr = ()
		self.eos (ENDALL_PRI)
		return self.stack.pop (), expr

def strtok (tk):
	if tk[0] >= SYM_BASE:
		if tk [0] == STR_BASE:
			if len (tk [1]) > 20:
				return '"' + tk[1][:3] + '...' + tk [1][-3:] + '"'
			return '"' + tk[1] + '"'
		return tk [1]
	if not exptable:
		mkexptable ()
	return "'%s'" % exptable [tk [0]]

# ///// entry

def parse (filename=None, source=None):
	return DFA_parser (filename, source).outcome

def parse_expr (source):
	return DFA_parser (None, source, isexpr=True).outcome

############################ main ############################

if __name__ == '__main__':
	print parse_expr ('(1+2*4, "xa"+"xo", (1, 1.023));')
	print repr (parse (filename='ptest.py', source=None))
	print "Yes?"
