#
# Python abstract syntax node definitions
#
# Also here we have the eval-AST
#

from gco	import GCO
from consts	import CO_VARARGS, CO_VARKEYWORDS
from misc	import NullIter

def ast2code (tree, mode):
	# hook
	print 'Module pycodegen not initialized'
	raise SystemExit

def flatten (lst):
	l = []
	for elt in lst:
		t = type (elt)
		if t is tuple or t is list:
			l.extend (flatten (elt))
		else:
			l.append (elt)
	return l

def flatten_nodes(lst):
	return [n for n in flatten (lst) if isinstance (n, Node)]

def extract_doc(stmt):
	if stmt.__class__ != Stmt or not stmt.nodes:
		return None
	stmt1 = stmt.nodes [0]
	if stmt1.__class__ == Discard and stmt1.expr.__class__ == Const\
	and type (stmt1.expr.value) in (str, unicode):
		return stmt.nodes.pop (0).expr.value
	return None

class Node:
	isconst=0
	def eval (self):
		print "***** ADD eval() to ast node:", self.__class__
		raise SyntaxError ("No eval for node %s" % self.__class__)
	def __repr__ (self):
		return "%s(%s)" %(self.__class__.__name__, ", ".join ([repr (x) for x in self.getChildNodes()]))

# common base properties

class NodeLeftRight (Node):
	def eval (self):
		l = self.left.eval ()
		r = self.right.eval ()
		n = self.__name__
		if n <= 'Mod':
			if n == 'Add': return l+r
			if n == 'Mod': return l%r
			if n == 'Div': return l/r
			return l<<r
		if n == 'Sub': return l-r
		if n == 'Mul': return l*r
		if n == 'Power': return l**r
		return l>>r
	def __init__(self, (left, right)):
		self.left = left
		self.right = right
	def getChildNodes(self):
		yield self.left
		yield self.right
	def __repr__(self):
		return "%s((%r,%r))" % (self.__class__.__name__, self.left, self.right)

class NodeNodes (Node):

	def __init__ (self, nodes):
		self.nodes = nodes
	def __repr__(self):
		return "%s(%r)" % (self.__class__.__name__, self.nodes)

class NodeNodesList (NodeNodes):

	def getChildNodes (self):
		return self.nodes

class NodeExpr (Node):

	def __init__ (self, expr):
		self.expr = expr
	def getChildNodes(self):
		return self.expr,
	def __repr__(self):
		return "%s(%r)" % (self.__class__.__name__, self.expr)

class NodeNoChild (Node):

	def __init__(self, lineno=None):
		self.lineno = lineno

	getChildNodes = NullIter

	def __repr__(self):
		return "%s()" % (self.__class__.__name__,)

# actual nodes

class Expression(Node):
	# Expression is an artificial node class to support "eval"
	def __init__(self, node):
		self.node = node
	def eval (self):
		return self.node.eval ()
	def getChildNodes(self):
		return self.node,

class Add(NodeLeftRight):
	pass

class And(NodeNodesList):

	def eval (self):
		for i in self.nodes:
			x = i.eval ()
			if not x:
				return x
		return x

class AssAttr(Node):
	def __init__(self, expr, attrname, flags):
		self.expr = expr
		self.attrname = attrname
		self.flags = flags

	def getChildNodes(self):
		yield self.expr

	def __repr__(self):
		return "AssAttr(%r, %s, %r)" % (self.expr, self.attrname, self.flags)

class AssList(NodeNodes):
	def __init__(self, nodes, lineno=None):
		self.nodes = nodes
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.nodes))
		return tuple(nodelist)

class AssName(Node):
	def __init__(self, name, flags, lineno=None):
		self.name = name
		self.flags = flags
		self.lineno = lineno

	getChildNodes = NullIter

	def __repr__(self):
		return "AssName(%r, %r)" % (self.name, self.flags)

class AssTuple(NodeNodesList):
	def __init__(self, nodes, lineno=None):
		self.nodes = nodes
		self.lineno = lineno

class Assert(Node):
	def __init__(self, test, fail, lineno=None):
		self.test = test
		self.fail = fail
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.append(self.test)
		if self.fail is not None:
			nodelist.append(self.fail)
		return tuple(nodelist)

	def __repr__(self):
		return "Assert(%r, %r)" % (self.test, self.fail)

class Assign(Node):
	def __init__(self, nodes, expr, lineno=None):
		self.discarded = False
		self.nodes = nodes
		self.expr = expr
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.nodes))
		nodelist.append(self.expr)
		return tuple(nodelist)

	def __repr__(self):
		return "Assign(%r, %r)" % (self.nodes, self.expr)

class AugAssign(Node):
	def __init__(self, node, op, expr, lineno=None):
		self.discarded = False
		self.node = node
		self.op = op
		self.expr = expr
		self.lineno = lineno

	def getChildNodes(self):
		return self.node, self.expr

	def __repr__(self):
		return "AugAssign(%r, %r, %r)" % (self.node, self.op, self.expr)

class Backquote(NodeExpr):
	def __init__(self, expr, lineno=None):
		self.expr = expr
		self.lineno = lineno

class Bitand(NodeNodesList):
	def eval (self):
		n = self.nodes [0].eval ()
		for i in self.nodes [1:]:
			n &= i.eval ()
		return n

class Bitor(NodeNodesList):
	def eval (self):
		n = self.nodes [0].eval ()
		for i in self.nodes [1:]:
			n |= i.eval ()
		return n

class Bitxor(NodeNodesList):
	def eval (self):
		n = self.nodes [0].eval ()
		for i in self.nodes [1:]:
			n ^= i.eval ()
		return n

class Break(NodeNoChild):
	pass

class CallFunc(Node):
	def __init__(self, node, args, star_args = None, dstar_args = None, lineno=None):
		self.node = node
		self.args = args
		self.star_args = star_args
		self.dstar_args = dstar_args
		self.lineno = lineno

	def eval (self):
		if not self.star_args and not self.dstar_args:
			if not isinstance (self.args [-1], Keyword):
				return self.node.eval () (*[x.eval () for x in self.args])

	def getChildNodes(self):
		nodelist = []
		nodelist.append(self.node)
		nodelist.extend(flatten_nodes(self.args))
		if self.star_args is not None:
			nodelist.append(self.star_args)
		if self.dstar_args is not None:
			nodelist.append(self.dstar_args)
		return tuple(nodelist)

	def __repr__(self):
		return "CallFunc(%r, %r, %r, %r)" % (self.node, self.args, self.star_args, self.dstar_args)

class Class(Node):
	def __init__(self, name, bases, code, lineno=None):
		self.name = name
		self.bases = bases
		self.doc = extract_doc (code)
		self.code = code
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.bases))
		nodelist.append(self.code)
		return tuple(nodelist)

	def __repr__(self):
		return "Class(%r, %r, %r, %r)" % (self.name, self.bases, self.doc, self.code)

import operator

_cmpops = {
	'>': operator.gt,
	'<': operator.lt,
	'>=': operator.ge,
	'<=': operator.le,
	'==': operator.eq,
	'!=': operator.ne,
	'is': operator.is_,
	'is not': operator.is_not,
	'in': operator.contains,
	'not in': lambda x,y: x not in y
}

del operator

def cmpop (v1, op, v2):
	return _cmpops [op](v1, v2)

class Compare(Node):
	def __init__(self, expr, ops, lineno=None):
		self.expr = expr
		self.ops = ops
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = [self.expr]
		nodelist.extend(flatten_nodes(self.ops))
		return tuple(nodelist)

	def eval (self):
		e0 = self.expr.eval ()
		for o, e in self.ops:
			e = e.eval ()
			if not cmpop (e0, o, e):
				return False
		return True

	def __repr__(self):
		return "Compare(%r, %r)" % (self.expr, self.ops)

class Const(Node):

	isconst=1

	def __init__(self, value, lineno=None):
		self.value = value
		self.lineno = lineno

	def eval (self):
		return self.value

	getChildNodes = NullIter

	def __repr__(self):
		return "Const(%r)" % self.value

class Continue(NodeNoChild):
	pass

class Decorators(NodeNodes):
	def __init__(self, nodes, lineno=None):
		self.nodes = nodes
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.nodes))
		return tuple(nodelist)

class Dict(Node):
	def __init__(self, items, lineno=None):
		self.items = items
		if not items:	# xxx compatibility with python's package. empty dict has a tuple
			self.items = ()
		self.lineno = lineno

	def eval (self):
		return dict ([(k.eval (), v.eval ()) for k, v in self.items])

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.items))
		return tuple(nodelist)

	def __repr__(self):
		return "Dict(%s)" % repr (self.items)

class Discard(Node):
	def __init__(self, expr, lineno=None):
		self.expr = expr
		self.lineno = lineno

	def getChildNodes(self):
		yield self.expr

class Div(NodeLeftRight):
	pass

class Ellipsis(NodeNoChild):
	pass

class Exec(Node):
	def __init__(self, expr, locals, globals, lineno=None):
		# XXX: experiment
		self.expr = expr
		self.locals = locals
		self.globals = globals
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.append(self.expr)
		if self.locals is not None:
			nodelist.append(self.locals)
		if self.globals is not None:
			nodelist.append(self.globals)
		return tuple(nodelist)

	def __repr__(self):
		return "Exec(%r, %r, %r)" % (self.expr, self.locals, self.globals)

class FloorDiv(NodeLeftRight):
	pass

class For(Node):
	def __init__(self, assign, lst, body, else_, lineno=None):
		self.assign = assign
		self.list = lst
		self.body = body
		self.else_ = else_
		self.lineno = lineno

	def getChildNodes(self):
		if self.else_:
			return self.assign, self.list, self.body, self.else_
		return self.assign, self.list, self.body

	def __repr__(self):
		return "For(%r, %r, %r, %r)" % (self.assign, self.list, self.body, self.else_)

class From(NodeNoChild):
	def __init__(self, modname, names, lineno=None):
		self.modname = modname
		self.names = names
		self.lineno = lineno

	def __repr__(self):
		return "From(%r, %r)" % (self.modname, self.names)

class Function(Node):
	def __init__(self, decorators, name, argnames, defaults, flags, code, lineno=None):
		if decorators is not None:
			for i in decorators.nodes:
				if isinstance (i, CallFunc) and\
	        isinstance (i.node, Name) and i.node.name == '__pyc_closures__':
					GCO ['funcs_with_consts'].add (self)
		self.decorators = decorators
		self.name = name
		self.argnames = argnames
		self.defaults = defaults
		self.flags = flags
		self.doc = extract_doc (code)
		self.code = code
		self.lineno = lineno
		self.varargs = self.kwargs = None
		if flags & CO_VARARGS:
			self.varargs = 1
		if flags & CO_VARKEYWORDS:
			self.kwargs = 1

	def getChildNodes(self):
		nodelist = []
		if self.decorators is not None:
			nodelist.append(self.decorators)
		nodelist.extend(flatten_nodes(self.defaults))
		nodelist.append(self.code)
		return tuple(nodelist)

	def __repr__(self):
		return "Function(%r, %r, %r, %r, %r, %r, %r)" % (self.decorators, self.name, self.argnames, self.defaults, self.flags, self.doc, self.code)

class GenExpr(Node):
	def __init__(self, code, lineno=None):
		self.code = code
		self.lineno = lineno
		self.argnames = ['[outmost-iterable]']
		self.varargs = self.kwargs = None

	def getChildNodes(self):
		return self.code,

class GenExprFor(Node):
	def __init__(self, assign, Iter, ifs, lineno=None):
		self.assign = assign
		self.iter = Iter
		self.ifs = ifs
		self.lineno = lineno
		self.is_outmost = False

	def getChildNodes(self):
		nodelist = []
		nodelist.append(self.assign)
		nodelist.append(self.iter)
		nodelist.extend(flatten_nodes(self.ifs))
		return tuple(nodelist)

	def __repr__(self):
		return "GenExprFor(%r, %r, %r)" % (self.assign, self.iter, self.ifs)

class GenExprIf(Node):
	def __init__(self, test, lineno=None):
		self.test = test
		self.lineno = lineno

	def getChildNodes(self):
		return self.test,

class GenExprInner(Node):
	def __init__(self, expr, quals, lineno=None):
		self.expr = expr
		self.quals = quals
		quals [0].is_outmost = True
		self.outmost_iterable = quals [0].iter	# genexp-1
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.append(self.expr)
		nodelist.extend(flatten_nodes(self.quals))
		return tuple(nodelist)

	def __repr__(self):
		return "GenExprInner(%r, %r)" % (self.expr, self.quals)

class Getattr(Node):
	def __init__(self, expr, attrname):
		self.expr = expr
		self.attrname = attrname

	def getChildNodes(self):
		yield self.expr

	def __repr__(self):
		return "Getattr(%r, %r)" % (self.expr, self.attrname)

class Global(NodeNoChild):
	def __init__(self, names, lineno=None):
		self.names = names
		self.lineno = lineno

	def __repr__(self):
		return "Global(%r)" % self.names

class If(Node):
	def __init__(self, tests, else_, lineno=None):
		self.tests = tests
		self.else_ = else_
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = flatten_nodes(self.tests)
		if self.else_:
			nodelist.append(self.else_)
		return tuple(nodelist)

	def __repr__(self):
		return "If(%r, %r)" % (self.tests, self.else_)

class Import(NodeNoChild):
	def __init__(self, names, lineno=None):
		self.names = names
		self.lineno = lineno

	def __repr__(self):
		return "Import(%r)" % self.names

class Invert(NodeExpr):
	def eval (self):
		return ~ self.expr.eval ()

class Keyword(Node):
	def __init__(self, name, expr, lineno=None):
		self.name = name
		self.expr = expr
		self.lineno = lineno

	def getChildNodes(self):
		yield self.expr

	def __repr__(self):
		return "Keyword(%r, %r)" % (self.name, self.expr)

class Lambda(Node):
	def __init__(self, argnames, defaults, flags, code, lineno=None):
		self.argnames = argnames
		self.defaults = defaults
		self.flags = flags
		self.code = code
		self.lineno = lineno
		self.varargs = self.kwargs = None
		if flags & CO_VARARGS:
			self.varargs = 1
		if flags & CO_VARKEYWORDS:
			self.kwargs = 1

	def eval (self):
		return eval (ast2code (Expression (self), 'eval'))	# eval (code-object)

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.defaults))
		nodelist.append(self.code)
		return tuple(nodelist)

	def __repr__(self):
		return "Lambda(%r, %r, %r, %r)" % (self.argnames, self.defaults, self.flags, self.code)

class LeftShift(NodeLeftRight):
	pass

class List(NodeNodesList):
	def __init__(self, nodes, lineno=None):
		self.nodes = nodes
		self.lineno = lineno

	def eval (self):
		return [x.eval() for x in self.nodes]

class ListComp(Node):
	def __init__(self, expr, quals, lineno=None):
		self.expr = expr
		self.quals = quals
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = [self.expr]
		nodelist.extend(flatten_nodes(self.quals))
		return tuple(nodelist)

	def __repr__(self):
		return "ListComp(%r, %r)" % (self.expr, self.quals)

class ListCompFor(Node):
	def __init__(self, assign, List, ifs, lineno=None):
		self.assign = assign
		self.list = List
		self.ifs = ifs
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = [self.assign, self.list]
		nodelist.extend(flatten_nodes(self.ifs))
		return tuple(nodelist)

	def __repr__(self):
		return "ListCompFor(%r, %r, %r)" % (self.assign, self.list, self.ifs)

class ListCompIf(Node):
	def __init__(self, test, lineno=None):
		self.test = test
		self.lineno = lineno

	def getChildNodes(self):
		yield self.test

class Mod(NodeLeftRight):
	pass

class Module(Node):
	def __init__(self, node, lineno=None):
		self.doc = extract_doc (node)
		self.node = node
		self.lineno = lineno

	def getChildNodes(self):
		return self.node,

	def __repr__(self):
		return "Module(%r, %r)" % (self.doc, self.node)

	def Import (self, name):
		self.node.nodes.insert (0, Import ([(name, name)]))

class Mul(NodeLeftRight):
	pass

class Name(Node):
	def __init__(self, name, lineno):
		self.name = name
		self.lineno = lineno

	def eval (self):
		return GCO ['eval_lookup'] (self.name)

	getChildNodes = NullIter

	def __repr__(self):
		return "Name(%r)" % self.name

class Not(NodeExpr):
	def __init__(self, expr, lineno=None):
		self.expr = expr
		self.lineno = lineno

	def eval (self):
		return not self.expr.eval ()

class Or(NodeNodesList):
	def eval (self):
		for i in self.nodes:
			x = i.eval ()
			if x:
				return x
		return x

class Pass(NodeNoChild):
	pass

class Power(NodeLeftRight):
	pass

class Print(Node):
	def __init__(self, nodes, dest, lineno=None):
		self.nodes = nodes
		self.dest = dest
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.nodes))
		if self.dest is not None:
			nodelist.append(self.dest)
		return tuple(nodelist)

	def __repr__(self):
		return "Print(%r, %r)" % (self.nodes, self.dest)

class Printnl(Node):
	def __init__(self, nodes, dest, lineno=None):
		self.nodes = nodes
		self.dest = dest
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.nodes))
		if self.dest is not None:
			nodelist.append(self.dest)
		return tuple(nodelist)

	def __repr__(self):
		return "Printnl(%r, %r)" % (self.nodes, self.dest)

class Raise(Node):
	def __init__(self, expr1, expr2, expr3, lineno=None):
		self.expr1 = expr1
		self.expr2 = expr2
		self.expr3 = expr3
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		if self.expr1 is not None:
			nodelist.append(self.expr1)
		if self.expr2 is not None:
			nodelist.append(self.expr2)
		if self.expr3 is not None:
			nodelist.append(self.expr3)
		return tuple(nodelist)

	def __repr__(self):
		return "Raise(%r, %r, %r)" % (self.expr1, self.expr2, self.expr3)

class Return(Node):
	def __init__(self, value):
		self.value = value

	def getChildNodes(self):
		yield self.value

class RightShift(NodeLeftRight):
	pass

class Slice(Node):
	def __init__(self, expr, flags, lower, upper, lineno=None):
		self.expr = expr
		self.flags = flags
		self.lower = lower
		self.upper = upper
		self.lineno = lineno

	def getChildNodes(self):
		if self.lower:
			if self.upper:
				return self.expr, self.lower, self.upper
			return self.expr, self.lower
		if self.upper:
			return self.expr, self.upper
		return self.expr,

	def __repr__(self):
		return "Slice(%r, %r, %r, %r)" % (self.expr, self.flags, self.lower, self.upper)

class Sliceobj(NodeNodes):
	def __init__(self, nodes, lineno=None):
		self.nodes = nodes
		for i in range (len (nodes)):
			if not nodes [i]:
				nodes [i] = Const (None)
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.extend(flatten_nodes(self.nodes))
		return tuple(nodelist)

def mark_discarded (nodes):
	for i in nodes:
		if isinstance (i, Assign) or isinstance (i, AugAssign):
			i.discarded = True

class Stmt(NodeNodesList):
	def __init__(self, nodes, lineno=None):
		mark_discarded (nodes) # # # # assignment-as-expression stuff
		self.nodes = nodes
		self.lineno = lineno

	def add_globals (self, names):
		self.nodes.insert (0, Global (names))

class Sub(NodeLeftRight):
	pass

class Subscript(Node):
	def __init__(self, expr, flags, subs, lineno=None):
		self.expr = expr
		self.flags = flags
		if len (subs) == 1:
			self.sub = subs [0]
		else:
			self.sub = Tuple (subs)
		self.lineno = lineno

	def getChildNodes(self):
		return self.expr, self.sub

	def __repr__(self):
		return "Subscript(%r, %r, %r)" % (self.expr, self.flags, self.sub)

class TryExcept(Node):
	def __init__(self, body, handlers, else_, lineno=None):
		self.body = body
		self.handlers = handlers
		self.else_ = else_
		self.lineno = lineno

	def getChildNodes(self):
		nodelist = []
		nodelist.append(self.body)
		nodelist.extend(flatten_nodes(self.handlers))
		if self.else_ is not None:
			nodelist.append(self.else_)
		return tuple(nodelist)

	def __repr__(self):
		return "TryExcept(%r, %r, %r)" % (self.body, self.handlers, self.else_)

class TryFinally(Node):
	def __init__(self, body, final, lineno=None):
		self.body = body
		self.final = final
		self.lineno = lineno

	def getChildNodes(self):
		return self.body, self.final

class Tuple(NodeNodesList):
	def __init__(self, nodes, lineno=None):
		self.nodes = nodes
		self.lineno = lineno

	def eval (self):
		return tuple ([x.eval() for x in self.nodes])

class UnaryAdd(NodeExpr):
	def eval (self):
		return + self.expr.eval ()

class UnarySub(NodeExpr):
	def eval (self):
		return - self.expr.eval ()

class While(Node):
	def __init__(self, test, body, else_, lineno=None):
		self.test = test
		self.body = body
		self.else_ = else_
		self.lineno = lineno

	def getChildNodes(self):
		if self.else_:
			return self.test, self.body, self.else_
		return self.test, self.body

	def __repr__(self):
		return "While(%r, %r, %r)" % (self.test, self.body, self.else_)

class Yield(Node):
	def __init__(self, value):
		self.value = value

	def getChildNodes(self):
		yield self.value

# *-*-*-* new ones *-*-*-*

class ListAppend(Node):
	# generated by the type annotator
	def __init__ (self, lst, expr):
		self.lst = lst
		self.expr = expr

	def getChildNodes (self):
		yield self.lst
		yield self.expr

class Conditional(Node):
	# generated by the optimizer if two branches are the same STORE
	def __init__ (self, cond, expr1, expr2):
		self.cond = cond
		self.expr1 = expr1
		self.expr2 = expr2

	def getChildNodes (self):
		yield self.cond
		yield self.expr1
		yield self.expr2

class With(Node):
	# removed at the transformer
	def __init__ (self, expr, var, code, lineno=None):
		self.expr = expr
		self.var = var
		self.code = code
		self.lineno = lineno
		GCO ['have_with'] = True

	def getChildNodes (self):
		yield self.expr
		yield self.code

	def __repr__ (self):
		return 'With (%r, %r, %r)' % (self.expr, self.var, self.code)

del NullIter
