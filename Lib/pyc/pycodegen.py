from visitor import walk
from codeobj import CodeObject, RealCode, ConstCollector
import ast
import pyassem
import misc
from gco import GCO
opt_progress = misc.opt_progress

'''
def CSE (B, ss):
	##print ss.graph.name
	L = []
	for b in B [1:]:
		I = []
		for op, arg in b.insts[1:]:
			if op == 'SET_LINENO' or op == 'LOAD_ATTR':
				continue
			if op == 'LOAD_FAST' or op == 'LOAD_GLOBAL':
				I.append ((op, arg))
			else:
				break
		L.append (I)
	for i in L:
		if not i or i[0] != L[0][0]:
			print 'xXx',
			break
	else:
		print L
'''

try:
	CO_NESTED
except:
	from consts import CO_VARARGS, CO_VARKEYWORDS, CO_NEWLOCALS,\
         	       CO_NESTED, CO_GENERATOR, CO_GENERATOR_ALLOWED, CO_FUTURE_DIVISION

from pyassem import TupleArg

callfunc_opcode_info = {
	# (Have *args, Have **args) : opcode
	(False,False) : "CALL_FUNCTION",
	( True,False) : "CALL_FUNCTION_VAR",
	( True, True) : "CALL_FUNCTION_VAR_KW",
	(False, True) : "CALL_FUNCTION_KW",
}

def neg_jump (jump):
	if jump == 'JUMP_IF_FALSE':
		return 'JUMP_IF_TRUE'
	return 'JUMP_IF_FALSE'

def last_exit (node):
	if isinstance (node, ast.Stmt) and node.nodes:
		last = node.nodes [-1]
		if isinstance (last, ast.Return):
			return True
		elif isinstance (last, ast.Raise):
			return True
		elif isinstance (last, ast.If):
			if not last.else_ or not last_exit (last.else_):
				return False
			for i in last.tests:
				if not last_exit (i [1]):
					return False
			return True
# doesn't work
#	elif isinstance (last, ast.TryExcept):
#	    if not last_exit (last.body):
#		return False
#	    for i in last.handlers:
#		if not last_exit (i [2]):
#		    return False
#	    return True
	return False

# global options

def ast2code (tree, mode):
	if mode == 'eval':
		return RealCode (ExpressionCodeGenerator (tree).getCode ())
	elif mode == 'single':
		return RealCode (InteractiveCodeGenerator (tree).getCode ())
	return RealCode (ModuleCodeGenerator (tree).getCode ())

class CodeGenerator:
	# Defines basic code generator for Python bytecode
	#
	# This class is an abstract base class.  Concrete subclasses must
	# define an __init__() that defines self.graph and then calls the
	# __init__() defined in this class.
	#
	# The concrete class must also define the class attributes
	# NameFinder, FunctionGen, and ClassGen.  These attributes can be
	# defined in the initClass() method, which is a hook for
	# initializing these methods after all the classes have been
	# defined.

	__initialized = None

	def __init__(self):
		if self.__initialized is None:
			self.initClass()
			self.__class__.__initialized = 1
		self.setups = []
		self.last_lineno = None
		self._setupGraphDelegation()
		self.Py2Extensions = GCO ['py2ext']

	def initClass(self):
		"""This method is called once for each class"""

	def _setupGraphDelegation(self):
		self.emit = self.graph.emit
		self.newBlock = self.graph.newBlock
		self.startBlock = self.graph.startBlock
		self.nextBlock = self.graph.nextBlock
		self.setDocstring = self.graph.setDocstring

	def getCode(self):
		"""Return a code object"""
		return CodeObject (self.graph.getCodeParams ())

	def get_module(self):
		raise RuntimeError, "should be implemented by subclasses"

	# Next five methods handle name access

	def delName (prefix):
		D = {
			'SC_LOCAL':'_NAME',
			'SC_GLOBAL':'_GLOBAL',
			'SC_UNDEF':'_NAME',
			'SC_FREE':'_DEREF',
			'SC_CELL':'_DEREF'
		}
		for i, j in D.items ():
			D [i] = intern (prefix + j)
		def NameOp (self, name):
			self.emit (D [self.scope.check_name (name)], name)
		return NameOp

	storeName = delName ('STORE')
	loadName = delName ('LOAD')
	delName = delName ('DELETE')

	def _implicitNameOp(self, prefix, name):
		self.emit(prefix + '_NAME', name)

	# The set_lineno() function and the explicit emit() calls for
	# SET_LINENO below are only used to generate the line number table.
	# As of Python 2.3, the interpreter does not have a SET_LINENO
	# instruction.  pyassem treats SET_LINENO opcodes as a special case.

	def set_lineno(self, node):
		# Emit SET_LINENO if necessary.
		#
		# The instruction is considered necessary if the node has a
		# lineno attribute and it is different than the last lineno
		# emitted.
		#
		# Returns true if SET_LINENO was emitted.
		#
		# In pyc, the rules for emitting a lineno, is that a lineno is
		# emitted only for ast.Name() nodes. What can be broken about that?
		# Some things apparently.  Also emit for ast.Function, ast.Class, ast.Raise
		lineno = node.lineno
		if lineno != self.last_lineno:
			self.emit('SET_LINENO', lineno)
			self.last_lineno = lineno

	# The first few visitor methods handle nodes that generator new
	# code objects.  They use class attributes to determine what
	# specialized code generators to use.

	FunctionGen = None
	ClassGen = None

	def visitModule(self, node):
		self.scope = node.symtab
		self.emit('SET_LINENO', 0)
		if node.doc:
			self.emit('LOAD_CONST', node.doc)
			self.storeName('__doc__')
		self.visit(node.node)
		self.emit('LOAD_CONST', None)
		self.emit('RETURN_VALUE')

	def visitExpression(self, node):
		self.scope = node.symtab
		self.visit(node.node)
		self.emit('RETURN_VALUE')

	def visitFunction(self, node):
		self._visitFuncOrLambda(node, isLambda=0, hasReturn = last_exit (node.code))
		if '.' not in node.name:
			self.storeName(node.name)
		else:
			name, attr = node.name.split ('.')
			node = ast.AssAttr (ast.Name (name, self.last_lineno), attr, 'OP_ASSIGN')
			self.visitAssAttr (node)
			self.name = attr

	def visitLambda(self, node):
		self._visitFuncOrLambda(node, isLambda=1)

	def _visitFuncOrLambda(self, node, isLambda=0, hasReturn=0):
		if not isLambda and node.decorators:
			for decorator in node.decorators.nodes:
				self.visit(decorator)
			ndecorators = len(node.decorators.nodes)
		else:
			ndecorators = 0

		gen = self.FunctionGen(node, isLambda, self.get_module())
		gen.hasReturn = hasReturn

		walk(node.code, gen)
		gen.finish()
		self.set_lineno (node)
		for default in node.defaults:
			self.visit(default)
		frees = gen.scope.get_free_vars()
		if frees:
			for name in frees:
				self.emit('LOAD_CLOSURE', name)
			self.emit('LOAD_CONST', gen.getCode ())
			self.emit('MAKE_CLOSURE', len(node.defaults))
		else:
			self.emit('LOAD_CONST', gen.getCode ())
			self.emit('MAKE_FUNCTION', len(node.defaults))

		for i in range(ndecorators):
			self.emit('CALL_FUNCTION', 1)

	def visitClass(self, node):
		gen = self.ClassGen (node, self.get_module ())
		walk(node.code, gen)
		gen.finish()
		self.set_lineno (node)
		self.emit('LOAD_CONST', node.name)
		for base in node.bases:
			self.visit(base)
		self.emit('BUILD_TUPLE', len(node.bases))
		frees = gen.scope.get_free_vars()
		for name in frees:
			self.emit('LOAD_CLOSURE', name)
		self.emit('LOAD_CONST', gen.getCode ())
		if frees:
			self.emit('MAKE_CLOSURE', 0)
		else:
			self.emit('MAKE_FUNCTION', 0)
		self.emit('CALL_FUNCTION', 0)
		self.emit('BUILD_CLASS')
		self.storeName(node.name)

	# The rest are standard visitor methods

	# The next few implement control-flow statements

	def visitIf(self, node):
		end = self.newBlock()

		for test, suite in node.tests:
			nextTest = self.newBlock ()
			self.visitBoolean (test, 'JUMP_IF_FALSE', nextTest)

			self.nextBlock()

			self.emit('POP_TOP')
			self.visit(suite)
			if last_exit (suite):
				self.startBlock(nextTest)
				self.emit('POP_TOP')
				continue
			if not (node.fallthrough and test is node.tests [-1][0]):
				self.emit('JUMP_FORWARD', end)

			self.startBlock(nextTest)
			self.emit('POP_TOP')
		if node.else_:
			self.visit(node.else_)

		self.nextBlock(end)

	def visitConditional (self, node):
		end = self.newBlock ()
		nextTest = self.newBlock ()
		self.visitBoolean (node.cond, 'JUMP_IF_FALSE', nextTest)
		self.nextBlock ()
		self.emit('POP_TOP')
		self.visit (node.expr1)
		self.emit ('JUMP_FORWARD', end)
		self.startBlock (nextTest)
		self.emit ('POP_TOP')
		self.visit (node.expr2)
		self.nextBlock (end)

	def visitBoolean (self, node, jump, target):
		if isinstance (node, ast.Not):
			self.visitBoolean (node.expr, neg_jump (jump), target)
			opt_progress ('!')
		else:
			self.visit (node)
			self.emit (jump, target)

	def visitWhile(self, node):
		loop = self.newBlock()
		else_ = self.newBlock()
		after = self.newBlock()

		need_setup = have_break (node.body)
		if need_setup:
			self.emit('SETUP_LOOP', after)
		else:
			opt_progress ('L')

		self.nextBlock(loop)
		self.setups.append(('LOOP', loop))

		self.visitBoolean (node.test, 'JUMP_IF_FALSE', else_ or after)

		self.nextBlock()
		self.emit('POP_TOP')
		self.visit(node.body)
		self.emit('JUMP_ABSOLUTE', loop)

		self.startBlock(else_) # or just the POPs if not else clause
		self.emit('POP_TOP')
		if need_setup:
			self.emit('POP_BLOCK')
		self.setups.pop()

		if node.else_:
			self.visit(node.else_)
		self.nextBlock(after)

	def visitFor(self, node):
		start = self.newBlock()
		anchor = self.newBlock()
		after = self.newBlock()

		need_setup = have_break (node.body)
		if need_setup:
			self.emit ('SETUP_LOOP', after)
		else:
			opt_progress ('L')
		self.setups.append(('LOOP', start))

		self.visit(node.list)
		self.emit('GET_ITER')

		self.nextBlock(start)
		self.emit('FOR_ITER', anchor)
		self.visit(node.assign)
		self.visit(node.body)
		self.emit('JUMP_ABSOLUTE', start)
		self.nextBlock(anchor)

		if need_setup:
			self.emit('POP_BLOCK')
		self.setups.pop()

		if node.else_:
			self.visit(node.else_)
		self.nextBlock(after)

	def visitBreak(self, node):
		if not self.setups:
			raise SyntaxError, "'break' outside loop (%s, %d)" % \
                  (node.filename, node.lineno)
		self.emit('BREAK_LOOP')

	def visitContinue(self, node):
		if not self.setups:
			raise SyntaxError, "'continue' outside loop (%s, %d)" % \
                  (node.filename, node.lineno)
		kind, block = self.setups [-1]

		in_eh = False
		if kind == 'EXCEPT_HANDLER':
			in_eh = True
			for kind, block in reversed (self.setups):
				if kind != 'EXCEPT_HANDLER':
					break
			else:
				raise SyntaxError, "'continue' outside loop (%s, %d)" % \
                  (node.filename, node.lineno)

		if kind == 'LOOP':
			#
			# 3 POP 
			#
			if in_eh:
				self.emit ('POP_TOP')
				self.emit ('POP_TOP')
				self.emit ('POP_TOP')
			self.emit('JUMP_ABSOLUTE', block)
			self.nextBlock()
		elif kind == 'EXCEPT' or kind == 'TRY_FINALLY':
			# find the block that starts the loop
			top = len(self.setups)
			while top > 0:
				top = top - 1
				kind, loop_block = self.setups[top]
				if kind == 'LOOP':
					break
			if kind != 'LOOP':
				raise SyntaxError, "'continue' outside loop (%s, %d)" % \
                		      (node.filename, node.lineno)
			self.emit('CONTINUE_LOOP', loop_block)
			self.nextBlock()
		elif kind == 'END_FINALLY':
			msg = "'continue' not allowed inside 'finally' clause (%s, %d)"
			raise SyntaxError, msg % (node.filename, node.lineno)

	def visitTest(self, node, jump):
		end = self.newBlock()
		for child in node.nodes[:-1]:
			self.visit(child)
			self.emit(jump, end)
			self.nextBlock()
			self.emit('POP_TOP')
		self.visit(node.nodes[-1])
		self.nextBlock(end)

	def visitAnd(self, node):
		self.visitTest(node, 'JUMP_IF_FALSE')

	def visitOr(self, node):
		self.visitTest(node, 'JUMP_IF_TRUE')

	def visitCompare(self, node):
		self.visit(node.expr)
		cleanup = self.newBlock()
		for op, code in node.ops[:-1]:
			self.visit(code)
			self.emit('DUP_TOP')
			self.emit('ROT_THREE')
			self.emit('COMPARE_OP', op)
			self.emit('JUMP_IF_FALSE', cleanup)
			self.nextBlock()
			self.emit('POP_TOP')
		# now do the last comparison
		if node.ops:
			op, code = node.ops[-1]
			self.visit(code)
			self.emit('COMPARE_OP', op)
		if len(node.ops) > 1:
			end = self.newBlock()
			self.emit('JUMP_FORWARD', end)
			self.startBlock(cleanup)
			self.emit('ROT_TWO')
			self.emit('POP_TOP')
			self.nextBlock(end)

	# list comprehensions
	__list_count = 0

	def visitListComp(self, node):
		# setup list
		append = "_[%d]" % self.__list_count
		self.__list_count += 1
		self.emit('BUILD_LIST', 0)
		self.emit('DUP_TOP')
		if GCO ['arch'] == '2.3':
			self.emit ('LOAD_ATTR', 'append')
		self._implicitNameOp('STORE', append)

		stack = []
		for for_ in node.quals:
			start, anchor = self.visit(for_)
			cont = None
			for if_ in for_.ifs:
				if cont is None:
					cont = self.newBlock()
				self.visit(if_, cont)
			stack.insert(0, (start, cont, anchor))

		self._implicitNameOp('LOAD', append)
		self.visit(node.expr)

		if GCO ['arch'] == '2.3':
			self.emit ('CALL_FUNCTION', 1)
			self.emit ('POP_TOP')
		else:
			self.emit ('LIST_APPEND')

		for start, cont, anchor in stack:
			if cont:
				skip_one = self.newBlock()
				self.emit('JUMP_FORWARD', skip_one)
				self.startBlock(cont)
				self.emit('POP_TOP')
				self.nextBlock(skip_one)
			self.emit('JUMP_ABSOLUTE', start)
			self.startBlock(anchor)
		self._implicitNameOp('DELETE', append)

		self.__list_count -= 1

	def visitListCompFor(self, node):
		start = self.newBlock()
		anchor = self.newBlock()

		self.visit(node.list)
		self.emit('GET_ITER')
		self.nextBlock(start)
		self.emit('FOR_ITER', anchor)
		self.nextBlock()
		self.visit(node.assign)
		return start, anchor

	def visitListCompIf(self, node, branch):
		self.visitBoolean (node.test, 'JUMP_IF_FALSE', branch)
		self.nextBlock()
		self.emit('POP_TOP')

	def visitGenExpr(self, node):
		gen = GenExprCodeGenerator (node, self.get_module ())
		walk(node.code, gen)
		gen.finish()
		frees = gen.scope.get_free_vars()
		if frees:
			for name in frees:
				self.emit('LOAD_CLOSURE', name)
			self.emit('LOAD_CONST', gen.getCode ())
			self.emit('MAKE_CLOSURE', 0)
		else:
			self.emit('LOAD_CONST', gen.getCode ())
			self.emit('MAKE_FUNCTION', 0)

        # precomputation of outmost iterable

		self.visit(node.code.quals[0].iter)

		self.emit('GET_ITER')
		self.emit('CALL_FUNCTION', 1)

	def visitGenExprInner(self, node):
		stack = []
		for i, for_ in zip(range(len(node.quals)), node.quals):
			start, anchor = self.visit(for_)
			cont = None
			for if_ in for_.ifs:
				if cont is None:
					cont = self.newBlock()
				self.visit(if_, cont)
			stack.insert(0, (start, cont, anchor))

		self.visit(node.expr)
		self.emit('YIELD_VALUE')

		for start, cont, anchor in stack:
			if cont:
				skip_one = self.newBlock()
				self.emit('JUMP_FORWARD', skip_one)
				self.startBlock(cont)
				self.emit('POP_TOP')
				self.nextBlock(skip_one)
			self.emit('JUMP_ABSOLUTE', start)
			self.startBlock(anchor)
		self.emit('LOAD_CONST', None)

	def visitGenExprFor(self, node):
		start = self.newBlock()
		anchor = self.newBlock()

		if node.is_outmost:
			self.loadName('[outmost-iterable]')
		else:
			self.visit(node.iter)
			self.emit('GET_ITER')

		self.nextBlock(start)
		self.emit('FOR_ITER', anchor)
		self.nextBlock()
		self.visit(node.assign)
		return start, anchor

	def visitGenExprIf(self, node, branch):
		self.visitBoolean (node.test, 'JUMP_IF_FALSE', branch)
		self.nextBlock()
		self.emit('POP_TOP')

	# exception related

	def visitAssert(self, node):
		# XXX would be interesting to implement this via a
		# transformation of the AST before this stage
		if __debug__ and GCO ['Asserts']:
			end = self.newBlock()
			# XXX AssertionError appears to be special case -- it is always
			# loaded as a global even if there is a local name.  I guess this
			# is a sort of renaming op.
			self.nextBlock()
			self.visit(node.test)
			self.emit('JUMP_IF_TRUE', end)
			self.nextBlock()
			self.emit('POP_TOP')
			self.emit('LOAD_GLOBAL', 'AssertionError')
			if node.fail:
				self.visit(node.fail)
				self.emit('RAISE_VARARGS', 2)
			else:
				self.emit('RAISE_VARARGS', 1)
			self.nextBlock(end)
			self.emit('POP_TOP')

	def visitRaise(self, node):
		self.set_lineno (node)
		n = 0
		for i in node.expr1, node.expr2, node.expr3:
			if i:
				self.visit (i)
				n += 1
		self.emit('RAISE_VARARGS', n)

	def visitTryExcept(self, node):
		self.graph.enterTry ()
		body = self.newBlock()
		self.graph.leaveTry ()

		handlers = self.newBlock()
		end = self.newBlock()
		if node.else_:
			lElse = self.newBlock()
		else:
			lElse = end
		self.emit('SETUP_EXCEPT', handlers)
		self.nextBlock(body)
		self.setups.append(('EXCEPT', body))

		self.graph.enterTry ()
		self.visit(node.body)
		self.graph.leaveTry ()

		self.emit('POP_BLOCK')
		self.setups.pop()
		self.emit('JUMP_FORWARD', lElse)
		self.startBlock(handlers)

		self.setups.append (('EXCEPT_HANDLER', None))
		for expr, target, body in node.handlers:
			if expr:
				self.emit('DUP_TOP')
				self.visit(expr)
				self.emit('COMPARE_OP', 'exception match')
				next = self.newBlock()
				self.emit('JUMP_IF_FALSE', next)
				self.nextBlock()
				self.emit('POP_TOP')

			# -*- unlike CPython compiler -*-
			#
			# The exception *remains* on the stack during all of the
			# 'except' body.  CPython doesn't need that, but it's the
			# right thing to do for faster and neater exception handling ;)
			#
			if target:
				self.emit ('ROT_TWO')
				self.emit ('DUP_TOP')
				self.visit (target)
				self.emit ('ROT_TWO')
			self.visit(body)
			self.emit ('POP_TOP')
			self.emit ('POP_TOP')
			self.emit ('POP_TOP')
			self.emit('JUMP_FORWARD', end)

			if expr:
				self.nextBlock(next)
				self.emit('POP_TOP')
			else:
				self.nextBlock()
		self.setups.pop ()
		self.emit('END_FINALLY')
		if node.else_:
			self.nextBlock(lElse)
			self.visit(node.else_)
		self.nextBlock(end)

	def visitTryFinally(self, node):

		self.graph.enterTry ()
		body = self.newBlock()
		self.graph.leaveTry ()

		final = self.newBlock()
		self.emit('SETUP_FINALLY', final)
		self.nextBlock(body)
		self.setups.append(('TRY_FINALLY', body))

		self.graph.enterTry ()
		self.visit(node.body)
		self.graph.leaveTry ()

		self.emit('POP_BLOCK')
		self.setups.pop()
		self.emit('LOAD_CONST', None)
		self.nextBlock(final)
		self.setups.append(('END_FINALLY', final))
		self.visit(node.final)
		self.emit('END_FINALLY')
		self.setups.pop()

	# misc

	def visitDiscard(self, node):
		self.visit(node.expr)
		self.emit('POP_TOP')

	def visitConst(self, node):
		self.emit('LOAD_CONST', node.value)

	def visitKeyword(self, node):
		self.emit('LOAD_CONST', node.name)
		self.visit(node.expr)

	def visitGlobal(self, node):
		pass

	def visitName(self, node):
		self.set_lineno (node)
		self.loadName(node.name)

	def visitPass(self, node):
		pass

	def visitImport(self, node):
		for name, alias in node.names:
			self.emit('LOAD_CONST', None)
			self.emit('IMPORT_NAME', name)
			mod = name.split(".")[0]
			if alias:
				self._resolveDots(name)
				self.storeName(alias)
			else:
				self.storeName(mod)

	def visitFrom(self, node):
		fromlist = map(lambda (name, alias): name, node.names)
		self.emit('LOAD_CONST', tuple(fromlist))
		self.emit('IMPORT_NAME', node.modname)
		for name, alias in node.names:
			if name == '*':
				self.namespace = 0
				self.emit('IMPORT_STAR')
				# There can only be one name w/ from ... import *
				return
			else:
				self.emit('IMPORT_FROM', name)
				self._resolveDots(name)
				self.storeName(alias or name)
		self.emit('POP_TOP')

	def _resolveDots(self, name):
		elts = name.split(".")
		if len(elts) == 1:
			return
		for elt in elts[1:]:
			self.emit('LOAD_ATTR', elt)

	def visitGetattr(self, node):
		self.visit(node.expr)
		self.emit('LOAD_ATTR', node.attrname)

	# next five implement assignments

	def visitAssign(self, node):
		self.visit(node.expr)
		dups = len(node.nodes) - 1
		if not node.discarded:
			##if not self.Py2Extensions:
			##	raise SyntaxError, "assignment as an expression is not allowed"
			self.emit('DUP_TOP')
		if not dups:
			self.visit (node.nodes [0])
		else:
			for i in range(len(node.nodes)):
				elt = node.nodes[i]
				if i < dups:
					self.emit('DUP_TOP')
				if isinstance(elt, ast.Node):
					self.visit(elt)

	def visitAssName(self, node):
		# XXX set_lineno!
		if node.flags == 'OP_ASSIGN':
			self.storeName(node.name)
		else: ### node.flags == 'OP_DELETE'
			self.delName(node.name)

	def visitAssAttr(self, node):
		self.visit(node.expr)
		if node.flags == 'OP_ASSIGN':
			self.emit('STORE_ATTR', node.attrname)
		else: ### node.flags == 'OP_DELETE'
			self.emit('DELETE_ATTR', node.attrname)

	def _visitAssSequence(self, node):
		if findOp(node) != 'OP_DELETE':
			self.emit('UNPACK_SEQUENCE', len(node.nodes))
		for child in node.nodes:
			self.visit(child)

	visitAssTuple = _visitAssSequence
	visitAssList = _visitAssSequence

	# augmented assignment

	def visitAugAssign(self, node):
		aug_node = wrap_aug(node.node)
		self.visit(aug_node, "load")
		self.visit(node.expr)
		self.emit(self._augmented_opcode[node.op])
		if not node.discarded:
			if not self.Py2Extensions:
				raise SyntaxError, "augmented assignment as an expression is not allowed"
			self.emit ('DUP_TOP')
			self.visit(aug_node, "stored")
		else:
			self.visit(aug_node, "store")

	_augmented_opcode = {
		'+=' : 'INPLACE_ADD',
		'-=' : 'INPLACE_SUBTRACT',
		'*=' : 'INPLACE_MULTIPLY',
		'/=' : 'INPLACE_DIVIDE',
		'//=': 'INPLACE_FLOOR_DIVIDE',
		'%=' : 'INPLACE_MODULO',
		'**=': 'INPLACE_POWER',
		'>>=': 'INPLACE_RSHIFT',
		'<<=': 'INPLACE_LSHIFT',
		'&=' : 'INPLACE_AND',
		'^=' : 'INPLACE_XOR',
		'|=' : 'INPLACE_OR',
	}

	def visitAugName(self, node, mode):
		if mode == "load":
			self.loadName(node.name)
		elif mode == "store" or mode == 'stored':
			self.storeName(node.name)

	def visitAugGetattr(self, node, mode):
		if mode == "load":
			self.visit(node.expr)
			self.emit('DUP_TOP')
			self.emit('LOAD_ATTR', node.attrname)
		elif mode == "store":
			self.emit('ROT_TWO')
			self.emit('STORE_ATTR', node.attrname)
		elif mode == 'stored':
			self.emit('ROT_THREE')
			self.emit('ROT_TWO')
			self.emit('STORE_ATTR', node.attrname)

	def visitAugSlice(self, node, mode):
		if mode == "load":
			self.visitSlice(node, 1)
		elif mode == "store":
			slice = 0
			if node.lower:
				slice = slice | 1
			if node.upper:
				slice = slice | 2
			if slice == 0:
				self.emit('ROT_TWO')
			elif slice == 3:
				self.emit('ROT_FOUR')
			else:
				self.emit('ROT_THREE')
			self.emit('STORE_SLICE+%d' % slice)
		elif mode == 'stored':
			raise NotImplemented ('pyc: STORED subscript')

	def visitAugSubscript(self, node, mode):
		if mode == "load":
			self.visitSubscript(node, 1)
		elif mode == "store":
			self.emit('ROT_THREE')
			self.emit('STORE_SUBSCR')
		elif mode == 'stored':	# need ROT_FOUR
			raise NotImplemented ('pyc: STORED subscript')

	def visitExec(self, node):
		self.visit(node.expr)
		if node.locals is None:
			self.emit('LOAD_CONST', None)
		else:
			self.visit(node.locals)
		if node.globals is None:
			self.emit('DUP_TOP')
		else:
			self.visit(node.globals)
		self.emit('EXEC_STMT')

	def visitCallFunc(self, node):
		pos = 0
		kw = 0

		self.visit(node.node)
		for arg in node.args:
			self.visit(arg)
			if isinstance(arg, ast.Keyword):
				kw += 1
			else:
				pos += 1
		if node.star_args is not None:
			self.visit(node.star_args)
		if node.dstar_args is not None:
			self.visit(node.dstar_args)
		have_star = node.star_args is not None
		have_dstar = node.dstar_args is not None
		opcode = callfunc_opcode_info[(have_star, have_dstar)]
		self.emit(opcode, kw << 8 | pos)

	def visitListAppend (self, node):
		self.visit (node.lst)
		self.visit (node.expr)
		self.emit ('LIST_APPEND')

	def visitPrint(self, node, newline=0):
		if node.dest:
			self.visit(node.dest)
		for child in node.nodes:
			if node.dest:
				self.emit('DUP_TOP')
			self.visit(child)
			if node.dest:
				self.emit('ROT_TWO')
				self.emit('PRINT_ITEM_TO')
			else:
				self.emit('PRINT_ITEM')
		if node.dest and not newline:
			self.emit('POP_TOP')

	def visitPrintnl(self, node):
		self.visitPrint(node, newline=1)
		if node.dest:
			self.emit('PRINT_NEWLINE_TO')
		else:
			self.emit('PRINT_NEWLINE')

	def visitReturn(self, node):
		raise SyntaxError ("return outside function")

	def visitYield(self, node):
		self.visit(node.value)
		self.emit('YIELD_VALUE')

	# slice and subscript stuff

	def visitSlice(self, node, aug_flag=None):
		# aug_flag is used by visitAugSlice
		self.visit(node.expr)
		slice = 0
		if node.lower:
			self.visit(node.lower)
			slice |= 1
		if node.upper:
			self.visit(node.upper)
			slice |= 2
		if aug_flag:
			if slice == 0:
				self.emit('DUP_TOP')
			elif slice == 3:
				self.emit('DUP_TOPX', 3)
			else:
				self.emit('DUP_TOPX', 2)
		if node.flags == 'OP_APPLY':
			self.emit('SLICE+%d' % slice)
		elif node.flags == 'OP_ASSIGN':
			self.emit('STORE_SLICE+%d' % slice)
		elif node.flags == 'OP_DELETE':
			self.emit('DELETE_SLICE+%d' % slice)
		else:
			print "weird slice", node.flags
			raise

	SUBSCR = {
		'OP_APPLY':'BINARY_SUBSCR',
		'OP_ASSIGN':'STORE_SUBSCR',
		'OP_DELETE':'DELETE_SUBSCR'
	}

	def visitSubscript(self, node, aug_flag=None):
		self.visit(node.expr)
		self.visit(node.sub)
		if aug_flag:
			self.emit('DUP_TOPX', 2)
		self.emit (self.SUBSCR [node.flags])

	# binary ops

	def visitFloorDiv (OP):
		def binaryOp (self, node):
			self.visit (node.left)
			self.visit (node.right)
			self.emit (OP)
		return binaryOp

	visitAdd = visitFloorDiv ('BINARY_ADD')
	visitSub = visitFloorDiv ('BINARY_SUBTRACT')
	visitMul = visitFloorDiv ('BINARY_MULTIPLY')
	visitDiv = visitFloorDiv ('BINARY_DIVIDE')
	visitMod = visitFloorDiv ('BINARY_MODULO')
	visitPower = visitFloorDiv ('BINARY_POWER')
	visitLeftShift = visitFloorDiv ('BINARY_LSHIFT')
	visitRightShift = visitFloorDiv ('BINARY_RSHIFT')
	visitFloorDiv = visitFloorDiv ('BINARY_FLOOR_DIVIDE')

	# unary ops

	def visitBackquote (OP):
		def unaryOp (self, node):
			self.visit (node.expr)
			self.emit (OP)
		return unaryOp

	visitInvert = visitBackquote ('UNARY_INVERT')
	visitUnarySub = visitBackquote ('UNARY_NEGATIVE')
	visitUnaryAdd = visitBackquote ('UNARY_POSITIVE')
	visitNot = visitBackquote ('UNARY_NOT')
	visitBackquote = visitBackquote ('UNARY_CONVERT')

	# bit ops

	def visitBitxor (OP):
		def bitOp (self, node):
			node = node.nodes
			self.visit (node [0])
			for n in node [1:]:
				self.visit (n)
				self.emit (OP)
		return bitOp

	visitBitand = visitBitxor ('BINARY_AND')
	visitBitor = visitBitxor ('BINARY_OR')
	visitBitxor = visitBitxor ('BINARY_XOR')

	# object constructors

	def visitEllipsis(self, node):
		self.emit('LOAD_CONST', Ellipsis)

	def visitTuple (OP):
		def nodesop (self, node):
			for elt in node.nodes:
				self.visit (elt)
			self.emit (OP, len (node.nodes))
		return nodesop

	visitList = visitTuple ('BUILD_LIST')
	visitSliceObj = visitTuple ('BUILD_SLICE')
	visitTuple = visitTuple ('BUILD_TUPLE')

	def visitDict(self, node):
		self.emit('BUILD_MAP', 0)
		for k, v in node.items:
			self.emit('DUP_TOP')
			self.visit(k)
			self.visit(v)
			self.emit('ROT_THREE')
			self.emit('STORE_SUBSCR')

class NestedScopeMixin:
	# Defines initClass() for nested scoping (Python 2.2-compatible)
	def initClass(self):
		self.__class__.FunctionGen = FunctionCodeGenerator
		self.__class__.ClassGen = ClassCodeGenerator

class ModuleCodeGenerator(NestedScopeMixin, CodeGenerator):
	__super_init = CodeGenerator.__init__

	def __init__(self, tree):
		if GCO ['gnt']:
			GCO ['global_names_list'] = []
		if GCO ['gnc']:
			GCO ['global_consts_list'] = ConstCollector()
		self.graph = pyassem.PyFlowGraph24("?")
		self.__super_init()
		walk(tree, self)

	def get_module(self):
		return self

class ExpressionCodeGenerator(NestedScopeMixin, CodeGenerator):
	__super_init = CodeGenerator.__init__

	def __init__(self, tree):
		self.graph = pyassem.PyFlowGraph24("<expression>")
		self.__super_init()
		walk(tree, self)

	def get_module(self):
		return self

class InteractiveCodeGenerator(NestedScopeMixin, CodeGenerator):

	__super_init = CodeGenerator.__init__

	def __init__(self, tree):
		self.graph = pyassem.PyFlowGraph24("<interactive>")
		self.__super_init()
		walk(tree, self)
		self.emit('RETURN_VALUE')

	def get_module(self):
		return self

	def visitDiscard(self, node):
		# XXX Discard means it's an expression.  Perhaps this is a bad
		# name.		(yes it is. Ed.)
		self.visit(node.expr)
		self.emit('PRINT_ITEM')
		self.emit ('PRINT_NEWLINE')

class AbstractFunctionCode:
	codename = '<lambda>'

	def delName (prefix):
		D = {
			'SC_LOCAL':'_FAST',
			'SC_GLOBAL':'_GLOBAL',
			'SC_UNDEF':'_GLOBAL',
			'SC_FREE':'_DEREF',
			'SC_CELL':'_DEREF'
		}
		for i, j in D.items ():
			D [i] = intern (prefix + j)
		def NameOp (self, name):
			self.emit (D [self.scope.check_name (name)], name)
		return NameOp

	storeName = delName ('STORE')
	loadName = delName ('LOAD')
	delName = delName ('DELETE')

	def _implicitNameOp(self, prefix, name):
		self.emit(prefix + '_FAST', name)

	def __init__(self, func, isLambda, mod):
		self.hasReturn = False
		self.module = mod
		if isLambda:
			klass = FunctionCodeGenerator
			name = self.codename
		else:
			name = func.name
			if '.' in name:
				name = name.split ('.')[1]

		args, hasTupleArg, hasMemberArg = generateArgList(func.argnames)
		self.graph = pyassem.PyFlowGraph24(name, args,
                                         optimized=1, dynlocals=func.symtab.dynlocals, isfunc=True)
		self.isLambda = isLambda
		self.super_init()

		if not isLambda and func.doc:
			self.setDocstring(func.doc)

		if func.varargs:
			self.graph.setFlag(CO_VARARGS)
		if func.kwargs:
			self.graph.setFlag(CO_VARKEYWORDS)
		if hasTupleArg:
			self.generateArgUnpack(func.argnames)
		if hasMemberArg:
			self.generateMemberArg (func.argnames)

	def get_module(self):
		return self.module

	def finish(self):
		self.graph.startExitBlock()

		if not self.hasReturn:
			if not self.isLambda:
				self.emit('LOAD_CONST', None)
			self.emit('RETURN_VALUE')

	def generateArgUnpack(self, args):
		for i in range(len(args)):
			arg = args[i]
			if type(arg) is tuple:
				self.emit('LOAD_FAST', '.%d' % (i * 2))
				self.unpackSequence(arg)

	def generateMemberArg (self, args):
		for i in args:
			if i [0] == '$':
				self.emit ('LOAD_FAST', i [1:])
				self.emit ('LOAD_FAST', 'self')
				self.emit ('STORE_ATTR', i [1:])

	def unpackSequence(self, tup):
		self.emit('UNPACK_SEQUENCE', len(tup))
		for elt in tup:
			if type(elt) is tuple:
				self.unpackSequence(elt)
			else:
				self.storeName (elt)

	unpackTuple = unpackSequence

class FunctionCodeGenerator(NestedScopeMixin, AbstractFunctionCode,
                            CodeGenerator):
	super_init = CodeGenerator.__init__ # call the other init

	__super_init = AbstractFunctionCode.__init__

	def __init__ (self, func, isLambda, mod):
		self.scope = func.symtab
		self.__super_init (func, isLambda, mod)
		self.graph.setFreeVars (self.scope.get_free_vars())
		self.graph.setCellVars (self.scope.get_cell_vars())
		if self.scope.generator is not None:
			self.graph.setFlag(CO_GENERATOR)

	def visitReturn(self, node):
		self.visit(node.value)
		self.emit('RETURN_VALUE')


class GenExprCodeGenerator(NestedScopeMixin, AbstractFunctionCode,
                           CodeGenerator):
	codename = '<generator expression>'

	super_init = CodeGenerator.__init__ # call be other init

	__super_init = AbstractFunctionCode.__init__

	def __init__(self, gexp, mod):
		self.scope = gexp.symtab
		self.__super_init (gexp, 1, mod)
		self.graph.setFreeVars (self.scope.get_free_vars())
		self.graph.setCellVars (self.scope.get_cell_vars())
		self.graph.setFlag(CO_GENERATOR)

class AbstractClassCode:

	def __init__(self, klass, module):
		self.module = module
		self.graph = pyassem.PyFlowGraph24 (klass.name, optimized=0, klass=1)
		self.super_init()
		self.graph.setFlag(CO_NEWLOCALS)
		if klass.doc:
			self.setDocstring(klass.doc)

	def get_module(self):
		return self.module

	def finish(self):
		self.graph.startExitBlock()
		self.emit('LOAD_LOCALS')
		self.emit('RETURN_VALUE')

class ClassCodeGenerator(NestedScopeMixin, AbstractClassCode, CodeGenerator):
	super_init = CodeGenerator.__init__

	__super_init = AbstractClassCode.__init__

	def __init__ (self, klass, module):
		self.scope = klass.symtab
		self.__super_init (klass, module)
		self.graph.setFreeVars(self.scope.get_free_vars())
		self.graph.setCellVars(self.scope.get_cell_vars())
		self.emit("LOAD_GLOBAL", "__name__")
		self.storeName("__module__")
		if klass.doc:
			self.emit("LOAD_CONST", klass.doc)
			self.storeName('__doc__')

def generateArgList(arglist):
	# Generate an arg list marking TupleArgs
	args = []
	extra = []
	count = 0
	marg = False
	for i, elt in enumerate (arglist):
		if type(elt) is str:
			args.append(elt)
			if elt [0] == '$':
				marg = True
		elif type(elt) is tuple:
			args.append(TupleArg(i * 2, elt))
			extra.extend(misc.flatten(elt))
			count = count + 1
		else:
			raise ValueError, "unexpect argument type:", elt
	return args + extra, count, marg

#
# op finder (whatever)
#

class OpFinder:
	def init(self):
		self.op = None
	def visitAssName(self, node):
		if not self.op:
			self.op = node.flags
		elif self.op != node.flags:
			raise ValueError, "mixed ops in stmt"
	visitAssAttr = visitAssName
	visitSubscript = visitAssName

OpFinder = OpFinder()

def findOp(node):
	v = OpFinder
	v.init ()
	walk(node, v)
	return v.op

#
# Look for a break in a loop
#

class BreakFinder:
	# Traverse an AST to see if control can branch with a 'Break'.
	# We are also looking for 'Continue' but only inside Try-blocks.
	# The 'simple continue' is implemented with a JUMP and doesn't use
	# the LOOP_BLOCK

	def init (self):
		self.bad_continue = 0

	def visitBreak (self, node):
		raise BreakFinder
	def visitContinue (self, node):
		if self.bad_continue:
			raise BreakFinder

	def visitWhile (self, node):
		if node.else_:
			self.visit (node.else_)
	def visitFor (self, node):
		if node.else_:
			self.visit (node.else_)

	def visitTryExcept (self, node):
		self.bad_continue += 1
		self.visit(node.body)
		self.bad_continue -= 1
		for _, _, body in node.handlers:
			self.visit (body)
		if node.else_:
			self.visit(node.else_)

	def visitTryFinally (self, node):
		self.bad_continue += 1
		self.visit(node.body)
		self.visit(node.final)
		self.bad_continue -= 1

	def visitClass (self, node):
		pass
	visitFunction = visitClass
	visitDiscard = visitClass
	visitAssign = visitClass
	visitAugAssign = visitClass

	def visitIf (self, node):
		for test, suite in node.tests:
			self.visit (suite)
		if node.else_:
			self.visit(node.else_)

BreakFinder = BreakFinder ()

def have_break (node):
	v = BreakFinder
	v.init ()
	try:
		walk (node, v)
		return False
	except:
		return True

#
#

class Delegator:
	# Base class to support delegation for augmented assignment nodes
	#
	# To generator code for augmented assignments, we use the following
	# wrapper classes.  In visitAugAssign, the left-hand expression node
	# is visited twice.  The first time the visit uses the normal method
	# for that node .  The second time the visit uses a different method
	# that generates the appropriate code to perform the assignment.
	# These delegator classes wrap the original AST nodes in order to
	# support the variant visit methods.
	def __init__(self, obj):
		self.obj = obj

	def __getattr__(self, attr):
		return getattr(self.obj, attr)

class AugGetattr(Delegator):
	pass

class AugName(Delegator):
	pass

class AugSlice(Delegator):
	pass

class AugSubscript(Delegator):
	pass

wrapper = {
	ast.Getattr: AugGetattr,
	ast.Name: AugName,
	ast.Slice: AugSlice,
	ast.Subscript: AugSubscript,
}

def wrap_aug(node):
	return wrapper[node.__class__](node)

ast.ast2code = ast2code
