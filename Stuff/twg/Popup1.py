import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()

if 1:
        def FILEMENU (self):
            self.item ('New', 'print "New"')
            self.item ('Open', 'print "Open"')
            self.sep ()
            self.sub ('Send to')
            if 1:
             self.item ('Floppy disk', 'print "Floppy"')
            self.unsub ()
            self.sep ()
            self.item ('Exit', 'self.master.quit ()')

        def POPUPCODE (self):
            self.popup (FILEMENU)

        W = GUI.Window ()
        GUI.transplant (POPUPCODE, W)
        W.start_construction ()
        W.open_vbox ()
        W.open_hbox ()
        W.button (text='File', cmd=W.POPUPCODE)
        W.close_box ()
        W.separator ()
        W.editor (dims = (80,25))
        W.close_box ()
        W.end_construction ()
        GUI.exec_loop ()
        
