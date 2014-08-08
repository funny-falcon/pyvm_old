import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()
if 1:
	 def MAKETREE (self):
	    self.addrow ([['tmp.txt', 'file']])
	    self.addrow ([['home/', 'dir']])
	    self.sub ()
	    if 1:
	     self.addrow ([['johnny.html', 'HTML document']])
	     self.addrow ([['jack/', 'dir']])
	     self.sub ()
	     if 1:
	      self.addrow ([['Mailbox', 'MIME encoded data']])
	     self.unsub ()
	    self.unsub ()
	    self.addrow ([['core', 'data']])

         W=GUI.Window ()
         W.start_construction ()
         W.streebox (colnam=['dirs', 'type'], gcode=MAKETREE)
         W.end_construction ()
         GUI.exec_loop ()

