
import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()
cnt = 0

NT="""
self.settitle ('A page')
self.button (text='butto', cmd='self.master.RR.disable ("On")')
self.button (name='B', text='boggler', cmd='self.master.disable()')
self.editor (name='E',dims=(30,10))
self.open_radio (name='RR')
self.radio ('This', "This")
self.radio ('On', "Ons", active=1)
self.close_radio ()
self.E.set_text (self.workspace.master.NT)
"""

def NEWSHEET (self):
    GUI.Sheet (self.WS, NT)
    return
    global cnt
    S=GUI.Sheet (self.WS)
    S.start_construction ()
    S.settitle ('Page no:' + str (cnt))
    cnt += 1
    S.open_vbox ()
    S.textentry (label='To:', length=60)
    S.editor (dims = (60,20))
    S.close_box ()
    S.end_construction ()

W = GUI.Window ()
W.NT=NT
GUI.transplant (NEWSHEET, W)
W.start_construction ()
W.button (text='Make new sheet', cmd=W.NEWSHEET)
W.MDIworkspace (name='WS')
GUI.Sheet (W.WS, NT)
W.NEWSHEET ()
W.end_construction ()
GUI.exec_loop ()

