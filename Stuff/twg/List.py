import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init (('gtk',))
class transplant: 
   def __init__(self, method, host, method_name=None):
      self.host = host
      self.method = method
      setattr(host, method_name or method.__name__, self)
   def __call__(self, *args, **kwargs):
      nargs = [self.host]
      nargs.extend(args)
      return self.method (*nargs, **kwargs)

def MKLIST (self):
    for k, v in globals ().iteritems ():
	self.addrow ([[k, str (type (v))]])
#    for i in globals ():
#	self.addrow ([[i, str(eval('type('+i+')'))]])

def PCODE (self):
    self.item ('print it', 'print self.data')

def POP (self):
    self.popup (PCODE, data=self.L.row)

W=GUI.Window ()
transplant (POP, W)
W.start_construction ()
W.listbox (name='L', gcode=MKLIST, colnam=['globals', 'type'], rclick=W.POP, ecode=W.POP)
W.end_construction ()
GUI.exec_loop ()
