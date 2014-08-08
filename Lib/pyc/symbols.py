"""Module symbol-table generator"""

from gco	import GCO
from optimizer	import make_copy
from misc	import counter
import ast

try:
	SCOPE_GLOBAL
except:
	from consts import SCOPE_GLOBAL, SCOPE_FUNC, SCOPE_CLASS, SCOPE_GEXP

try:
	set
except:
	from sets import Set as set
	from misc import sorted

from misc	import counter
from visitor	import walk
from optimizer	import rename

class NoType: pass
class IgnoreType: pass

class Scope:

	def __init__(self, name, stype, module = None):
		self.name = name
		self.stype = stype
		if module:
			self.module = module
		else:
			self.module = self
		self.defs = {}
		self.uses = set ()
		self.globals = set ()
		self.params = set ()
		self.frees = set ()
		self.cells = set ()
		self.children = []
		# nested is true if the class could contain free variables,
		# i.e. if it is nested within another function.
		self.nested = None
		self.generator = None
		self.this = None
		self.add_use = self.uses.add
		self.dynlocals = GCO ['dynlocals']

	def add_def (self, name, Type = NoType):
		#
		# Simple type propagation.  We only handle the case where something
		# known is assigned to a local variable.   We assume that all other
		# names are of unknown type.  For instance in,
		#   def f ():
		#	x = []
		#	y = x
		# we don't know that 'y' is a list.  We do know it for 'x' though.
		#
		if name in self.defs:
			if self.defs [name] is not Type and Type is not IgnoreType:
				self.defs [name] = NoType
		else:
			#if Type == IgnoreType:
			#	print "Uninitialized local variable", name
			self.defs [name] = Type

	def __repr__(self):
		return "<%s: %s>" % (self.__class__.__name__, self.name)

	def add_global(self, name):
		# if name in self.uses or name in self.defs:
		#     pass # XXX warn about global following def/use
		if name in self.params:
			raise SyntaxError, "%s in %s is global and parameter" % \
                  (name, self.name)
		self.globals.add (name)
		self.module.add_def(name)

	def add_param(self, name):
		if not self.this:
			self.this = name
		self.add_def (name)
		self.params.add (name)

	def add_child(self, child):
		self.children.append(child)

	def check_name(self, name):
		# Return scope of name.
		#
		# The scope of a name could be LOCAL, GLOBAL, FREE, or CELL.
		# Also can be SC_UNDEF. Depending on the context this is either
		# a global or a local.
		if name in self.globals:
			return 'SC_GLOBAL'
		if name in self.cells:
			return 'SC_CELL'
		if name in self.defs:
			return 'SC_LOCAL'
		if self.nested:
			if name in self.frees or name in self.uses:
				return 'SC_FREE'
			return 'SC_UNKNOWN'
		return 'SC_UNDEF'

	def get_free_vars(self):
		if not self.nested:
			return ()
		free = self.frees | (self.uses - (self.globals | set (self.defs)))
		if not free:
			return ()
		return sorted (list (free))

	def handle_children(self):
		for child in self.children:
			frees = child.get_free_vars()
			Globals = self.add_frees(frees)
			for name in Globals:
				child.force_global(name)

	def force_global(self, name):
		# Force name to be global in scope.
		#
		# Some child of the current node had a free reference to name.
		# When the child was processed, it was labelled a free
		# variable.  Now that all its enclosing scope have been
		# processed, the name is known to be a global or builtin.  So
		# walk back down the child chain and set the name to be global
		# rather than free.
		#
		# Be careful to stop if a child does not think the name is
		# free.
		self.globals.add (name)
		self.frees.discard (name)
		for child in self.children:
			if child.check_name(name) == 'SC_FREE':
				child.force_global(name)

	def add_frees(self, names):
		# Process list of free vars from nested scope.
		#
		# Returns a list of names that are either 1) declared global in the
		# parent or 2) undefined in a top-level parent.  In either case,
		# the nested scope should treat them as globals.
		child_globals = []
		for name in names:
			sc = self.check_name(name)
			if self.nested:
				if sc == 'SC_UNKNOWN' or sc == 'SC_FREE' \
				or self.stype == SCOPE_CLASS:
					self.frees.add (name)
				elif sc == 'SC_GLOBAL':
					child_globals.append(name)
				elif self.stype in (SCOPE_FUNC, SCOPE_GEXP) and sc == 'SC_LOCAL':
					self.cells.add (name)
				elif sc != 'SC_CELL':
					child_globals.append(name)
			else:
				if sc == 'SC_LOCAL':
					self.cells.add (name)
				elif sc != 'SC_CELL':
					child_globals.append(name)
		return child_globals

	def get_cell_vars(self):
		return list (self.cells)

	# types

	def know_types (self):
		for v in self.defs.itervalues ():
			if v is not NoType:

			##	print "KNOW STUFF:", self.name
			##	for k, v in self.defs.iteritems ():
			##		if v is not NoType:
			##			print k, v
				return True
		return False

	def typeof (self, name):
		# embrace and extend
		try:
			return self.defs [name]
		except:
			return NoType

def ModuleScope ():
	return Scope ("global", SCOPE_GLOBAL)

def FunctionScope (name, module):
	return Scope (name, SCOPE_FUNC, module)

gcounter = counter ()

def GenExprScope (module):
	S = Scope ("generator expression<%i>"%gcounter(), SCOPE_GEXP, module)
	S.add_param ('[outmost-iterable]')	# kludge
	return S

def LambdaScope (module):
	return Scope ("lambda.%d", SCOPE_FUNC, module)

def ClassScope (name, module):
	return Scope (name, SCOPE_CLASS, module)

class SymbolVisitor:

	# node that define new scopes

	def visitModule(self, node):
		scope = self.module = node.symtab = ModuleScope()
		node.symtab = scope
		scope.Functions = node.Functions = []
		self.visit(node.node, scope)

		'''
		# this removes function definitions out of the function.
		CCF = []
		for i in scope.Functions:
			s = i.symtab
			if s.nested:
				frees = s.get_free_vars ()
				if len (frees) > 1:
					continue
				if len (frees) == 1 and i.name not in frees:
					continue
				CCF.append (i)
		if CCF:
			print GCO ['filename']
			print len (CCF)
			for i in CCF:
				print i.name
				print i.parent
				print i.symtab.get_free_vars ()
		'''

		del self.module

	visitExpression = visitModule

	def visitFunction(self, node, parent):
		if node.decorators:
			self.visit(node.decorators, parent)
		parent.add_def(node.name)
		for n in node.defaults:
			self.visit(n, parent)
		scope = FunctionScope (node.name, self.module)
		self.module.Functions.append (node)
		if parent.nested or parent.stype == SCOPE_FUNC:
			scope.nested = 1
		node.symtab = scope
		node.parent = parent
		self._do_args(scope, node.argnames)

		self.visit(node.code, scope)
		self.handle_free_vars(scope, parent)

	def visitGenExpr(self, node, parent):
		scope = GenExprScope(self.module)
		if parent.nested or parent.stype == SCOPE_FUNC \
                or parent.stype == SCOPE_GEXP:
			scope.nested = 1

		node.symtab = scope
		self.visit(node.code, scope)

		# Must visit the qual[0].iter at the parent node
		self.visit(node.code.outmost_iterable, parent)	# genexp-1

		self.handle_free_vars(scope, parent)

	def visitGenExprInner(self, node, scope):
		for genfor in node.quals:
			self.visit(genfor, scope)

		self.visit(node.expr, scope)

	def visitGenExprFor(self, node, scope):
		self.visit(node.assign, scope, 1)
		if not node.is_outmost:		# genexp-1
			self.visit(node.iter, scope)
		for if_ in node.ifs:
			self.visit(if_, scope)

	def visitGenExprIf(self, node, scope):
		self.visit(node.test, scope)

	def visitLambda(self, node, parent, assign=0):
		# Lambda is an expression, so it could appear in an expression
		# context where assign is passed.  The transformer should catch
		# any code that has a lambda on the left-hand side.
		assert not assign

		for n in node.defaults:
			self.visit(n, parent)
		scope = LambdaScope(self.module)
		if parent.nested or parent.stype in (SCOPE_FUNC, SCOPE_GEXP):
			scope.nested = 1
		node.symtab = scope
		self._do_args(scope, node.argnames)
		self.visit(node.code, scope)
		self.handle_free_vars(scope, parent)

	def _do_args(self, scope, args):
		for name in args:
			if type(name) is tuple:
				self._do_args(scope, name)
			else:
				if name [0] == '$':
					name = name [1:]
				scope.add_param(name)

	def handle_free_vars(self, scope, parent):
		parent.add_child(scope)
		scope.handle_children()

	def visitClass(self, node, parent):
		parent.add_def(node.name)
		for n in node.bases:
			self.visit(n, parent)
		scope = ClassScope(node.name, self.module)
		if parent.nested or parent.stype == SCOPE_FUNC:
			scope.nested = 1
		if node.doc is not None:
			scope.add_def('__doc__')
		scope.add_def('__module__')
		node.symtab = scope
		self.visit(node.code, scope)
		self.handle_free_vars(scope, parent)

	# name can be a def or a use

	# XXX a few calls and nodes expect a third "assign" arg that is
	# true if the name is being used as an assignment.  only
	# expressions contained within statements may have the assign arg.

	def visitName(self, node, scope, assign=0):
		if assign:
			scope.add_def(node.name, IgnoreType)
		else:
			scope.add_use(node.name)

	# operations that bind new names

	def visitFor(self, node, scope):
		self.visit(node.assign, scope, NoType)
		self.visit(node.list, scope)
		self.visit(node.body, scope)
		if node.else_:
			self.visit(node.else_, scope)

	def visitFrom(self, node, scope):
		for name, asname in node.names:
			if name == "*":
				continue
			scope.add_def(asname or name)

	def visitImport(self, node, scope):
		for name, asname in node.names:
			i = name.find(".")
			if i > -1:
				name = name[:i]
			scope.add_def(asname or name)

	def visitGlobal(node, scope):
		for name in node.names:
			scope.add_global(name)
	visitGlobal = staticmethod (visitGlobal)

	def visitAssign(self, node, scope):
		# Propagate assignment flag down to child nodes.
		#
		# The Assign node doesn't itself contains the variables being
		# assigned to.  Instead, the children in node.nodes are visited
		# with the assign flag set to true.  When the names occur in
		# those nodes, they are marked as defs.
		#
		# Some names that occur in an assignment target are not bound by
		# the assignment, e.g. a name occurring inside a slice.  The
		# visitor handles these nodes specially; they do not propagate
		# the assign flag to their children.
		if isinstance (node.expr, ast.List) or isinstance (node.expr, ast.ListComp):
			t = list

#		elif isinstance (node.expr, ast.Const) and type (node.expr.value) is int:
#			t = type (node.expr.value)
#			for n in node.nodes:
#				self.visit(n, scope, type (node.expr.value))

##		elif isinstance (node.expr, ast.Dict):
#			for n in node.nodes:
#				self.visit(n, scope, dict)

		else:
			t = NoType
		for n in node.nodes:
			self.visit(n, scope, t)
		self.visit(node.expr, scope)

	def visitAssTuple (self, node, scope, assign=NoType):
		#
		# at the moment we do not handle type propagation for tuple assignments,
		# that is: x,y,z = [], 1, 'foo'
		#
		for i in node.nodes:
			self.visit (i, scope, NoType)

	def visitAssName(self, node, scope, assign=NoType):
		scope.add_def(node.name, assign)

	def visitAssAttr(self, node, scope, assign=0):
		self.visit(node.expr, scope, 0)

	def visitSubscript(self, node, scope, assign=0):
		self.visit(node.expr, scope, 0)
		self.visit(node.sub, scope, 0)

	def visitSlice(self, node, scope, assign=0):
		self.visit(node.expr, scope, 0)
		if node.lower:
			self.visit(node.lower, scope, 0)
		if node.upper:
			self.visit(node.upper, scope, 0)

	def visitAugAssign(self, node, scope):
		# If the LHS is a name, then this counts as assignment.
		# Otherwise, it's just use.
		self.visit(node.node, scope)

		# commented out so that 'x += 1' does not make x a local
		# dunno if this is the right way. If add_def does more maybe
		# we should do something. YYYY.
#		if isinstance(node.node, ast.Name):
#			self.visit(node.node, scope, NoType) # XXX worry about this
		self.visit(node.expr, scope)

	# prune if statements if tests are false

	def visitIf(self, node, scope):
		for test, body in node.tests:
			self.visit(test, scope)
			self.visit(body, scope)
		if node.else_:
			self.visit(node.else_, scope)

	# if calls locals() or dir() set dynlocals flag

	def visitCallFunc (self, node, scope, assign=0):
		if isinstance (node.node, ast.Name) and (node.node.name == 'locals'\
		or (node.node.name == 'dir' and not node.args)):
			scope.dynlocals = True
		self = self.visit
		for i in node.getChildNodes ():
			self (i, scope)

	# a yield statement signals a generator

	def visitYield(self, node, scope):
		scope.generator = 1
		self.visit(node.value, scope)


#
# Attach an object 'symtab' to every ast node that defines a scope
# (module, function, class, lambda, genexp). So after parseSymbols
# we can request the 'symtab' attribute from ast nodes.  The most
# important function of the symtab is check_name(), which takes a
# name and returns its scope (SC_GLOBAL, SC_LOCAL, SC_FREE, ...)
#
# Also, create a list 'Functions' at the root node, which is a list
# that contains all the ast nodes that define functions.
#
def parseSymbols (tree):
	walk (tree, SymbolVisitor ())
