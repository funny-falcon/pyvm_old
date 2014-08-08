import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()

class transplant: 
   def __init__(self, method, host, method_name=None):
      self.host = host
      self.method = method
      setattr(host, method_name or method.__name__, self)
   def __call__(self, *args, **kwargs):
      nargs = [self.host]
      nargs.extend(args)
      return self.method (*nargs, **kwargs)

if 1:
        import os
        import os.path

        def CODA (self):
         self = self.L
         # the hidden data is the full pathname
         basedir = self.row [1]
         dirs=os.listdir (basedir)
         dirs.sort ()
         for i in dirs:
             fullname = basedir + '/' + i
             if os.path.isdir (fullname): 
                self.addrow (((i,),fullname),self.master.CODA)
             else:
                self.addrow (((i,),))

        CODE="self.addrow ((('/',),'/'), self.master.CODA)"

        W = GUI.Window ()
        transplant (CODA, W)
        W.start_construction ()
        W.treebox (name='L', colnam = ['dir'], gcode = CODE, dims=(20,10))
        W.end_construction ()
        GUI.exec_loop ()
