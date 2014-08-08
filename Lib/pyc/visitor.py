class ASTVisitor:
	def __init__(self):
		self._cache = {}

	def default(self, node, *args):
		self = self.dispatch
		for child in node.getChildNodes():
			self (child, *args)

	def add_cache (self, node, *args):
		klass = node.__class__
		className = klass.__name__
		meth = self._cache [className] = getattr(self.visitor, 'visit' + className, self.default)
		return meth (node, *args)

	def dispatch(self, node, *args):
		try:
			return self._cache [node.__class__.__name__] (node, *args)
		except KeyError:
			pass
		return self.add_cache (node, *args)

	def preorder(self, tree, visitor):
		"""Do preorder walk of tree using visitor"""
		self.visitor = visitor
		visitor.visit = self.dispatch
		try:
			return self.dispatch(tree)
		finally:
			# free some circular references. Why not?
			del self.visitor
			del visitor.visit
			del self._cache

def walk(tree, visitor):
	return ASTVisitor().preorder(tree, visitor)
