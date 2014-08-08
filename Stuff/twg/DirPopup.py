import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()



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
                self.addrow (((i,),fullname))

        def FILEMENU (self):
	    self.item ('Print fullname', 'print "Fullname:", self.fullname')
            print self.fullname

        def POPUPCODE (self):
            self.popup (FILEMENU, fullname=self.L.row [1])

        CODE="self.addrow ((('/',),'/'), self.master.CODA)"

        W = GUI.Window ()
        W.transplant (CODA)
        W.transplant (POPUPCODE)
        W.start_construction ()
        W.treebox (name='L', colnam = ['dir'], gcode = CODE, dims=(20,10), rclick=W.POPUPCODE)
        W.end_construction ()
        GUI.exec_loop ()
