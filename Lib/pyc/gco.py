# Global Compiler Options
#
# Used for recusrively reentrant compilation. 
#

try:
	set
except:
	from sets import Set as set

class GCO:
    def __init__ (self):
	self.CSTACK = []
	self.CURRENT = None
    def new_compiler (self):
	self.CSTACK.append (self.CURRENT)
	self.CURRENT = { 'funcs_with_consts':set(), 'have_with':False }
    def pop_compiler (self):
	self.CURRENT = self.CSTACK.pop ()
    def __getitem__ (self, x):
	return self.CURRENT [x]
    def __setitem__ (self, x, y):
	self.CURRENT [x] = y

GCO = GCO()
