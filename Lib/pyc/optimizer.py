#
# Optimizations on the AST
#

from visitor	import walk
from misc	import opt_progress, counter
from gco	import GCO

import ast

try:
	set
except:
	from sets import Set as set
	from misc import reversed

set_is_constant = True

def is_compare (node):
	return isinstance (node, ast.Compare)

#
# compare statements. This can be used to turn ifs to conditionals
#
#	if c: x = 1
#	else: x = 2
# to:	x = c ? 1 : 2
#
#	if c: f (1)
#	else: f (2)
# to:	f (c ? 1 : 2)
#
#	if c: yield 1
#	else: yield 2
# to:	yield c ? 1 : 2
#
# This is a size optimization
#

def stmts_eq_base (stmt1, stmt2):
	# if both statements have only one expression which can be optimized
	stmt1, stmt2 = stmt1.nodes, stmt2.nodes
	if len (stmt1) != 1 or len (stmt2) != 1:
		return False
	return expr_eq_base (stmt1 [0], stmt2 [0])

def expr_eq_base (stmt1, stmt2):
	if stmt1.__class__ is not stmt2.__class__:
		return False
	if isinstance (stmt1, ast.Assign):
		if repr (stmt1.nodes) == repr (stmt2.nodes):
			return True
		return False
	if isinstance (stmt1, ast.Yield):
		return True
	if isinstance (stmt1, ast.Discard):
		stmt1, stmt2 = stmt1.expr, stmt2.expr
		if stmt1.__class__ is not stmt2.__class__:
			return False
	if isinstance (stmt1, ast.CallFunc) and len (stmt1.args) == 1 == len (stmt2.args) and\
	   not isinstance (stmt2.args [0], ast.Keyword) and\
	   not isinstance (stmt1.args [0], ast.Keyword) and\
	   repr (stmt1.node) == repr (stmt2.node) and\
	   stmt1.star_args == stmt2.star_args == stmt1.dstar_args == stmt2.dstar_args == None:
		return True
	return False

def stmts_get_base (stmt):
	if isinstance (stmt, ast.Assign):
		def setter (expr):
			stmt.expr = expr
			return stmt
		return setter
	if isinstance (stmt, ast.Yield):
		def setter (expr):
			stmt.value = expr
			return stmt
		return setter
	if isinstance (stmt, ast.Discard):
		if isinstance (stmt.expr, ast.CallFunc):
			def setter (expr):
				stmt.expr.args [0] = expr
				return stmt
			return setter
	if isinstance (stmt, ast.CallFunc):
		def setter (expr):
			stmt.args [0] = expr
			return stmt
		return setter

def stmts_get_diff (stmt):
	if isinstance (stmt, ast.Assign):
		return stmt.expr
	if isinstance (stmt, ast.Yield):
		return stmt.value
	if isinstance (stmt, ast.CallFunc):
		return stmt.args [0]
	if isinstance (stmt, ast.Discard):
		if isinstance (stmt.expr, ast.CallFunc):
			return stmt.expr.args [0]

def optimizeConditional (C):
	# This one can handle further optimization for
	#	if c: x = bar (foo (1))
	#	else: x = bar (foo (2))
	# which is converted to
	#	x = bar (foo (c ? 1 : 2))
	#
	if expr_eq_base (C.expr1, C.expr2):
		CC = ast.Conditional (C.cond, stmts_get_diff (C.expr1),
					 stmts_get_diff (C.expr2))
		optimizeConditional (CC)
		make_copy (C, stmts_get_base (C.expr1) (CC))

# TODO: There are other oportunities in the standard library
# exposed after optimizeConditiona. Frequent case is ast.Add
# and ast.Getattr
#--------------------------------------------------------------

def mark_targeted (node):
	# if ast.Or/ast.And/ast.Not is used in a conditional
	# (which means that the result will not be used, we only care
	# for its boolean value), add an attribute 'Targeted' to the node
	#
	if isinstance (node, ast.Or) or isinstance (node, ast.And):
		node.Targeted = True
		for i in node.nodes:
			mark_targeted (i)
	elif isinstance (node, ast.Not):
		node.Targeted = True
		mark_targeted (node.expr)
	node.Targeted = True

def bool_final_not (node):
	return (isinstance (node, ast.And) or isinstance (node, ast.Or))\
	 and isinstance (node.nodes [-1], ast.Not)

def neg_AST (node):
	if isinstance (node, ast.Not):
		return node.expr
	return ast.Not (node)

def make_const (node, val):
	node.__class__ = ast.Const
	ast.Const.__init__ (node, val)
	node.__name__ = ast.Const.__name__

def make_copy (nodep, nodec):
	for i in list (nodep.__dict__):
		delattr (nodep, i)
	for i in nodec.__dict__:
		setattr (nodep, i, getattr (nodec, i))
	nodep.__class__ = nodec.__class__
	nodep.__name__ = nodec.__class__.__name__

def ast_Assign (name, expr):
	return ast.Assign ([ast.AssName (name, 'OP_ASSIGN')], expr)

def ast_Getattr (name, attr):
	return ast.Getattr (ast.Name (name, 0), attr)

end_stmt = set ([ast.Return, ast.Raise, ast.Break, ast.Continue])

def List2Tuple (node):
	for i in node.nodes:
		if not i.isconst:
			# we should probably turn this into tuple as well
			break
	else:
		make_const (node, tuple ([x.value for x in node.nodes]))
		del node.nodes

class FoldConstVisitor:

	import operator

	compares = {
		'==': operator.eq,
		'!=': operator.ne,
		'<>': operator.ne,
		'<=': operator.le,
		'>=': operator.ge,
		'<': operator.lt,
		'>': operator.gt,
		'is': operator.is_,
		'is not': operator.is_not,
		'not in': lambda x,y: x not in y,	# python doesn't have operator not_in
		'in': operator.contains,
	}

	def defVisitUnary (FUNC):
		def visitUnary (self, node):
			self.visit (node.expr)
			if node.expr.isconst:
				try:
					make_const (node, FUNC (node.expr.value))
					del node.expr
				except:
					pass
		return visitUnary

	visitUnaryAdd = defVisitUnary (operator.pos)
	visitUnarySub = defVisitUnary (operator.neg)
	visitInvert = defVisitUnary (operator.inv)
	del defVisitUnary

	def defVisitBinary (FUNC):
		def visitBinaryOp (self, node):
			self.visit (node.left)
			self.visit (node.right)
			if node.left.isconst and node.right.isconst:
				try:
					make_const (node, FUNC (node.left.value, node.right.value))
					del node.left, node.right
				except:
					pass
		return visitBinaryOp

	visitAdd = defVisitBinary (operator.add)
	visitSub = defVisitBinary (operator.sub)
	visitDiv = defVisitBinary (operator.div)
	visitMod = defVisitBinary (operator.mod)
	visitLeftShift = defVisitBinary (operator.lshift)
	visitRightShift = defVisitBinary (operator.rshift)
	visitPower = defVisitBinary (operator.pow)
	del defVisitBinary

	def visitMul (self, node):
		self.visit (node.left)
		self.visit (node.right)
		if node.left.isconst and node.right.isconst:
			try:
				# We don't want to make things like "50000 * (0,)" constants!
				val = node.left.value * node.right.value
				if type (val) is str and len (val) > 30 or type (val) is tuple and\
				   len (var) > 10:
					return
				make_const (node, val)
				del node.left, node.right
			except:
				pass

	def defBitOp (FUNC):
		def visitMultiOp (self, node):
			all_const = True
			for i in node.nodes:
				self.visit (i)
				if all_const and not i.isconst:
					all_const = False
			if all_const:
				try:
					value = node.nodes [0].value
					for i in node.nodes [1:]:
						value = FUNC (value, i.value)
					make_const (node, value)
					del node.nodes
				except:
					pass
		return visitMultiOp

	visitBitand = defBitOp (operator.and_)
	visitBitor  = defBitOp (operator.or_)
	visitBitxor = defBitOp (operator.xor)
	del defBitOp

	negate_op = { 'in':'not in', 'is':'is not', 'is not':'is', 'not in':'in' }

	def visitNot (self, node):
		self.visit (node.expr)
		if node.expr.isconst:
			try:
				make_const (node, not node.expr.value)
				del node.expr
			except:
				pass
		elif is_compare (node.expr) and len (node.expr.ops) == 1 and \
		     node.expr.ops [0][0] in self.negate_op:
			# not a in b -- > a not in b
			# not a is b -- > a is not b
			# not a is not b -- > a is b
			# not a not in b -- > a in b
			node.expr.ops [0] = (self.negate_op [node.expr.ops [0][0]], node.expr.ops [0][1])
			make_copy (node, node.expr)

	def visitEarlyTerminator (self, node, FLAG):
		visit = self.visit
		for i in node.nodes:
			visit (i)
		while 1:
			if node.nodes [0].isconst and bool (node.nodes [0].value) == FLAG:
				make_const (node, node.nodes [0].value)
				break
			if hasattr (node, 'Targeted'):
				removables = [x for x in node.nodes if x.isconst and bool (x.value) == (not FLAG) ]
			else:
				removables = [x for x in node.nodes[:-1] if x.isconst and bool (x.value) == (not FLAG) ]
			if removables:
				for i in removables:
					node.nodes.remove (i)
				if not node.nodes:
					make_const (node, FLAG)
					break
				continue
			for i in node.nodes:
				if i.isconst and bool (i.value) == FLAG:
					node.nodes = node.nodes [:node.nodes.index (i)+1]
					break
			break
		if isinstance (node, ast.And) or isinstance (node, ast.Or):
			for i in node.nodes:
				if not isinstance (i, ast.Not):
					return
			# convert "not a or not b" -> "not (a and b)"
			opast = isinstance (node, ast.And) and ast.Or or ast.And
			node2 = ast.Not (opast ([i.expr for i in node.nodes]))
			make_copy (node, node2)
			opt_progress ('ast(!!)')

	def visitCompare (self, node):
		self.visit (node.expr)
		for i, code in node.ops:
			self.visit (code)
			if i in ('in', 'not in') and isinstance (code, ast.List):
				List2Tuple (code)
		if node.expr.isconst and len (node.ops) == 1 and node.ops [0][1].isconst:
			make_const (node, self.compares [node.ops [0][0]] (node.expr.value, node.ops [0][1].value))

	def visitOr (self, node):
		self.visitEarlyTerminator (node, True)
	def visitAnd (self, node):
		self.visitEarlyTerminator (node, False)

	def visitTuple (self, node):
		# Turn BUILD_TUPLE of consts to a const tuple
		#
		visit = self.visit
		all_consts = True
		for i in node.nodes:
			visit (i)
			if not i.isconst:
				all_consts = False
		if all_consts:
			make_const (node, tuple ([x.value for x in node.nodes]))
			del node.nodes

	def visitName (self, node, xlater = {'None':None, 'True':True, 'False':False}):
		if node.name in xlater:
			make_const (node, xlater [node.name])
			del node.name

	def visitIf (self, node):
		# eliminate if-const
		#
		removables = []
		trueconst = None
		visit = self.visit

		for test, body in node.tests:
			mark_targeted (test)
			visit (test)
			visit (body)
			if test.isconst:
				if not test.value:
					removables.append ((test, body))
				elif not trueconst:
					trueconst = test, body
			elif bool_final_not (test):
				#
				# convert "if a and not b --> if not (not a or b)"
				# we have a difficulty removing the UNARY_NOT in the first case...
				#
				make_copy (test, ast.Not ((isinstance (test, ast.And) and ast.Or or ast.And) ([
				neg_AST (i) for i in test.nodes])))
		if node.else_:
			visit (node.else_)
		for i in removables:
			node.tests.remove (i)
		if not node.tests:
			if node.else_:
				make_copy (node, node.else_)
			else:
				make_copy (node, ast.Pass (node.lineno))
		elif trueconst:
			if trueconst == node.tests [0]:
				make_copy (node, trueconst [1])
			else:
				node.else_ = trueconst [1]
				node.tests = node.tests [:node.tests.index (trueconst)]

		if not isinstance (node, ast.If):
			return

		node.fallthrough = False
		if node.else_:
			for test, stmt in node.tests:
				if not stmts_eq_base (stmt, node.else_):
					break
			else:
			##	print '*', repr (node)
				basenode = stmts_get_base (node.else_.nodes [0])
				N = stmts_get_diff (node.else_.nodes [0])
				for test, stmt in reversed (node.tests):
					N = ast.Conditional (test, stmts_get_diff
								 (stmt.nodes [0]), N)
					optimizeConditional (N)
				basenode = basenode (N)
				make_copy (node, basenode)
			##	print '*>>', repr (node)
				opt_progress (':?:')
		else:
			# fallthrough means that the end of the if block must not JUMP_FORWARD
			# past the POP_TOP.
			if isinstance (node.tests [-1][1].nodes [-1], ast.Discard):
				node.fallthrough = True
				opt_progress ('fth')
				node.tests [-1][1].nodes [-1] = node.tests [-1][1].nodes [-1].expr

	def visitStmt (self, node):
		# Remove statements with no effect (docstrings have already been acquired)
		# Remove nodes after Return/Raise/Break/Continue
		# If an 'if' statement has constant True condition, embody its Stmt and rerun
		#
		visit = self.visit
		for i in node.nodes:
			visit (i)
		while 1:
			for i, j in enumerate (node.nodes):
				if isinstance (j, ast.Stmt):
					node.nodes [i:i+1] = j.nodes
					break
			else:
				break

		for i, j in enumerate (node.nodes):
			if isinstance (j, ast.Discard) and j.expr.isconst:
				node.nodes [i] = ast.Pass (j.lineno)
			elif j.__class__ in end_stmt and node.nodes [i+1:]:
				node.nodes = node.nodes [:i+1]
				return

	def visitFor (self, node):
		self.visit (node.list)
		if isinstance (node.list, ast.List):
			List2Tuple (node.list)
		self.visit (node.assign)
		self.visit (node.body)
		if node.else_:
			self.visit (node.else_)

	del operator

#
# Constify Names
#

class NameConstifier:

	def __init__ (self, D, node):
		self.D = D
		self.K = set (D.keys ())
		self.constify_names (node)

	def constify_names (self, node):
		# Walk the AST tree and replace Name()s that belong in the dictionary D
		# with Const()s with the value of it.
		if isinstance (node, ast.Name):
			if node.name in self.D:
				make_const (node, self.D [node.name])
		elif isinstance (node, ast.AssName):
			if node.name in self.D:
				raise SyntaxError, "assign to constant '%s' at %s:%i" % (node.name,
					 GCO ['filename'], node.lineno)
		elif isinstance (node, ast.Function):
			if self.K | set (node.argnames):
				D = dict (self.D)
				for i in node.argnames:
					if i in self.K:
						del D [i]
				self.D, D = D, self.D
				for i in node.getChildNodes ():
					self.constify_names (i)
				self.D = D
			else:
				for i in node.getChildNodes ():
					self.constify_names (i)
		else:
			for i in node.getChildNodes ():
				self.constify_names (i)

#
# Known type optimizer (LIST_APPEND)
#

class TypeVisitor:

	def __init__ (self, typeof):
		self.typeof = typeof

	def visitDiscard (self, node):
		#
		# convert: Discard (CallFunc (Getattr (Name ('x'), 'append'), ["expression"]))
		# to:	   ListAppend (Name ('x'), "expression")
		#
		node2 = node.expr
		if isinstance (node2, ast.CallFunc) and\
		isinstance (node2.node, ast.Getattr) and node2.node.attrname == 'append' and\
		isinstance (node2.node.expr, ast.Name) and self.typeof (node2.node.expr.name) is list and\
		len (node2.args) == 1 and not node2.star_args and not node2.dstar_args:
			make_copy (node, ast.ListAppend (node2.node.expr, node2.args [0]))
			opt_progress ('LA')
		else:
			self.visit (node2)

def type_optimizer (root):
	if GCO ['arch'] == '2.3':
		# no LIST_APPEND in 2.3
		return

	for i in root.Functions:
		if i.symtab.know_types ():
			walk (i, TypeVisitor (i.symtab.typeof))

def rename (node, n1, n2):
	if isinstance (node, ast.Name) or isinstance (node, ast.AssName):
		if node.name == n1:
			node.name = n2
	else:
		for i in node.getChildNodes ():
			rename (i, n1, n2)

#
# Marshal builtins. This is an advanced NameConstifier
#
MB = set (__builtins__) & set (('IndexError', 'unicode', 'isinstance', 'NameError', 'dict', 'oct', 'repr',
	 'list', 'iter', 'round', 'cmp', 'set', 'reduce', 'intern', 'sum',
	 'getattr', 'abs', 'hash', 'len', 'frozenset', 'ord', 'TypeError', 'filter',
	 'range', 'pow', 'float', 'StopIteration', 'divmod', 'enumerate', 'apply', 'LookupError',
	 'basestring', 'zip', 'hex', 'long', 'chr', 'xrange', 'type', 'Exception', 'tuple',
	 'reversed', 'hasattr', 'delattr', 'setattr', 'str', 'property', 'int', 'KeyError',
	 'unichr', 'id', 'OSError', 'min', 'bool', 'ValueError', 'NotImplemented',
	# complex
	 'map', 'buffer', 'max', 'object', 'callable', 'ZeroDivisionError', 'AttributeError'))

def cc_builtin (root, names):
	for i in root.getChildNodes ():
		if isinstance (i, ast.Name):
			if i.name in names:
				make_copy (i, ast.Const (__builtins__ [i.name]))
		elif not isinstance (i, ast.Const):
			cc_builtin (i, names)

def marshal_builtins (module):
	s = module.symtab
	MMB = MB - set (s.defs)
	for i in module.Functions:
		s = i.symtab
		if s.globals | MMB:
			vg = s.globals | set (s.defs)
			MMB -= vg
	for i in module.Functions:
		bs = (MMB & i.symtab.uses)
		if bs:
			cc_builtin (i, bs)

#
# turn globals into closures
#
c_no, f_no = counter (), counter ()

def constification (func, spec):
	# takes an ast.Function node and a list of expressions
	# and replaces the node with a stmt which when executed will define
	# the function and closureify the expressions

	cvars = []
	for east in spec:
		cn = 'ClOsUrE%i__' % c_no()
		replace_ast (func.code, east, cn)
		cvars.append ((cn, east))
	func_name = func.name
	subfunc = ast.Function (func.decorators, func_name, func.argnames, func.defaults,
				func.flags, func.code, func.lineno)
	stmt = [ast.Assign ([ast.AssName (cn, 'OP_ASSIGN')], east) for cn, east in cvars]
	stmt.append (subfunc)
	stmt.append (ast.Return (ast.Name (func_name, 0)))
	fn = 'CoNsTiFiCaTiOn%i' % f_no()
	dfunc = ast.Function (None, fn, (), (), 0, ast.Stmt (stmt), 0)
	creat = ast.Stmt ([dfunc, ast_Assign (func_name, ast.CallFunc (ast.Name (fn, 0), ()))])
	# XXX add del(CoNsTiFiCaTiOn)
	make_copy (func, creat)

def replace_ast (root, r1, r2):
	if root.__class__ == r1.__class__ and repr (root) == repr (r1):
		opt_progress ('constified:[%s]' %repr (r1))
		make_copy (root, ast.Name (r2, 0))
		return
	for i in root.getChildNodes ():
		replace_ast (i, r1, r2)

#
# publicite
#

def constify_names (node, D):
	NameConstifier (D, node)

def optimize_tree (tree):
	walk(tree, FoldConstVisitor())
	type_optimizer (tree)

def pyc_constants (tree):
	for i in GCO ['funcs_with_consts']:
		D, C = [], []
		for j in i.decorators.nodes:
			if isinstance (j, ast.CallFunc) and isinstance (j.node, ast.Name) and\
			   j.node.name == '__pyc_closures__':
				C.extend (j.args)
			else:
				D.append (j)
		if D:
			i.decorators.nodes = D
		else:
			i.decorators = None
		constification (i, C)
