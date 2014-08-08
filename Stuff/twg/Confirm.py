import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()

if 1:
        def DANGERCMD(self):
            D = GUI.Dialog (self)
            D.ok = False
            D.start_construction ()
            D.open_vbox ()
            D.label (text='Are you 100% sure?')
            D.open_hbox ()
            D.button (text='ok', cmd="""self.master.ok=True
print "WILL CLOSE NOW, "
self.master.close()""")
            D.button (text='Cancel', cmd='self.master.close()')
            D.close_box ()
            D.close_box ()
            D.end_construction ()
            if D.ok:
                print "Ok with me"
            else:
                print "Canceled"

        W = GUI.Window ()
        GUI.transplant (DANGERCMD, W)
        W.start_construction ()
        W.button (text='Dangerous action button', cmd=W.DANGERCMD)
        W.end_construction ()
        GUI.exec_loop ()
