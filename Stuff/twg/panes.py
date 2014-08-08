import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()
W=GUI.Window ()
W.start_construction ()
W.hsplitter ()
W.vsplitter ()
W.editor ()
W.editor ()
W.editor ()
W.end_construction ()
