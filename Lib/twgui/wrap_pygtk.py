#
# Twilight GUI wrapper for PyGTK
#
# Copyright (C) 2004, Stelios Xanthakis
#

import gtk
import gobject

#
# Utils
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

class ___disablable___:
    def disable (self):
	self.this.set_sensitive (False)
    def enable (self):
	self.this.set_sensitive (True)

def functype(): pass

def my_exec (source, d1=None, d2=None):
    eval (compile (source, 'exec', 'exec'), d1, d2)

class ___implant___:
    def implant (self, fname, func):
	if type (func) == type (functype):
	    name = func.__name__
	    transplant (func, self, name)
	    setattr (self, fname, getattr (self, name))
##	    exec 'self.'+fname+'=self.'+name
	else:
	    setattr (self, fname, func)
##	    exec 'self.'+fname+'= func'

class ___vexec___:
    def vexec (self, code):
	if code:
	    if type (code) == type (''):
	        my_exec (code, globals(), locals())
	    elif type (code) == type (functype):
		code (self)
	    else: code ()

#
# label
#

class ___gtklabel___(___disablable___):
    def __init__ (self, master, text):
        self.this = gtk.Label (text)
        self.master = master
    # available to code
    def get_text (self):
        return self.this.get_text ()
    def set_text (self, text):
        self.this.set_text (text)

#
# buttons
#

class ___gtkbutton___(___disablable___, ___vexec___):
    def __init__ (self, master, text, cmd, rcmd):
        self.this = gtk.Button (text)
        self.master = master
        self.code = cmd
	self.rcode = rcmd
##        self.this.connect ("clicked", self.dostuff)
        self.this.connect ("button-press-event", self.dostuff2)
    def dostuff (self, *args):
	self.vexec (self.code)
    def dostuff2 (self, widget, event):
	if event.button == 3:
	    self.vexec (self.rcode)
	else:
	    self.dostuff ()

class ___gtkcheckbutton___ (___disablable___, ___vexec___):
    def __init__ (self, master, text, cmd, active):
	self.this = gtk.CheckButton (text)
	self.master = master
	self.code = cmd
	self.active = active
	if (active):
	   self.this.set_active (1)
	self.this.connect ("toggled", self.dostuff)
    def dostuff (self, *args):
	self.active = not self.active
	self.vexec (self.code)
    # macrocode
    def activate (self, value):
	self.this.set_active (value)

class ___gtktogglebutton___(___disablable___, ___vexec___):
    def __init__ (self, master, text, cmda, cmdd, active):
        self.this = gtk.ToggleButton (text)
        self.master = master
        self.cmdact = cmda
        self.cmddeact = cmdd
        if (active):
            self.this.set_active (1)
        self.this.connect ("toggled", self.dostuff)
    def dostuff (self, *args):
	if self.this.get_active ():
	    self.vexec (self.cmdact)
	else:
	    self.vexec (self.cmddeact)
    # macrocode
    def toggle (self):
        self.this.set_active (not self.isOn ())
    def isOn (self):
	return self.this.get_active ()

class ___gtktransistor___ (___vexec___):
    def __init__ (self, cmd):
	self.cmd = cmd
	self.current = None
	self.rn = {}
    def transist (self, radio):
	self.current = radio
	self.vexec (self.cmd)
    def addradio (self, name, widget, active=False):
	self.rn [name] = widget
	if active:
	    self.current = name
    def activate (self, name):
	self.rn [name].activate ()
    def disable (self, name):
	self.rn [name].disable ()
    def enable (self, name):
	self.rn [name].enable ()

class ___gtkradiobutton___(___disablable___):
    def __init__ (self, master, group, name, text, tr, active):
        self.this = gtk.RadioButton (group, text)
        self.master = master
        self.transistor = tr
	self.name = name
        if group == None:
            active = True
        self.active = active
	tr.addradio (name, self, active)
        if active:
            self.this.set_active (1)
        self.this.connect ("toggled", self.dostuff)
    def dostuff (self, *args):
        self.active = not self.active
        if self.active:
            self.transistor.transist (self.name)
    # macrocode
    def activate (self):
        self.this.set_active (1)

#
# image
#

class ___gtkimage___:
    def __init__ (self, image):
	self.this = gtk.Image ()
	if image:
	    self.this.set_from_file (image)
    def load (self, image):
	self.this.set_from_file (image)

#
# text entries
#

class ___gtkentry___(___disablable___, ___vexec___):
    def __init__ (self, master, text, length, cmd):
        self.this = gtk.Entry ()
	if length > 0:
	    pl = self.this.create_pango_layout ('X').get_pixel_extents ()
	    self.this.set_size_request (pl[1][2] * length, -1)
        if text != '':
            text = self.set_text (text)
        self.master = master
        self.code = cmd
        self.this.connect ("key-press-event", self.dostuff)
    def dostuff (self, widget, event):
        if event.keyval == 65293:
            self.vexec (self.code)
    # Public functions accessible from self.code
    def text (self):
        return self.this.get_text ()
    def set_text (self, text):
        self.this.set_text (text)

class ___gtktext___(___disablable___):
    def __init__ (self, master, mode, dims, font, editable):
	self.this = gtk.ScrolledWindow ()
	self.this.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	self.txtw = gtk.TextView ()
	self.this.add (self.txtw)
	self.master = master
	self.txtw.set_wrap_mode (mode)
	if font:
	    self.tag = gtk.TextTag ()
	    self.tag.set_property ('font', font)
	    bf = self.txtw.get_buffer ()
	    bf.get_tag_table ().add (self.tag)
	    print "IT'sa:", bf.get_start_iter (), type (bf.get_start_iter ())
	    bf.apply_tag (self.tag, bf.get_start_iter (), bf.get_end_iter ())
	else:
	    self.tag = None
	if dims != (0,0): pl = self.txtw.create_pango_layout ('g').get_pixel_extents ()
	if dims [0] == 0: gx = -1
	else: gx = pl [1][2] * dims [0]
	if dims [1] == 0: gy = -1
	else: gy = (pl[1][3]+self.txtw.get_pixels_above_lines()+self.txtw.get_pixels_below_lines())*dims [1]
	self.this.set_size_request (gx, gy)
	self.set_editable (editable)
    # available to code
    def get_text (self):
        bf = self.txtw.get_buffer ()
        return bf.get_text (bf.get_iter_at_offset (0), bf.get_iter_at_offset (bf.get_char_count ()))
    def set_text (self, text):
        bf = self.txtw.get_buffer ()
        bf.set_text (text)
        if self.tag:
            bf.apply_tag (self.tag, bf.get_start_iter (), bf.get_end_iter ())
    def set_editable (self, setting):
        self.txtw.set_editable (setting)

#
# Lists and trees
#

class ___gtklistbase___(___disablable___, ___vexec___, ___implant___):
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	self.master = master
	self.this = gtk.ScrolledWindow ()
	self.this.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	self.mk_store (colnam)
	self.L=gtk.TreeView (self.model)
	pl = self.L.create_pango_layout ('g').get_pixel_extents ()
	if dims [0] == 0: gx = -1
	else: gx = pl [1][2]*dims [0]
	if dims [1] == 0: gy = -1
	else: gy = (pl [1][3] + 4) * dims [1]
	self.this.set_size_request (gx, gy)
	self.this.add (self.L)
	self.ncol = len (colnam)
	for x in range (len (colnam)):
	    column = gtk.TreeViewColumn (colnam [x], gtk.CellRendererText(), text=x)
	    self.L.append_column (column)
	self.L.connect ('row-activated', self.dclicked)
	self.L.connect ('cursor-changed', self.doselected)
	self.L.connect ('button-press-event', self.dorclick)
	self.implant ('gcode', gcode)
	self.scode = scode
	self.ecode = ecode
	self.rclick = rclick
	self.reload ()
    def rowdata (self, row):
	self.row = row
    def dorclick (self, widget, event):
	if event.button == 3:
	    path = widget.get_path_at_pos (int (event.x), int (event.y))[0]
            iter = self.model.get_iter (path)
	    self.rowdata (self.model.get_value (iter, self.ncol).get_data (''))
	    self.vexec (self.rclick)
    def dclicked (self, treeview, row, column):
        self.rowdata (self.model [row [0]][-1].get_data (''))
        self.vexec (self.ecode)
    def doselected (self, *args):
        selection = self.L.get_selection ()
        selection = selection.get_selected ()
        if not selection:
            self.row = None
            return
        iter = selection [1]
        self.rowdata (self.model.get_value (iter, self.ncol).get_data (''))
        if not self.scode:
            return
        self.vexec (self.scode)
    # to macros
    def reload (self, code=None):
	if code: self.gcode = code
        self.L.set_model (None)
        self.model.clear ()
        self.vexec (self.gcode)
        self.L.set_model (self.model)

class ___gtklist___ (___gtklistbase___):
    def mk_store (self, colnam):
	exec 'self.model=gtk.ListStore ('+len(colnam)*'gobject.TYPE_STRING,'+'gobject.TYPE_OBJECT)'
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	___gtklistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
    def sub (self):
	pass
    def unsub (self):
	pass
    def addrow (self, data):
	iter = self.model.append ()
	for i in range (len (data [0])):
	    self.model.set_value (iter, i, data [0][i])
	O = gobject.GObject()
	O.set_data ('', data)
	self.model.set_value (iter, i+1, O)

class ___gtkstree___ (___gtklistbase___):
    def mk_store (self, colnam):
	exec 'self.model=gtk.TreeStore ('+len(colnam)*'gobject.TYPE_STRING,'+'gobject.TYPE_OBJECT)'
	self.root = [None]
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	___gtklistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
    def sub (self):
	self.root.append (self.last)
    def unsub (self):
	self.root.pop ()
    def addrow (self, data):
	iter = self.model.append (self.root [-1])
	self.last = iter
	for i in range (len (data [0])):
	    self.model.set_value (iter, i, data [0][i])
	O = gobject.GObject()
	O.set_data ('', data)
	self.model.set_value (iter, i+1, O)

class ___gtktree___ (___gtklistbase___):
    def mk_store (self, colnam):
	exec 'self.model=gtk.TreeStore ('+len(colnam)*'gobject.TYPE_STRING,'+'gobject.TYPE_OBJECT)'
	self.root = [None]
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	___gtklistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
	self.L.connect ('test-expand-row', self.expandor)
	self.L.connect ('test-collapse-row', self.collapsor)
    def rowdata (self, row):
	self.row = row[0]
    def expandor (self, x, iter, z):
	self.row, expd = self.model.get_value (iter, self.ncol).get_data ('')
	ch = self.model.iter_children (iter)
	self.model.remove (ch)
	self.last = iter
	self._sub ()
	self.vexec (expd)
	self._unsub ()
	return False
    def collapsor (self, x, iter, z):
	self.row, expd = self.model.get_value (iter, self.ncol).get_data ('')
	ch = self.model.iter_children (iter)
	while self.model.iter_next (ch):
	    self.model.remove (ch)
	    ch = self.model.iter_children (iter)
	return False
    def _sub (self):
	self.root.append (self.last)
    def _unsub (self):
	self.root.pop ()
    # to macrocode
    def addrow (self, data, expand=None):
	iter = self.model.append (self.root [-1])
	self.last = iter
	for i in range (len (data [0])):
	    self.model.set_value (iter, i, data [0][i])
	O = gobject.GObject()
	if expand: O.set_data ('', (data, expand))
	else: O.set_data ('', (data, 0))
	self.model.set_value (iter, i+1, O)
	if expand:
	    self._sub ()
	    self.addrow (data)
	    self._unsub ()

#
# The popup menu
#

class ___gtkpopup___ (___vexec___, ___implant___):
    def __init__(self, master, code, *args, **kw):
	for i in kw.keys():
	    setattr (self, i, kw [i])
	self.master = master
	self.menu = gtk.Menu ()
	self.istack = []
	self.mstack = [ self.menu ]
	self.implant ('code', code)
	self.vexec (self.code)
	del self.mstack
	self.menu.popup (None, None, None, 1, 0)
    def callback (self, widget, code):
        self.vexec (code)
    # to macrocode
    def item (self, name, code):
        itm = gtk.MenuItem (name)
        self.mstack [-1].append (itm)
        itm.connect ("activate", self.callback, code)
        itm.show ()
    def sub (self, name):
        itm = gtk.MenuItem (name)
        self.mstack [-1].append (itm)
        itm.show ()
        self.mstack.append (gtk.Menu ())
        self.istack.append (itm)
    def unsub (self):
        self.istack.pop ().set_submenu (self.mstack.pop ())
    def sep (self):
        S = gtk.SeparatorMenuItem ()
        S.show ()
        self.mstack [-1].append (S)
#
# workspaces
#

class ___gtknotebook___(___disablable___):
    def __init__ (self, master):
	self.master = master
	self.this = gtk.Notebook ()
    def addon (self, sheet):
	l = gtk.Label ()
	l.set_text_with_mnemonic (sheet.title)
	l.show ()
	sheet.this.show ()
	self.this.append_page (sheet.this, l)
	n = self.this.page_num (sheet.this)
	self.this.set_current_page (n)
	self.this.show_all ()
	self.master.win.show ()

#
# File selection dialog. The FileSelection class is just a
# widget. The FileChoser which is really powerful is not
# available on my version of pytgk. So, for fun, make our
# own modal file choser dialog out of a FileSelection class.
# straight out of the manual
#
class MyFileSelectionDialog(gtk.Dialog):
    def file_ok_sel(self, w):
        self.result = self.filew.get_filename()
	self.close (self)
    def close(self, widget):
	self.looper.quit ()
        self.destroy ()
    def __init__(self, master, title, name):
	gtk.Dialog.__init__ (self, title, master.win,
	              gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_NO_SEPARATOR)
	self.filew = gtk.FileSelection(title)
	lbl = gtk.Label (title)
	self.filew.main_vbox.pack_start (lbl, 1, 1, 0)
	lbl.show ()
	self.filew.connect("destroy", self.close)
	self.filew.ok_button.connect("clicked", self.file_ok_sel)
	self.filew.cancel_button.connect("clicked", self.close)
	if name:
	    self.filew.set_filename(name)
	self.filew.show()
	self.vbox.pack_start (self.filew, True, True, 0)
	self.result = None
	self.looper = gobject.MainLoop ()
	self.connect ('destroy', self.close)
	self.looper.run ()


#
# main sheet class
#

class ___gtksheet___:
    def transplant (self, method, method_name=None):
	transplant (method, self, method_name)
    # Private
    def attach (self, w, v=None):
        if len (self.boxen) > 0:
	    if self.boxen [-1][2] == 'p':
		p, n, tt = self.boxen.pop ()
		if n == 0:
		    p.add1 (w)
		    self.boxen.append ((p, 1, 'p'))
		else:
		    p.add2 (w)
		    self.attach (p)
	    else:
		if not v:
		    if self.boxen [-1][2] == 'h': v = True
		    else: v = False
		self.boxen [-1][0].pack_start (w, v, v, 0)
		#self.boxen [-1][0].pack_start (w, v, True, 0)
    def addwidget (self, b, name):
 	self.attach (b.this)
	if name:
	    setattr (self, name, b)
    def popup (self, code, *args, **kw):
	___gtkpopup___ (self, code, *args, **kw)
    def openFileDialog (self, name=''):
	x = MyFileSelectionDialog (self, "Open File", name)
	return x.result
    def saveFileDialog (self, name=''):
	x = MyFileSelectionDialog (self, "Save File", name)
	return x.result
    def start_construction (self):
        self.boxen = []
        self.radion = []
	self.transistors = []
	self.open_vbox ()
    def end_construction (self):
	self.this = self.boxen [-1][0]
	self.close_box ()
	if len (self.boxen) > 0:
	    print "___gtksheet___ : WARNING. Unclosed container boxes"
    # Protected
    BaseGUI='pygtk'
    def __init__ (self, code=None):
	self.code = code
	if code:
	    self.start_construction ()
	    my_exec (code, globals(), locals ())
	    self.end_construction ()
    def button (self, name=None, text='button', cmd='0', rclick=None):
        b = ___gtkbutton___ (self, text, cmd, rclick)
        self.addwidget (b, name)
	return b
    def checkbutton (self, name=None, text='check', cmd=None, active=0):
        b = ___gtkcheckbutton___ (self, text, cmd, active)
        self.addwidget (b, name)
	return b
    def tbutton (self, name=None, text='tbutton', cmdact='', cmddeact='', active=0):
        b = ___gtktogglebutton___ (self, text, cmdact, cmddeact, active)
        self.addwidget (b, name)
	return b
    def textentry (self, name=None, text='', length=0, cmd='', label=None):
        if label != None:
            self.open_hbox ()
            self.label (text=label)
            b = self.textentry (name, text, length, cmd)
            self.close_box ()
        else:
            b = ___gtkentry___ (self, text, length, cmd)
            self.addwidget (b, name)
	return b
    def label (self, name=None, text='label'):
        b = ___gtklabel___ (self, text)
        self.addwidget (b, name)
    def radio (self, name=None, text='radio', active=False):
	if not name: name=text
        b = ___gtkradiobutton___ (self, self.radion [-1], name, text, self.transistors [-1], active)
        self.addwidget (b, None)
        self.radion [-1] = b.this
	return b
    def editor (self, name=None, dims = (50, 10), font=None, wrap=0, editable=True):
        b = ___gtktext___ (self, (gtk.WRAP_NONE, gtk.WRAP_CHAR, gtk.WRAP_WORD)[wrap], dims, font, editable)
        self.addwidget (b, name)
	return b
    def listbox (self, name=None,gcode='',colnam=[''],scode=None,ecode=None,dims=(20,10),rclick=None):
        b = ___gtklist___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def treebox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(20,10), rclick=None):
        b = ___gtktree___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def streebox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(20,10), rclick=None):
        b = ___gtkstree___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def image (self, filename=None, name=None):
	b = ___gtkimage___ (filename)
	self.addwidget (b, name)
	return b
    def separator (self):
	if len (self.boxen) > 0:
	    if self.boxen [-1][2] == 'h':
		self.boxen [-1][0].pack_start (gtk.VSeparator(), False, True, 5)
	    else:
		self.boxen [-1][0].pack_start (gtk.HSeparator(), False, True, 5)
    def hsplitter (self):
	self.boxen.append ((gtk.HPaned (), 0, 'p'))
    def vsplitter (self):
	self.boxen.append ((gtk.VPaned (), 0, 'p'))
    def open_hbox (self, text=None):
        f = None
        if text:
          f = gtk.Frame (text)
        hb = gtk.HBox (False, 0)
        self.boxen.append ((hb, f, 'h'))
    def open_vbox (self, text=None): 
        f = None
        if text:
          f = gtk.Frame (text)
        hb = gtk.VBox (False, 0)
        self.boxen.append ((hb, f, 'v'))
    def close_box (self):
        hb, f, s = self.boxen.pop ()
        if f:
            f.add (hb)
            self.attach (f, True)
        else:
            self.attach (hb, True)
    def open_radio (self, cmd=None, name=None):
	self.transistors.append (___gtktransistor___ (cmd))
	if name:
	    setattr (self, name, self.transistors [-1])
	self.radion.append (None)
    def close_radio (self):
        self.radion.pop ()
	self.transistors.pop ()
    def tabworkspace (self, name=None):
	b = ___gtknotebook___ (self)
	self.addwidget (b, name)
	return b
    def MDIworkspace (self, name=None):
	return self.tabworkspace (name)

#
# Main class namespace
#

wincount = 0

class Window (___gtksheet___):
    def start_construction (self):
	___gtksheet___.start_construction (self)
	self.win = gtk.Window (gtk.WINDOW_TOPLEVEL)
	self.win.connect ('destroy', self.quit)
    def end_construction (self):
	___gtksheet___.end_construction (self)
	self.win.add (self.this)
	self.win.show_all ()
	global wincount
	wincount += 1
    def __init__ (self, code=None):
	___gtksheet___.__init__ (self, code)
    def settitle (self, title):
	self.win.set_title (title)
    def quit (self, *x):
	self.win.destroy ()
	global wincount
	if wincount > 0: wincount -= 1
	if wincount == 0:
	    terminate ()

class Sheet (___gtksheet___, ___disablable___):
    def start_construction (self):
	___gtksheet___.start_construction (self)
        self.title = ''
    def __init__ (self, workspace, code=None):
	self.workspace = workspace
	___gtksheet___.__init__ (self, code)
    def end_construction (self):
	___gtksheet___.end_construction (self)
	self.workspace.addon (self)
	self.this.show ()
    def settitle (self, title):
	self.title = title
    def show (self):
	pass

class Dialog (___gtksheet___):
    def start_construction (self):
	___gtksheet___.start_construction (self)
        self.title = ''
    def end_construction (self):
 	___gtksheet___.end_construction (self)
	self.dialog = gtk.Dialog (self.title, self.master.win,
		     gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_NO_SEPARATOR)
	self.dialog.connect ('destroy', self.close)
	self.dialog.vbox.pack_start (self.this, True, True, 0)
	self.dialog.show_all  ()
	self.looper = gobject.MainLoop ()
	self.looper.run ()
    def __init__ (self, master, code=None):
	self.master = master
	___gtksheet___.__init__ (self, code)
    def settitle (self, title):
	self.title = title
    def close (self, *args):
	self.looper.quit ()
	self.dialog.destroy ()

main_rUnning = False

def exec_loop ():
    global main_rUnning
    if not main_rUnning:
	main_rUnning = True
	gtk.main ()
	main_rUnning = False

def terminate ():
    gtk.main_quit ()
