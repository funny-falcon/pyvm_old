#
# Twilight GUI wrapper for PyQT
#
# Copyright (C) 2004, Stelios Xanthakis
#

import qt

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
      return apply(self.method, nargs, kwargs)

class ___disable___:
    def disable (self):
	self.this.setEnabled (False)
    def enable (self):
	self.this.setEnabled (True)

def functype(): pass

class ___vexec___:
    def vexec (self, code):
	if not code: return
	if type (code) == type (''):
	    exec code
	elif type (code) == type (functype):
	    code (self)
	else: code ()

class ___implant___:
    def implant (self, fname, func):
	if type (func) == type (functype):
	    name = func.__name__
	    transplant (func, self, name)
	    exec 'self.'+fname+'=self.'+name
	else:
	    exec 'self.'+fname+'= func'

#
# label
#
class ___qtlabel___(___disable___):
    def __init__ (self, master, text):
        self.this = qt.QLabel (text, master.group[-1][0])
        self.this.setText (text)
        self.master = master
    # available to code
    def get_text (self):
        return self.this.text ()
    def set_text (self, text):
        self.this.setText (text)

#
# Buttons
#

class ___qtbutton___(___disable___, ___vexec___):
    class QQPushButton (qt.QPushButton):
	def __init__ (self, mastah, *args):
	    qt.QPushButton.__init__ (self, *args)
	    self.mastah = mastah	# circular reference. may garbage collectors be w/ us
	def contextMenuEvent (self, cmev):
	    self.mastah.dorclick ()
    def __init__ (self, master, text, cmd, rclick):
        #self.this = qt.QPushButton (master.group [-1][0])
        self.this = ___qtbutton___.QQPushButton (self, master.group [-1][0])
        self.this.setText (text)
        self.master = master
        self.code = cmd
	self.rclick = rclick
        master.win.connect (self.this, qt.SIGNAL("clicked()"), self.dostuff)
    def dostuff (self, *args):
        self.vexec (self.code)
    def dorclick (self):
	self.vexec (self.rclick)

class ___qttogglebutton___(___disable___, ___vexec___):
    def __init__ (self, master, text, cmda, cmdd, active):
	self.this = qt.QPushButton (master.group [-1][0])
	self.this.setToggleButton (True)
	self.this.setText (text)
	self.master = master
	self.cmdact = cmda
	self.cmddeact = cmdd
	self.this.setOn (active)
	master.win.connect (self.this, qt.SIGNAL("clicked()"), self.dostuff)
    def dostuff (self, *args):
	if self.this.isOn ():
	    self.vexec (self.cmdact)
	else:
	    self.vexec (self.cmddeact)
    # macrocode
    def toggle (self):
	self.this.setOn (not self.isOn()) 
	self.dostuff ()
    def isOn (self):
	return self.this.isOn ()

class ___qtcheckbutton___(___disable___, ___vexec___):
    def __init__ (self, master, text, cmd, active):
        self.this = qt.QCheckBox (text, master.group [-1][0])
        self.master = master
        self.code = cmd
        self.active = active
        if (active):
            self.this.setChecked (1)
        master.win.connect (self.this, qt.SIGNAL ("toggled(bool)"), self.dostuff)
    def dostuff (self, *args):
        self.active = not self.active
        self.vexec (self.code)
    # Available to macro
    def activate (self, value):
        self.this.setChecked (value)

class ___qttransistor___ (___vexec___):
    def __init__ (self, cmd):
	self.cmd = cmd
	self.current = None
	self.rn = {}
    def transist (self, radio):
	self.current = radio
	if self.cmd:
	    self.vexec (self.cmd)
    def addradio (self, name, w, active=False):
	self.rn [name] = w
	if active:
	    self.current = name
    # To macro code
    def activate (self, name):
	self.rn [name].activate ()
    def disable (self, name):
	self.rn [name].disable ()
    def enable (self, name):
	self.rn [name].enable ()

class ___qtradiobutton___(___disable___):
    def __init__ (self, master, name, text, tr, active):
        self.this = qt.QRadioButton (text, master.group [-1][0])
        self.master = master
        self.active = active
	self.name = name
	self.transistor = tr
	tr.addradio (name, self, active)
        if (active):
            self.this.setChecked (1)
        master.win.connect (self.this, qt.SIGNAL ("toggled(bool)"), self.dostuff)
    def dostuff (self, *args):
        self.active = not self.active
        if self.active:
	    self.transistor.transist (self.name)
    # Available to macro
    def activate (self):
        self.this.setChecked (1)

#
# image
#

class ___qtimage___:
    def __init__ (self, master, imag):
	self.img = qt.QPixmap (imag)
	self.this = qt.QLabel (master.group [-1][0])
	self.this.setPixmap (self.img)
	self.this.setFixedSize (self.img.size ())
	self.this.show ()
    def load (self, imag):
	# this doesn't work. WhyTheFuck?
	self.img = qt.QPixmap (imag)
	self.this.setPixmap (self.img)
	self.this.setFixedSize (self.img.size ())
	self.this.show ()

#
# text entering
#

class ___qtentry___(___disable___, ___vexec___):
    def __init__ (self, master, text, length, cmd):
        self.this = qt.QLineEdit (master.group [-1][0])
	if length > 0:
	    fm = self.this.fontMetrics ()
	    self.this.setMinimumWidth (length * fm.width ('X'))

        if text != '':
            text = self.this.setText (text)
        self.master = master
        self.code = cmd
        master.win.connect (self.this, qt.SIGNAL ("returnPressed()"), self.dostuff)
    def dostuff (self):
        self.vexec (self.code)
    # Public functions accessible from self.code
    def text (self):
        return self.this.text ()
    def set_text (self, text):
        self.this.setText (text)

class ___qttext___(___disable___):
    def __init__ (self, master, dims, font, ww, wp, editable):
	self.this = qt.QMultiLineEdit (master.group [-1][0])
	self.master = master
	self.this.setWordWrap (ww)
	self.this.setWrapPolicy (wp)
	if font:
	    self.this.setFont (qt.QFont (font))
	if dims != (0,0):
	    fm = self.this.fontMetrics ()
	    if dims [0] != 0:
		self.this.setMinimumWidth (dims [0] * fm.width ('X'))
	    if dims [1] != 0:
		self.this.setMinimumHeight (dims [1] * fm.height())
	self.set_editable (editable)
    # available to code
    def get_text (self):
        return str (self.this.text ())
    def set_text (self, text):
        self.this.setText (text)
    def set_editable (self, setting):
        self.this.setReadOnly (not setting)

#
# List and Tree
#

class ___qtlistbase___(___disable___, ___vexec___, ___implant___):
    class ___qrrclist___ (qt.QListView):
	def __init__ (self, *args):
	    qt.QListView.__init__ (self, *args)
	    self.rclicked = False
	def contextMenuEvent (self, c):
	    self.rclicked = True
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	self.master = master
	self.this = ___qtlist___.___qrrclist___ (master.group [-1][0])
	self.root = [self.this]
	for i in colnam:
	    self.this.addColumn (i)
	self.keyn = len (colnam)
	self.this.setAllColumnsShowFocus (True)
	self.implant ('gcode', gcode)
	self.ecode = ecode
	self.scode = scode
	self.rclick = rclick
	if dims != (0,0):
	    fm = self.this.fontMetrics()
	    if dims [0] != 0:
		self.this.setMinimumWidth (dims [0] * fm.width ('g'))
	    if dims [1] != 0:
		self.this.setMinimumHeight (dims [1] * fm.height ())
	master.win.connect (self.this, qt.SIGNAL ("clicked (QListViewItem*)"), self.dostuff1)
	master.win.connect (self.this, qt.SIGNAL ("doubleClicked (QListViewItem*)"), self.dostuff2)
	master.win.connect (self.this, qt.SIGNAL ("returnPressed (QListViewItem*)"), self.dostuff2)
	self.reload ()
    def dostuff1 (self, item):
	if not item:
	    self.row = None
	    return
	self.row = self.zdict [str (item.text (self.keyn))]
	if self.this.rclicked:
	    self.this.rclicked = False
	    self.vexec (self.rclick)
	if self.scode:
	    self.vexec (self.scode)
    def dostuff2 (self, item):
	if not item:
	    self.row = None
	    return
	self.row = self.zdict [str (item.text (self.keyn))]
	self.vexec (self.ecode)
    # macros
    def reload (self, code = None):
	if code: self.gcode = code
	self.this.clear ()
	self.cntr = 0
	self.zdict = {}
	self.vexec (self.gcode)

class ___qtlist___ (___qtlistbase___):
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	___qtlistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
	self.this.setRootIsDecorated (False)
   # to macros
    def sub (self):
	pass
    def unsub (self):
	pass
    def addrow (self, data):
	t = data [0]
	i = qt.QListViewItem (self.this)
	for j in range (len (t)):
	    i.setText (j, t [j])
	key = str (self.cntr)
	self.cntr += 1
	i.setText (j+1, key)   # hidden
	self.zdict [key] = data

class ___qtstree___ (___qtlistbase___):
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	___qtlistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
	self.this.setRootIsDecorated (True)
    # to macros
    def sub (self):
	self.root.append (self.last)
    def unsub (self):
	self.root.pop ()
    def addrow (self, data):
	t = data [0]
	i = qt.QListViewItem (self.root [-1])
	self.last = i
	for j in range (len (t)):
	    i.setText (j, t [j])
	key = str (self.cntr)
	self.cntr += 1
	i.setText (j+1, key)   # hidden
	self.zdict [key] = data

class ___qttree___ (___qtlistbase___):
    class ritem (qt.QListViewItem):
	def __init__ (self, parent, listclass, excode):
	    qt.QListViewItem.__init__ (self, parent)
	    self.setExpandable (True)
	    self.listclass = listclass
	    self.excode = excode
	def setOpen (self, o):
	    if o:
		self.st = self.listclass.cntr
	        self.listclass.expander (self, self.excode)
		self.en = self.listclass.cntr
	    else:
                while self.childCount ():
                    f = self.firstChild ()
                    self.takeItem (f)
                    del f
		i = self.st
		while i < self.en:
		    del self.listclass.zdict [str (i)]
		    i += 1
	    qt.QListViewItem.setOpen (self, o)
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	___qtlistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
	self.this.setRootIsDecorated (True)
    def expander (self, item, code):
	self.last = item
	self.row = self.zdict [str (item.text (self.keyn))]
	self.root.append (self.last)
	self.vexec (code)
	self.root.pop ()
    # to macros
    def sub (self):
	pass
    def unsub (self):
	pass
    def addrow (self, data, expand=None):
	t = data [0]
	if expand:
	    i = ___qttree___.ritem (self.root [-1], self, expand)
	else:
	    i = qt.QListViewItem (self.root [-1])
	self.last = i
	for j in range (len (t)):
	    i.setText (j, t [j])
	key = str (self.cntr)
	self.cntr += 1
	i.setText (j+1, key)   # hidden
	self.zdict [key] = data

#
# The popup menu
#

class ___qtpopup___ (___vexec___, ___implant___):
    def __init__(self, master, code, *args, **kw):
	for i in kw.keys ():
	    setattr (self, i, kw [i])
        self.master = master
        self.menu = qt.QPopupMenu (master.win)
        self.istack = []
        self.mstack = [ self.menu ]
        self.cnt = 0
        self.codes = {}
	self.implant ('code', code)
        self.vexec (self.code)
        del self.mstack
        self.menu.exec_loop (qt.QCursor.pos ())
    # to macrocode
    def item (self, name, code):
        self.codes [self.cnt] = code
        exec 'def ooo (self, x): self.vexec (self.codes ['+str(self.cnt)+'])'
        nm = 'ooo' + str (self.cnt)
        self.cnt += 1
        transplant (ooo, self, nm)
        self.mstack [-1].insertItem (name, self.__dict__[nm])
    def sub (self, name):
        self.mstack.append (qt.QPopupMenu (self.master.win))
        self.istack.append (name)
    def unsub (self):
        m = self.mstack.pop ()
        self.mstack [-1].insertItem (self.istack.pop(), m)
    def sep (self):
        self.mstack [-1].insertSeparator ()

#
# Workspaces
#

class ___qttabdialog___(___disable___):
    wstype = 'tab'
    def __init__ (self, master):
	self.this = qt.QTabWidget (master.group [-1][0])
	self.master = master
    def addon (self, tab):
	self.this.addTab (tab.this, tab.title)
	self.this.show ()
	tab.this.show ()

class ___qtmdiworkspace___(___disable___):
    wstype = 'MDI'
    def __init__ (self, master):
	self.this = qt.QWorkspace (master.group [-1][0])
	self.master = master
    def addon (self, tab):
	self.this.addTab (tab.this, tab.title)
	self.this.show ()

#
# main sheet class
#

class ___qtsheet___(___disable___):
    def transplant (self, method, method_name=None):
	transplant (method, self, method_name)
    # Private 
    def addwidget (self, b, name):
	if not name:
	    name = 'NYPD' + str (self.icnt)
	    self.icnt += 1
	setattr (self, name, b)
	if self.group [-1][1] != -1:
	    if self.group [-1][1] == 1: self.group [-1][1] -= 1
	    else: self.close_splitter ()
    def popup (self, code, *args, **kw):
	___qtpopup___ (self, code,  *args, **kw)
    def openFileDialog (self, name=''):
	xx = str (qt.QFileDialog.getOpenFileName (name, qt.QString.null, self.win))
	if xx == '': return None
	return xx
    def saveFileDialog (self, name=''):
	xx = str (qt.QFileDialog.getSaveFileName (name, qt.QString.null, self.win))
	if xx == '': return None
	return xx
    def close_splitter (self):
	self.group.pop ()
	self.addwidget (None, None)
    def start_construction (self):
	self.icnt = 0
        self.group = [ [self.win,-1] ]
	self.mode = []
	self.transistors = []
	self.open_vbox ()
    def end_construction (self):
	self.this = self.group [-1][0]
	self.close_box ()
    # Protected
    BaseGUI='pyqt'
    def __init__ (self):
	pass
    def button (self, name=None, text='button', cmd='0', rclick=None):
        b = ___qtbutton___ (self, text, cmd, rclick)
        self.addwidget (b, name)
	return b
    def checkbutton (self, name=None, text='check', cmd='', active=False):
        b = ___qtcheckbutton___ (self, text, cmd, active)
        self.addwidget (b, name)
	return b
    def tbutton (self, name=None, text='toggler bobbler', cmdact='', cmddeact='', active=False):
        b = ___qttogglebutton___ (self, text, cmdact, cmddeact, active)
        self.addwidget (b, name)
	return b
    def textentry (self, name=None, text='', length=0, cmd='', label=None):
        if label != None:
            self.open_hbox ()
            self.label (text=label)
            b = self.textentry (name, text, length, cmd)
            self.close_box ()
	    self.addwidget (None, None)
        else:
            b = ___qtentry___ (self, text, length, cmd)
            self.addwidget (b, name)
	return b
    def label (self, name=None, text='label'):
        b = ___qtlabel___ (self, text)
        self.addwidget (b, name)
	return b
    def radio (self, name=None, text='radio', active=False):
	if not name: name=text
        return ___qtradiobutton___ (self, name, text, self.transistors [-1], active)
    def editor (self, name=None, font=None, dims = (0,0), wrap=0, editable=True):
        wrp=[qt.QMultiLineEdit.NoWrap,qt.QMultiLineEdit.WidgetWidth,qt.QMultiLineEdit.WidgetWidth]
        wrp2=[qt.QMultiLineEdit.Anywhere,qt.QMultiLineEdit.Anywhere,qt.QMultiLineEdit.AtWhiteSpace]
        b = ___qttext___ (self, dims, font, wrp [wrap], wrp2 [wrap], editable)
        self.addwidget (b, name)
	return b
    def listbox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(0, 0), rclick=None):
        b = ___qtlist___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def treebox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(0, 0), rclick=None):
        b = ___qttree___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def streebox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(0, 0), rclick=None):
        b = ___qtstree___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def image (self, name=None, filename=None):
	b = ___qtimage___ (self, filename)
	self.addwidget (b, name)
	return b
    def separator (self):
	s = qt.QFrame(self.group [-1][0])
	if self.mode [-1] == 'v':
	    s.setFrameStyle(qt.QFrame.HLine | qt.QFrame.Sunken)
	    s.setFixedHeight(s.sizeHint().height())
	else:
	    s.setFrameStyle(qt.QFrame.VLine | qt.QFrame.Sunken)
	    s.setFixedWidth(s.sizeHint().width())
	self.addwidget (None, None)
    def hsplitter (self):
	self.group.append ([qt.QSplitter (qt.Qt.Horizontal, self.group [-1][0]),1])
    def vsplitter (self):
	self.group.append ([qt.QSplitter (qt.Qt.Vertical, self.group [-1][0]),1])
    def open_hbox (self, text=None): 
	if text:
	    hb = qt.QGroupBox (1, qt.QGroupBox.Vertical, text, self.group [-1][0])
	else:
	    hb = qt.QHBox (self.group[-1][0])
	self.group.append ([hb,-1])
	self.mode.append ('h')
    def open_vbox (self, text=None): 
	if text:
	    hb = qt.QGroupBox (1, qt.QGroupBox.Horizontal, text, self.group [-1][0])
	else:
	    hb = qt.QVBox (self.group [-1][0])
	self.group.append ([hb,-1])
	self.mode.append ('v')
    def close_box (self):
	self.group.pop ()
	self.mode.pop ()
	self.addwidget (None, None)
    def open_radio (self, cmd=None, title=None, name=None):
	self.group.append ([qt.QButtonGroup (1, qt.QGroupBox.Horizontal, title, self.group [-1][0]),-1])
	self.mode.append ('v')
	self.transistors.append (___qttransistor___ (cmd))
	if name:
	    setattr (self, name, self.transistors [-1])
    def close_radio (self):
	self.transistors.pop ()
	self.group.pop ()
	self.mode.pop ()
	self.addwidget (None, None)
    def tabworkspace (self, name=None):
	b = ___qttabdialog___ (self)
	self.addwidget (b, name)
	return b
    def MDIworkspace (self, name=None):
	b = ___qtmdiworkspace___ (self)
	self.addwidget (b, name)
	return b

#
# Ancenstry
#

class Window (___qtsheet___):
    def start_construction (self):
        self.win = qt.QMainWindow ()
	___qtsheet___.start_construction (self)
    def end_construction (self):
	___qtsheet___.end_construction (self)
	self.win.setCentralWidget (self.this)
	if not main_running:
	    QAP.setMainWidget (self.win)
	self.win.show ()
    # Protected
    def __init__ (self, code=None):
        self.code = code
        if code:
	   self.start_construction ()
           exec code
	   self.end_construction ()
    def settitle (self, title):
	self.win.setCaption (title)
    def quit (self):
	self.win.close ()

class Sheet (___qtsheet___):
    def start_construction (self):
 	if self.workspace.wstype == 'tab':
	    self.title = ''
	else:
	    self.win = qt.QMainWindow (self.workspace.this, "", qt.Qt.WDestructiveClose)
	___qtsheet___.start_construction (self)
    def end_construction (self):
	___qtsheet___.end_construction (self)
 	if self.workspace.wstype == 'tab':
	    self.workspace.addon (self)
	else:
	    self.win.setCentralWidget (self.this)
	    self.win.show ()
    def __init__ (self, workspace, code=None):
	self.workspace = workspace
	self.win = self.workspace.this
        self.code = code
        if code:
	   self.start_construction ()
           exec code
	   self.end_construction ()
    def settitle (self, title):
	if self.workspace.wstype == 'tab':
	    self.title = title
	else:
	    self.win.setCaption (title)


class Dialog (___qtsheet___):
    def start_construction (self):
	self.win = qt.QDialog (self.master.win)
	self.win.setModal (1)
	___qtsheet___.start_construction (self)
    def end_construction (self):
	___qtsheet___.end_construction (self)
	l = qt.QHBoxLayout (self.win)
	l.addWidget (self.this)
	self.win.show ()
	self.win.exec_loop ()
   # Protected
    def __init__ (self, master, code=None):
	self.master = master
        self.code = code
        if code:
	   self.start_construction ()
           exec code
	   self.end_construction ()
    def settitle (self, title):
  	self.win.setCaption (title)
    def close (self):
	self.win.done (1)

main_running = False

def exec_loop ():
    global main_running
    if not main_running:
	main_running = True
	QAP.exec_loop ()
	main_running = False

def terminate ():
    global main_running
    main_running = False

QAP = qt.QApplication ([])
