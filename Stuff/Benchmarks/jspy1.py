#
# initial version of the jspy vm
# Stelios Xanthakis
#
import gc

#DEJAVU
'''
{
'NAME':"Javascript VM",
'DESC':"Javascript VM running fib/tak in js",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"SEM",
'BARGS':""
}
'''

#
# TODO:
#  escape python reserved words
#  exponential floats
#  regexes
#  escape string literal
#  what's the precedence?
#  js string + other
#  'preparse' method, should detect function definitions in if's for's and move
#	outside

class jsSyntaxError:
    pass

try:
    import pyc
    def compile (s, f, t):
	return pyc.compile (s, f, t, dynlocals=False, RRot3=True, showmarks=0)
except:
    pass

#
# Tokenizer.
#
# given a line return a list of tokens
# given an iterable, tokenize each line and
# return a list of lists of tokens.
#
# does comment removal.
#
import re

IDENTIFIER = r"[a-zA-Z_]\w*"
FLOAT = r"\d+\.\d+|\.\d+|\d+\."
NUM = r"\d+"
HEX = r""
THREEOP = r"===|!===|>>>"
TWOOP = r"==|!=|&&|\|\||%=|\^=|&=|\*=|-=|\+=|<=|>=|/=|\+\+|--|//|/\*"
UNOP = r"""[+\-!%\^*()[\]=|{};<>.,/"'?:]"""

match_token = re.compile (r"\s*("+'|'.join ([IDENTIFIER, FLOAT, NUM, THREEOP, TWOOP, UNOP])+")").match
is_identifier = re.compile (IDENTIFIER).match
is_number = re.compile ('|'.join ([FLOAT, NUM])).match
del IDENTIFIER, FLOAT, NUM, HEX, THREEOP, TWOOP, UNOP

def skip_string (s, i):
    q = s [i]
    j = i + 1
    while 1:
	j = s.find (q, j)
	if j == -1:
	    raise jsSyntaxError
	if s[j-1] == '\\':
	    k = j - 2
	    while s [k] == '\\':
		k -= 1
	    if (j-1-k)%2:
		j += 1
		continue
	return j + 1, s [i:j+1]

UNACCEPTABLE_DIV = ';([{=}'	# '/' after these signals a regexp

def tokenize (line):
    global IN_COMMENT, LAST_TOK

    i = 0
    T = []

    if IN_COMMENT:
	if '*/' in line:
	    i = line.find ('*/') + 2
	    IN_COMMENT = False
	else:
	    return T

    while 1:
        M = match_token (line, i)
	if not M:
	    break
	t = M.group (1)
	if t [0] == '/':
	    if t == '//':
		break
	    if t == '/*':
	        if '*/' in line [M.start (1):]:
		    i = line.find ('*/', M.start (1)) + 2
		    continue
	        IN_COMMENT = True
		break
	    if (T and T [-1] or LAST_TOK) [-1] in UNACCEPTABLE_DIV:
		i,w = skip_string (line, M.start (1))
		T.append (w)
		continue
	elif t in """"'""":
	    i,w = skip_string (line, M.start (1))
	    # escape it
	    T.append (w)
	    continue
	i = M.end ()
	T.append (M.group (1))

    if T:
	LAST_TOK = T [-1]
    return T

def tokenize_all (itr):
    global IN_COMMENT, LAST_TOK
    IN_COMMENT = False
    LAST_TOK = ';'

    S = []
    for x in itr:
	y = tokenize (x)
	if y:
	    S.append (y)
    return S

#
# Prepare 1
#
# Modifies 'source' which is a list of lists so that:
#  each element of [source] is one statement
#  this implies "AUTOMATIC SEMICOLON INSERTION" 
#  eventually semicolons are found only at the end of each sublist
#  ...and removed afterwards
#  Also checks that {([ are properly paired with ])}
#  and makes { } line separators in their own list
#  unless they are about "ObjectLiteral".
#
# In other words, this function will break and join lines forming
# statements.
#
def dlen (x, j=0):
    for i in xrange (j, 1000000):
	if i >= len (x):
	    return
	yield i

AUTOJOIN = set(['+', '-', '*', '/', '&', '^', '|', '<<', '>>', '>>>', '<<<', '==', '!=', '=', '!', ',',
		'+=', '-=', '*=', '&=', '^=', '%=', '\=', '<=', '>=', '>>=', '<<=', '===', '!===', '.',
		'var', 'function', 'if', 'while', '?', ':'])
AUTOJOIN2 = set(['*', '/', '&', '^', '|', '<<', '>>', '>>>', '<<<', '==', '!=', '=', ',', '.', ':', '?',
		'+=', '-=', '*=', '&=', '^=', '%=', '\=', '<=', '>=', '>>=', '<<=', '===', '!==='])

def prepare (source):
    nest = []
    curl = 0
    for i in dlen (source):
	l = source [i]
	j = 0
	while 1:
	    for j in dlen (l, j):
		t = l [j]
		if t in "([":
		    nest.append (t)
		elif t in ")]":
		    if not nest or nest.pop()+t not in "[]()":
			raise jsSyntaxError
		elif t in "{}":
		    if not j:
			if t == '{': curl += 1
			elif not curl: raise jsSyntaxError
			else: curl -= 1
			if len (l) > 1:
			    source.insert (i+1, l [1:])
			    del l [1:]
		    else:
			if j < len (l) - 1:
			    source.insert (i+1, l [j+1:])
			source.insert (i+1, [t])
			del l [j:]
		elif t == ';' and not nest and len (l)-j != 1:
		    source.insert (i+1, l [j+1:])
		    del l [j+1:]
	    # AUTOMATIC SEMICOLON INSERTION
	    # actually, "automatic line join" but the same effect eventually...
	    if nest or l [-1] in AUTOJOIN or (i < len (source) - 1 and source [i+1][0] in AUTOJOIN2):
	        l.extend (source [i+1])
		del source [i+1]
		j += 1
		continue
	    break

	source [i] = tuple (source [i])

    # join ObjectLiteral
    for i in dlen (source):
	if source [i] == ('{',):
	    j = source [i+1]
	    if j == ('}',) or len (j) > 1 and j [1] == ':':
		source [i:i+3] = [tuple (source [i] + source [i+1] + source [i+2])]

    if curl:
	raise jsSyntaxError

    return source

#
# Misc Utils
#

NESTINGS = { '(':'()', '[':'[]', '{':'{}' }

def skip_nesting (lst, j):
    nst = NESTINGS [lst [j]]
    j += 1
    n = 1
    while n:
	if lst [j] in nst:
	    if lst [j] == nst [0]:
		n += 1
	    else:
		n -= 1
	j += 1
    return j

def expect (c, v):
    if c != v:
	raise jsSyntaxError

class peeking_generator:
    def __init__ (self, itr, nopeek = 0):
	self.iter = self.generator (itr)
	self.next = self.iter.next
	self.p = self
	self.nopeek = nopeek
    def generator (self, itr):
	for i in itr:
	    yield i
	    while self.p is not self:
		i, self.p = self.p, self
		yield i
    def __iter__ (self):
	return self.iter
    def peek (self):
	try:
	    self.p = self.iter.next ()
	    return self.p
	except:
	    return self.nopeek

#
# Pseudo-AST synthesizer for statements
#
# We are using AST-like nodes to high level statements only.
# expressions will be converted directly to python code.
#
# each node has a method 'compile' which recusrively compiles and
#  prepares the nodes for execution.  compile happens with Global
#  namespace known.
#
# exec: each statement/expression has a method 'eval_in' to execute in a local
#  namespace
#

class Node:
    pass

def ename ():
    for i in xrange (1000000):
	yield 'js_Expr%i' %i
ename = ename ()

CODE_TEMPLATE = r"""
def d(GLOBAL, ADD):
 def %s(LOCAL):
%s
 return %s
"""

class Expr (Node):
    reprstr = 'Expr (%s)'

    def __init__ (self, tokens):
	self.tokens = tokens

    def compile (self, ns, vars):
	name = ename.next ()
	x = js2py_compiler (self.tokens, vars)
	FUNC = CODE_TEMPLATE % (name, x.output, name)
	self.CODE_TEMPLATE = FUNC
	D = {}
	exec compile (FUNC, '', 'exec') in D, D
	self.F = D ['d'](ns, jsADD)

    def eval_in (self, ns):
	return self.F (ns)

    def __repr__ (self):
	return self.reprstr % ' '.join (self.tokens)

class Stmt (Node):
    def __init__ (self, stmts):
	self.stmts = stmts

    def preparse (self, vars, funcs):
	preparse (self.stmts, vars, funcs)

    def compile (self, ns, vars):
	for i in self.stmts:
	    i.compile (ns, vars)

    def eval_in (self, ns):
	for i in self.stmts:
	    i.eval_in (ns)

class VarDef (Expr):
    reprstr = 'VarDef (%s)'

class Function (Node):
    def __init__ (self, i, source):
	if i [1] == '(':
	    j = 1
	    self.name = 0
	else:
	    self.name = i [1]	## check
	    j = 2
	if len (i) == j:
	    i = source.next ()
	    j = 0
	expect (i [j], '(')
	if skip_nesting (i, j) != len (i):
	    raise jsSyntaxError
	self.argdef = i [j:]
	i = source.next ()
	expect (i [0], '{')
	self.body = compound_statement (source)

    def compile (self, ns):
	self.vars, self.funcs = set (), []
	self.body.preparse (self.vars, self.funcs)
	if self.argdef [1:-1]:
	    self.argnames = ''.join (self.argdef [1:-1]).split (',')
	else:
	    self.argnames = ()
	for i in self.argnames:
	    self.vars.add (i)
	self.body.compile (ns, self.vars)
	self.undefs = self.vars - set (self.argnames)

    def __call__ (self, *args):
	if len (args) != len (self.argnames):
	    raise jsSyntaxError
	# load locals 
	LOCAL = {}
	for i in self.undefs:
	    LOCAL [i] = JsUndefined
	for i, j in zip (self.argnames, args):
	    LOCAL [i] = j
	# do eval
	try:
	    self.body.eval_in (LOCAL)
	except Return.ReturnException, R:
	    return R.val

    def __repr__ (self):
	return "Function %s %s %s" % (self.name, ' '.join (self.argdef), self.body)

class If (Node):
    def __init__ (self, i, source):
	expect (i [1], '(')
	k = skip_nesting (i, 1)
	self.cond = Expr (i [1:k])
	if k == len (i):
	    i = source.next ()
	    k = 0
	self.body = statement (i [k:], source)
	if source.peek () [0] == 'else':
	    i = source.next ()
	    if len (i) == 1:
		i = source.next ()
	        self._else = statement (i, source)
	    else:
	        self._else = statement (i [1:], source)
	else:
	    self._else = None

    def compile (self, ns, vars):
	self.cond.compile (ns, vars)
	self.body.compile (ns, vars)
	if self._else:
	    self._else.compile (ns, vars)

    def eval_in (self, ns):
	if self.cond.eval_in (ns):
	    self.body.eval_in (ns)
	elif self._else:
	    self._else.eval_in (ns)

    def __repr__ (self):
	return "IF"
#	s = "If %s %s" % (' '.join (self.cond), self.body)
#	if not self._else:
#	    return s
#	return s + " Else %s" % repr (self._else)

class Return (Node):

    class ReturnException:
	def __init__ (self, val):
	    self.val = val

    def __init__ (self, i, source):
	self.expr = Expr (i [1:] or source.next ())

    def compile (self, ns, vars):
	self.expr.compile (ns, vars)

    def eval_in (self, ns):
	raise self.ReturnException (self.expr.eval_in (ns))

def compound_statement (source):
    S = []
    nc = 1
    for i in source:
	if i == ('}',):
	    nc -= 1
	    if not nc:
		return Stmt (S)
	S.append (synthline (i, source))
	if i == ('{',):
	    nc += 1

def statement (line, source):
    if line [0] == '{':
	return compound_statement (source)
    return synthline (line, source)

def synthline (i, source):
    if i [0] == 'var':
	return VarDef (i [1:])
    elif i [0] == 'function':
	return Function (i, source)
    elif i [0] == 'if':
	return If (i, source)
    elif i [0] == 'return':
	return Return (i, source)
    else:
	return Expr (i)

def synth (source):
    return [synthline (i, source) for i in source]


#
# pre-parse
#
# Given the body of a function/Main, turn 'var' into expressions,
# gather names of local variables, gather functions outside the
# code

def preparse (body, vars, funcs):
    rmv = []
    for i in dlen (body):
	s = body [i]
	if isinstance (s, VarDef):
	    delim = [0]
	    i = 1
	    while i < len (s.tokens):
		if s.tokens [i] == ',':
		     i += 1
		     delim.append (i)
		elif s.tokens [i] in NESTINGS:
		     i = skip_nesting (s.tokens, i)
		     continue
		i += 1
	    # remove decls without initialization
	    for i in delim:
		vars.add (s.tokens [i])
	elif isinstance (s, Expr):
	    pass
	elif isinstance (s, Function):
	    funcs.append (s)
	    rmv.append (i)
#	else:
#	    print "UNKNOWN:", s
    for i in reversed (rmv):
	del body [i]

#
# compile/translate javascript expressions to python functions
#
# We take a list of tokens and generate a python function which
# when called will return the value that the js-expression would
# produce.
#
# Our functions should take GLOBAL/LOCAL parameters
#

expr_term = re.compile (r"\s*(R\d+)\s*=\s*((?:LOCAL|GLOBAL)\s*\[[^\]]*\])").match
expr_attr = re.compile (r"\s*(R\d+)\s*=GETATTR\(([^)]*)\)").match
expr_subs = re.compile (r"\s*(R\d+)\s*=\s*(R\d+\[[^\]]*])").match

def NA(msg):
    print "NOT IMPLEMENTED:", msg
    raise jsSyntaxError

INDENT = 4*' '

def is_literal (x):
    return is_number (x) or x [0] in """"'"""

def indent (l):
    for i, x in enumerate (l):
	l [i] = INDENT + x

def register ():
    for i in xrange (10000):
	yield 'R%i'%i

BINARY = {}
for i, o in enumerate ((
	'*%/',
	'+-',
	('<<', '>>', '>>>'),
	('<', '>', '<=', '>=', 'instanceof'),
	('==', '!=', '===', '!=='),
	'&',
	'^',
	'|',
	('&&',),
	('||',))):
    for j in o:
	BINARY [j] = i

def assigned (output, op, R, Rl):
    aug = ''
    if op != '=':
	aug = op [0]
    ll = output [-1]
    M = expr_term (ll) or expr_subs (ll)
    if M:
	if not aug:
	    output [-1] = ''.join ([Rl, '=', M.group (2), '=', R])
	elif aug != '+':
	    output.append (''.join ([Rl, '=', M.group (2), '=', M.group (1), aug, R]))
	else:
	    output.append (''.join ([Rl, '=', M.group (2), '= ADD (', M.group (1), ',', R, ')']))
        return output, Rl
    M = expr_attr (ll)
    if M:
	output [-1] = ''.join ([Rl, '=', 'SETATTR(', M.group (1), ',', R, ')'])
        return output, Rl
    print ll, M#, M.group (1)
    NA ("assignmentor")

class js2py_compiler:
    PREFIX = set (['delete', 'void', 'typeof', '++', '--', '+', '-', '~', '!'])
    POSTFIX = '.[('
    ASSIGN = set (['=', '*=', '/=', '%=', '+=', '-=', '<<=', '>>=', '>>>=', '&=', '^=', '|'])
    def __init__ (self, expr, vars):
	self.vars = vars
	self.register = register ().next
	self.output = ['#' + ' '.join (expr)]
	expr, R = self.Expression (expr)
	self.emit ('return ', R)
	self.output = INDENT + ('\n' + INDENT).join (self.output)
    def emit (self, *args):
	self.output.append (''.join (args))	# OPT
    def emitR (self, *args):
	R = self.register ()
	self.output.append (R + ''.join (args))
	return R
    def logicalExpression (self, expr):
	expr, var = self.UnaryExpression (expr)
	if not expr or expr [0] not in BINARY:
	    return expr, var
	emit = self.emitR
	vars = [var]
	binaries = []
	while expr and expr [0] in BINARY:
	    pri = BINARY [expr [0]]
	    while binaries and pri >= binaries [-1][0]:
		op = binaries.pop ()[1]
		if op == '+':
		    R = emit ('=', 'ADD(', vars [-2], ',', vars [-1], ')')
		else:
		    R = emit ('=', vars [-2], op, vars [-1])
		vars.pop ()
		vars [-1] = R
	    binaries.append ((pri, expr [0]))
	    expr, var = self.UnaryExpression (expr [1:])
	    vars.append (var)
	R = vars.pop ()
	while binaries:
	    op = binaries.pop ()[1]
	    if op == '+':
		R = emit ('= ADD (', vars.pop (), ',', R, ')')
	    else:
		R = emit ('=', vars.pop (), op, R)
	return expr, R
    def ConditionalExpression (self, expr):
	expr, R = self.logicalExpression (expr)
	if not (expr and expr [0 ] == '?'):
	    return expr, R
	out1, self.output = self.output, []
	expr, R1 = self.Expression (expr [1:])
	expect (expr [0], ':')
	out2, self.output = self.output, []
	expr, R2 = self.Expression (expr [1:])
	self.output, out1 = out1, self.output
	indent (out1)
	indent (out2)
	r = self.register ()
	self.emit ('if ', R, ':')
	self.output.extend (out2)
	self.emit (INDENT + r, '=', R1)
	self.emit ('else:')
	self.output.extend (out1)
	self.emit (INDENT + r, '=', R2)
	return expr, r
    def AssignmentExpression (self, expr):
	orig, self.output = self.output, []
	expr, R = self.ConditionalExpression (expr)
	if not expr or expr [0] not in self.ASSIGN:
	    self.output = orig + self.output
	    return expr, R
	s = []
	while expr and expr [0] in self.ASSIGN:
	    s.append ((self.output, expr [0]))
	    self.output = []
	    expr, R = self.ConditionalExpression (expr [1:])
	self.output = orig + self.output
	while s:
	    out, op = s.pop ()
	    out, R = assigned (out, op, R, self.register ())
	    self.output.extend (out)
	return expr, R
    def Expression (self, expr):
	expr, R = self.AssignmentExpression (expr)
	while expr and expr [0] == ',':
	    expr, R = self.AssignmentExpression (expr [1:])
	return expr, R
    def UnaryExpression (self, expr):
	emit = self.emitR
	i = 0
	unaries = []
	while expr [i] in self.PREFIX:
	    unaries.append (expr [i])
	    i += 1

	if expr [i] in ('new', 'function', '[', '{'):
	    NA ("new/function in UnaryExpr")

	t = expr [i]
	if is_literal (t):
	    R = t
	elif is_identifier (t):
	    if t not in self.vars: x = 'GLOBAL'
	    else: x = 'LOCAL'
	    R = emit ('=', x, '["', t, '"]')
	elif t == '(':
	    expr, R = self.Expression (expr [i+1:])
	    i = 0
	    expect (expr [0], ')')
	else:
	    raise jsSyntaxError
	i += 1

	while i < len (expr) and expr [i] in self.POSTFIX:
	    t = expr [i]
	    i += 1
	    if t == '.':
		R = emit ('=GETATTR(', repr (expr [i]), ',', R, ')')	# verify identifier
		i += 1
	    elif t == '[':
		expr, R1 = self.Expression (expr [i:])
		expect (expr [0], ']')
		i = 1
		R = emit ('=', R, '[', R1, ']')
	    elif t == '(':
		args = []
		if expr [i] != ')':
		    while 1:
			expr, R1 = self.AssignmentExpression (expr [i:])
			args.append (R1)
			if expr [0] == ')':
			    break
			if expr [0] != ',':
			    raise jsSyntaxError
			i = 1
		    i = 0
		i += 1
		R = emit ('=', R, '(', ','.join (args), ')')
	    else:
		NA ("This postfix")

	for t in reversed (unaries):
	    if t in '+-~':
		R = emit ('=', t, R)
	    elif t == '!':
		R = emit ('=', 'not ', R)
	    elif t in '++--':
		# oh really?
		out, R = assigned (self.output, t == '++' and '+=' or '-=', '1', self.register ())
#		R = emit ('=', t [0], R)
	    else:
		NA ("prefix operator "+t)

	return expr [i:], R

def jsADD (x, y):
    try:
	return x + y
    except:
	if type (x) is str:
	    return x + str (y)
	if type (y) is str:
	    return str (x) + y
	raise

#
# Jscript objects
#
# That's needed as GLOBAL/LOCAL namespace for functions
#

class JsObject:
    def __init__ (self, D = None):
	self.D = D or {}
    def __getitem__ (self, x):
	try:
	    return self.D [x]
	except:
	    return JsUndefined
    def __setitem__ (self, x, y):
	self.D [x] = y

class JsUndefined (JsObject):
    def __init__ (self):
	self.D = {}
    def __repr__ (self):
	return "<Undefined>"

JsUndefined = JsUndefined ()

#
#
#

class Main:
    def __init__ (self, body, GLOBAL):
	self.GLOBAL = GLOBAL
	self.body = body
	vars, self.funcs = set (), []
	preparse (body, vars, self.funcs)
#	print "FUNCS:", self.funcs
#	print "BODY:", self.body
	for i in body:
	    i.compile (GLOBAL, ())
	for i in self.funcs:
	    i.compile (GLOBAL)
	    GLOBAL [i.name] = i

    def eval (self):
	for i in self.body:
	    i.eval_in (self.GLOBAL)

#############################################################################################

import sys

if 0:
    x = tokenize_all (open (sys.argv [1]))
    for i in x:
        print i
    x = prepare (x)
    print '----------'
    for i in x:
        print i
    x = synth (peeking_generator (x))
    for i in x:
        print i
    prog = Main (x, JsObject())
    raise SystemExit

JSPROG = r"""
function fib(i) {
    if (i < 2) return 1
    else return ( fib(i-2) + fib(i-1) )
}

writeln ("fib 20:" + fib (20))
writeln ("fib 20:" + fib (20))
writeln ("fib 20:" + fib (20))
writeln ("fib 20:" + fib (20))

function tak(x, y, z) {
    if (!(y < x)) return(z);
    else {
      return (
        tak (
          tak (x-1, y, z),
          tak (y-1, z, x),
          tak (z-1, x, y) ));
    }
}

writeln ("tak(18,12,6):" + tak (18,12,6))
writeln ("tak(18,12,6):" + tak (18,12,6))
writeln ("tak(18,12,6):" + tak (18,12,6))
"""

JSPROGSEM = r"""
function fib(i) {
    if (i < 2) return 1
    else return ( fib(i-2) + fib(i-1) )
}
function tak(x, y, z) {
    if (!(y < x)) return(z);
    else {
      return (
        tak (
          tak (x-1, y, z),
          tak (y-1, z, x),
          tak (z-1, x, y) ));
    }
}
writeln ("fib 20:" + fib (20))
writeln ("tak(14,12,6):" + tak (14,12,6))
"""

if 'SEM' in sys.argv:
    JSPROG = JSPROGSEM
    
PAST = synth (peeking_generator (prepare (tokenize_all (JSPROG.split ('\n')))))

Global = JsObject ()

def writeln (x):
    print x

Global ['writeln'] = writeln

gc.collect ()
prog = Main (PAST, Global)
from time import time
prog.eval ()
#print Global.D
