import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()

if 1:
         # make a listbox with the keys of globals() and a viewer to show their values

         def MAKELIST (self):
             lst = globals ().keys ()
             lst.sort ()
             for i in lst:
                self.addrow ([[i]])

         def SHOWKEY (self):
	     try:
                x = repr (globals ()[self.master.L.row [0][0]])
	     except:
		x = "-NO REPR-"
             self.master.E.set_text (x)

         W=GUI.Window ()
         W.start_construction ()
         W.hsplitter ()
         if 1:
          W.listbox (name='L', colnam=['keys'], gcode=MAKELIST, scode=SHOWKEY, dims=(20,10))
          W.editor (name='E', editable=False, dims = (40, 10))
 	 W.checkbutton (text='adas')
         W.end_construction ()
         GUI.exec_loop ()

