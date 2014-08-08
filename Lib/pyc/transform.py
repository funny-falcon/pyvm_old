#
# AST tranformations
#

import ast
from visitor	import walk
from gco	import GCO
from misc	import opt_progress, counter
from optimizer	import make_copy, ast_Assign, ast_Getattr

class TransformVisitor:

	# convert:  print >> X, text
	# to: __print_to__ (X.write, text, '\n')
	# for pyvm only

	def visitPrint (self, node, nl = 0):
		if not node.dest or not GCO ['pyvm']:
			for child in node.nodes:
				self.visit (child)
			return
		L = [ast.Getattr (node.dest, 'write')] + node.nodes
		if nl:
			L.append (ast.Const ('\n', node.lineno))
		make_copy (node, ast.Discard
			(ast.CallFunc (ast.Name ('__print_to__', node.lineno), L)))
		self.visit (node)

	def visitPrintnl (self, node):
		self.visitPrint (node, 1)

	# convert exec to __exec__()
	# for pyvm only

	def visitExec (self, node):
		self.visit (node.expr)
		if node.globals:
			self.visit (node.globals)
		if node.locals:
			self.visit (node.locals)
		if GCO ['pyvm']:
			make_copy (node, ast.Discard 
			(ast.CallFunc (ast.Name ('__exec__', node.lineno), list (node.getChildNodes ()))))

	# with-statement. Convert:
	#
	#	with EXPR as VAR:
	#		BLOCK
	# to:
	#	abc = (EXPR).__context__ ()
	#	exc = (None, None, None)
	#	VAR = abc.__enter__ ()
	#	try:
	#		try:
	#			BLOCK
	#		except:	exc = sys.exc_info (); raise
	#	finally: abc.__exit__ (*exc)
	#
	# if BLOCK doesn't have return/break/continue, do it as
	#
	#	abc = (EXPR).__context__ ()
	#	VAR = abc.__enter__ ()
	#	try:
	#		BLOCK
	#	except:	abc.__exit__ (*sys.exc_info ()); raise
	#	else: abc.__exit__ (None, None, None)
	#
	withcnt = counter()

	def visitWith (self, node):

		i = self.withcnt ()
		abc, exc = 'WiTh_CoNtExT__%i' %i, 'WiTh_ExC__%i' %i
		lno = node.lineno
		self.visit (node.expr)
		self.visit (node.code)
		rbc = hasRBC (node.code)
		stmts = []
		stmts.append (ast_Assign (abc, ast.CallFunc (ast.Getattr (node.expr, '__context__'), [])))
		if rbc:
			stmts.append (ast_Assign (exc, ast.Const ((None, None, None))))
		enter = ast.CallFunc (ast_Getattr (abc, '__enter__'), [])
		if node.var:
			enter = ast_Assign (node.var, enter)
		else:
			enter = ast.Discard (enter)
		stmts.append (enter)
		if rbc:
			stmts.append (ast.TryFinally (
		ast.TryExcept (
			node.code,
			[(None, None, ast.Stmt ([
				ast_Assign (exc, ast.CallFunc (ast_Getattr ('sys', 'exc_info'), [])),
				ast.Raise (None, None, None, lno)
			]))],
			None, lno
		),
		ast.Discard (ast.CallFunc (ast_Getattr (abc, '__exit__'), [], ast.Name (exc, 0))),
		lno
	    ))
		else:
			stmts.append (ast.TryExcept (
				node.code,
				[(None, None, ast.Stmt ([
					ast.Discard (ast.CallFunc (ast_Getattr (abc, '__exit__'), [],
					ast.CallFunc (ast_Getattr ('sys', 'exc_info'), []))),
					ast.Raise (None, None, None, lno)
				]))],
				ast.Stmt ([
					ast.Discard (ast.CallFunc (ast_Getattr (abc, '__exit__'),
					3 * [ast.Const (None)]))
				])
				, lno
			))
		make_copy (node, ast.Stmt (stmts))

class RBCFinder:
	# Traverse AST and look for return/break/continue that affect the
	# current node

	def __init__ (self):
		self.inloop = 0

	def visitReturn (self, node):
		raise RBCFinder

	def visitBreak (self, node):
		if not self.inloop:
			raise RBCFinder

	visitContinue = visitBreak

	def visitWhile (self, node):
		self.inloop += 1
		self.visit (node.body)
		self.inloop -= 1
		if node.else_:
			self.visit (node.else_)

	visitFor = visitWhile

	def visitClass (self, node):
		pass

	visitFunction = visitClass
	visitDicard = visitClass
	visitAssign = visitClass
	visitAugAssign = visitClass

def hasRBC (node):
	try:
		walk (node, RBCFinder ())
		return False
	except RBCFinder:
		return True

def transform_tree (tree):
	walk(tree, TransformVisitor())
