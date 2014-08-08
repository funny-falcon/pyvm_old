import sys
if not sys.copyright.startswith ('pyvm'):
   sys.path.append ('/home/stan/toolchain/Lib/')
import twgui
GUI = twgui.init ()

import string
import os

#
# Utility
#
class transplant: 
   def __init__(self, method, host, method_name=None):
      self.host = host
      self.method = method
      setattr(host, method_name or method.__name__, self)
   def __call__(self, *args, **kwargs):
      nargs = [self.host]
      nargs.extend(args)
      return self.method (*nargs, **kwargs)

def readfile (fnm):
    f=open (fnm, 'r')
    txt = f.read()
    f.close ()
    return txt

def writefile (fnm, txt):
    f=open (fnm, 'w')
    f.write (txt)
    f.close ()

def app ():
 def NEWCMD(self):
   self.ED.set_text('')
   self.CURRENT_FILE='NewFile.py'
   self.FILENAME.set_text ('NewFile.py')

 def RELOADCMD(self):
   self.ED.set_text (readfile (self.CURRENT_FILE))

 def LOADCMD (self):
    l = self.openFileDialog (name=self.CURRENT_FILE)
    if l:
        try:
	    self.ED.set_text (readfile (l))
	    self.FILENAME.set_text (l)
	    self.CURRENT_FILE = l
        except IOError:
	    print "No such file"

 def SAVEASCMD (self):
    l = self.saveFileDialog (name=self.CURRENT_FILE)
    if l:
        try:
	    writefile (l, self.ED.get_text ())
	    self.FILENAME.set_text (l)
	    self.CURRENT_FILE = l
        except IOError:
	    print "Failed save"

 def SAVECMD(self):
    D=self.MyGUI.Dialog (self)
    D.ok = False
    D.start_construction ()
    D.open_vbox ()
    D.label (text='Save file '+self.CURRENT_FILE+' ?')
    D.open_hbox ()
    D.button (text='ok', cmd="self.master.ok=True; self.master.close()")
    D.button (text='Cancel', cmd='self.master.close()')
    D.close_box ()
    D.close_box ()
    D.end_construction ()
    if D.ok:
        writefile (self.CURRENT_FILE, self.ED.get_text())

 def RUNCMD (self):
    x = self.LIBRADIO.current
    print 'Running with ['+x+']'
    for i in self.GUIList:
	if i[0] == x:
	    break
    xx=self.ED.get_text ()
    global GUI
    TMP=GUI
    GUI = i[1]
    exec xx in globals (), globals ()
    GUI.exec_loop ()
    GUI=TMP

 def RUN2CMD (self):
    x = self.LIBRADIO.current
    os.system ('./run2.py -'+string.lower (x)+' '+self.CURRENT_FILE + ' &')
    

 W = GUI.Window ()
 W.MyGUI = GUI
 W.CURRENT_FILE = 'Editor2.py'
 W.GUIList = GUIList = [('tk', GUI)]
 transplant (RUNCMD, W)
 transplant (NEWCMD, W)
 transplant (RELOADCMD, W)
 transplant (SAVECMD, W)
 transplant (SAVEASCMD, W)
 transplant (LOADCMD, W)
 W.transplant (RUN2CMD)
 if W.BaseGUI == 'pyqt': fnt = 'terminal'
 elif W.BaseGUI == 'tkinter': fnt = 'courier'
 else: fnt = 'Courier 12'
 W.start_construction ()
 W.settitle ('Editor IDE in '+W.BaseGUI)
 W.open_vbox ()
 if 1:
  W.label (name='FILENAME', text=W.CURRENT_FILE)
  W.open_hbox ()
  if 1:
   W.editor (name='ED', dims=(78,23), font = fnt)
   W.open_vbox ('Run it with')
   if 1:
    W.open_radio (name='LIBRADIO')
    if 1:
     for i in GUIList:
         W.radio (name=i[0], text=i[0], active=(GUI==i[1]))
    W.close_radio ()
    W.button (text="Run it!", cmd=W.RUNCMD)
    W.button (text="Fork 'n' Run file", cmd=W.RUN2CMD)
    if W.BaseGUI == 'tkinter': fn = 'tw-logo.gif'
    else: fn = 'tw-logo.png'
    W.image (name='IMG', filename=fn)
   W.close_box ()
  W.close_box ()
  W.open_hbox ()
  if 1:
   W.button (text='New', cmd=W.NEWCMD)
   W.button (text='Reload', cmd=W.RELOADCMD)
   W.button (text='Load', cmd=W.LOADCMD)
   W.button (text='Save', cmd=W.SAVECMD)
   W.button (text='Save As...', cmd=W.SAVEASCMD)
   W.button (text='Quit', cmd='self.master.quit ()')
  W.close_box ()
 W.close_box ()
 W.ED.set_text (readfile (W.CURRENT_FILE))
 W.end_construction ()


app ()

