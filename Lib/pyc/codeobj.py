from new import code as BuildCodeObject
from gco import GCO

''' The co_names tuple.
Every code object has such a tuple which keeps the names
of global variables and attributes that are used by the
code object. Of course there is a lot of duplication because
the functions of a module share most of these names.
The "shared names tuple" means that all those names are
stored in ONE big common tuple.

This saves 10-20% on the size of the pyc file.
It is good for freezing pyvm application.

In order to do that we emit the tuple at the *first*
code object of the module whos co_names will be loaded.
For all the other code objects, we marshal None as co_names.
Python does not accept None for co_names and this is
valid only for MAGIC_PYVM files.  '''

''' The co_consts tuple.
There is similar duplication with co_consts. However, the
co_consts of a code object may contain other code objects
to it is not possible to do what we did with the names tuple.
Instead we collect only constants that are not code objects
in the 'global consts tuple'. These constants get an index
number which is their index in the global consts tuple
plus 30000.

In order to be able to find this tuple, we append it as
the last element of the shared co_names tuple.

With this and marshalling None as the co_consts of
code objects whos co_consts would otherwise be the
empty tuple, we save about 8%.
'''

class ConstCollector:
	def __init__ (self):
		self.D = {}
	def add (self, x):
		t = type (x), x
		try:
			return self.D [t]
		except:
			n = len (self.D)
			self.D [t] = n
			return n
	def tolist (self):
		L = [(j, i [1]) for i, j in self.D.iteritems ()]
		L.sort ()
		return [i [1] for i in L]

class CodeObject:
	def __init__ (self, params):
		self.params = params

	def to_real_code (self):
		global StoredGnt

		for c in self.params [5]:
			if isinstance (c, CodeObject):
				break
		else:	# leaf
			if not StoredGnt:
				StoredGnt = True
				params = list (self.params)
				params [6] = tuple (GCO ['global_names_list'])
				#print "ShNT:", len (params [6])
				self.params = tuple (params)
			return BuildCodeObject (*self.params)

		params = list (self.params)
		consts = list (params [5])
		for i, c in enumerate (consts):
			if isinstance (c, CodeObject):
				consts [i] = c.to_real_code ()
		params [5] = tuple (consts)

		return BuildCodeObject (*params)

	def __repr__ (self):
		return "<temporary code object>"

def RealCode (c):
	global StoredGnt
	StoredGnt = not GCO ['gnt']
	if GCO ['gnc']:
		g = GCO ['global_consts_list'].tolist ()
		GCO ['global_names_list'].append (tuple (g))
	return c.to_real_code ()
