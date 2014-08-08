#
# Twilight GUI wrapper for Tkinter
#
# Copyright (C) 2004, Stelios Xanthakis
#  Tom Parker <palfrey@tevp.net>
#
# The notebook widget is inspired on the notebook recipe
# from ASPN, which is:
#   Copyright 2003, Iuri Wickert (iwickert yahoo.com)
# The list was inspired on IDLE's list implementation
#

import Tkinter
import tkFileDialog
import tkFont
import ScrolledText
import string

havePIL = True
try:
    import PIL
    import Image, ImageTk
except ImportError: havePIL = False

def my_exec (source, g=None, l=None):
    eval (compile (source, "exec", "exec"), g, l)

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
      return self.method (*nargs, **kwargs)

class ___disablable___:
    def disable (self):
	self.this ['state'] = Tkinter.DISABLED
    def enable (self):
	self.this ['state'] = Tkinter.NORMAL

def functype(): pass

class ___implant___:
    def implant (self, fname, func):
	if type (func) == type (functype):
	    name = func.__name__
	    transplant (func, self, name)
	    setattr (self, fname, getattr (self, name))
#	    exec 'self.'+fname+'=self.'+name
	else:
	    setattr (self, fname, func)
#	    exec 'self.'+fname+'= func'

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

class ___tklabel___(___disablable___):
    fill = Tkinter.X
    def __init__ (self, master, text):
        self.this = Tkinter.Label (master.boxen [-1][0], text=text)
        self.master = master
    # available to code
    def get_text (self):
	return self.this ['text']
    def set_text (self, text):
	self.this ['text'] = text

#
# buttons
#

class ___tkbutton___(___disablable___, ___vexec___):
    fill = Tkinter.X
    def __init__ (self, master, text, cmd, rcmd):
	self.this = Tkinter.Button (master.boxen [-1][0], text=text, command=self.dostuff)
	self.master = master
        self.code = cmd
	self.rcode = rcmd
	self.this.bind ("<Button-3>", self.dostuff2)
    def dostuff (self, *args):
	self.vexec (self.code)
    def dostuff2 (self, event):
	if self.rcode and self.this ['state'] != Tkinter.DISABLED:
	    self.vexec (self.rcode)

class ___tkcheckbutton___ (___disablable___, ___vexec___):
    fill = Tkinter.X
    def __init__ (self, master, text, cmd, active):
	self.this = Tkinter.Checkbutton (master.boxen [-1][0], text=text, command=self.dostuff)
	self.master = master
	self.code = cmd
	self.active = active
	if (active):
	   self.this.select ()
    def dostuff (self, *args):
	self.active = not self.active
	self.vexec (self.code)
    # macrocode
    def activate (self, value):
	if self.active and not value:
	    self.this.deselect ()
	    self.dostuff ()
	elif value and not self.active:
	    self.this.select ()
	    self.dostuff ()

class ___tktogglebutton___(___disablable___, ___vexec___):
    fill = Tkinter.X
    def __init__ (self, master, text, cmda, cmdd, active):
        self.this = Tkinter.Button (master.boxen [-1][0], text=text, command=self.dostuff)
        self.master = master
        self.cmdact = cmda
        self.cmddeact = cmdd
	self.active = active
        if active:
            self.this ['relief'] = Tkinter.SUNKEN
    def dostuff (self, *args):
	self.active = not self.active
	if self.active:
	    self.vexec (self.cmdact)
            self.this ['relief'] = Tkinter.SUNKEN
	else:
	    self.vexec (self.cmddeact)
            self.this ['relief'] = Tkinter.RAISED
    # macrocode
    def toggle (self):
        self.dostuff ()
    def isOn (self):
	return self.active

class ___tktransistor___ (___vexec___):
    def __init__ (self, cmd):
	self.cmd = cmd
	self.current = None
	self.var = Tkinter.StringVar ()
	self.rn = {}
    def transist (self, radio):
	self.var.set (radio)
	self.current = radio
	self.vexec (self.cmd)
    def addradio (self, name, widget, active=False):
	self.rn [name] =  widget
	if active:
	    self.current = name
	    self.var.set (name)
    # to macrocode
    def activate (self, name):
	if self.var.get () == name:
	    return
	self.rn [name].dostuff ()
    def disable (self, name):
	self.rn [name].disable ()
    def enable (self, name):
	self.rn [name].enable ()

class ___tkradiobutton___(___disablable___):
    fill = Tkinter.X
    def __init__ (self, master, name, text, tr, active):
        self.this = Tkinter.Radiobutton (master.boxen [-1][0], text=text, variable = tr.var, value=name, command = self.dostuff)
        self.transistor = tr
	self.name = name
	tr.addradio (name, self, active)
    def dostuff (self, *args):
        self.transistor.transist (self.name)

#
# image
#

class ___tkimage___:
    fill = Tkinter.X
    def __init__ (self, master, img):
	self.this = Tkinter.Label (master.boxen [-1][0])
	if img: self.load (img)
    def load (self, img):
	if not havePIL:
	    self.img0 = Tkinter.PhotoImage (file=img)
	else: # untested...
	    im = Image.open (img)
	    self.img0 = ImageTk.PhotoImage (im)
	self.this ['image'] = self.img0

#
# text entries
#

class ___tkentry___(___disablable___, ___vexec___):
    fill = Tkinter.X
    def __init__ (self, master, text, length, cmd):
	self.this = Tkinter.Entry (master.boxen [-1][0])
	if length > 0: self.this ['width'] = length
        if text != '':
            text = self.set_text (text)
        self.master = master
        self.code = cmd
	self.this.bind ("<Return>", self.dostuff)
    def dostuff (self, *args):
        self.vexec (self.code)
    # Public functions accessible from self.code
    def text (self):
        return self.this.get ()
    def set_text (self, text):
	self.this.delete (0, Tkinter.END)
        self.this.insert (Tkinter.END, text)

class ___tktext___:
    fill = Tkinter.BOTH
    def disable (self):
	self.txt ['state'] = Tkinter.DISABLED
    def enable (self):
	self.txt ['state'] = Tkinter.NORMAL
    def __init__ (self, master, mode, dims, font, editable):
	self.font = font
	# must put in frame because ScrolledText is incompatible
	# with PanedWindow.add (...)
	self.this = Tkinter.Frame (master.boxen [-1][0])
	self.txt = ScrolledText.ScrolledText (self.this, wrap= (Tkinter.NONE, Tkinter.CHAR, Tkinter.WORD) [mode], background="white")
	if font:
	    if ' ' in font:
		i = font.find (' ')
		tup = (font [:i], font [i+1:])
	    else: tup = (font, '12')
	    self.txt ['font'] = tup
	if dims [0] > 0: self.txt ['width'] = dims [0]
	if dims [1] > 0: self.txt ['height'] = dims [1]
	self.editable = editable
	if not editable:
	    self.disable ()
	self.txt.pack (fill=Tkinter.BOTH, expand=Tkinter.YES)
    # available to code
    def get_text (self):
	return self.txt.get ("0.0", Tkinter.END)
    def set_text (self, text):
	if not self.editable: self.enable ()
	self.txt.delete ("0.0", Tkinter.END)
	self.txt.insert (Tkinter.END, text)
	if not self.editable: self.disable ()
    def set_editable (self, setting):
	self.editable = setting
	if self.editable: self.enable ()
	else: self.disable ()

#
# Lists and trees
# tkinter tree is pain in the ass and has troubled many people
#  here we have an ascii tree for now
# In the case we have a list with many columns, we use multiple ___smalllist___s
#  in one frame sharing the same scrollbar.  Must use PanedWindow between them...
#

class ___smalllist___:
    default = "(None)"
    def __init__ (self, master, name, vbar, parent):
	self.parent = parent
        self.master = master
        self.frame = frame = Tkinter.Frame(master)
        self.frame.pack(fill="both", expand=1, side="left")
	self.label = Tkinter.Label (frame, text=name)
	self.label.pack (side="top")
	self.vbar = vbar
        self.listbox = listbox = Tkinter.Listbox(frame, exportselection=0, background="white")
        listbox.pack(expand=1, fill="both")
        listbox["yscrollcommand"] = parent.set
        listbox.bind("<ButtonRelease-1>", self.click_event)
        listbox.bind("<Double-ButtonRelease-1>", self.double_click_event)
        listbox.bind("<Return>", self.double_click_event)
        listbox.bind("<ButtonPress-3>", self.popup_event)
        listbox.bind("<Key-Up>", self.up_event)
        listbox.bind("<Key-Down>", self.down_event)
        self.clear()
    def yview (self, *args):
	self.listbox.yview (*args)
    def close(self):
        self.frame.destroy()
    def clear(self):
        self.listbox.delete(0, "end")
        self.empty = 1
        self.listbox.insert("end", self.default)
    def get(self, index):
        return self.listbox.get(index)
    def up_event(self, event):
        index = self.listbox.index("active")
        if self.listbox.selection_includes(index):
            index = index - 1
        else:
            index = self.listbox.size() - 1
        if index < 0:
            self.listbox.bell()
        else:
            self.select(index)
            self.parent.on_select(index)
        return "break"
    def down_event(self, event):
        index = self.listbox.index("active")
        if self.listbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.listbox.size():
            self.listbox.bell()
        else:
            self.select(index)
            self.parent.on_select(index)
        return "break"
    def double_click_event(self, event):
        index = self.listbox.index("active")
        self.select(index)
        self.parent.on_double(index)
        return "break"
    def popup_event(self, event):
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
        self.select(index)
	self.parent.fill_menu (index)
    def select(self, index):
	self.parent.select (index)
    def _select (self, index):
        self.listbox.focus_set()
        self.listbox.activate(index)
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.see(index)

class ___scrolledlist___ (___smalllist___):
    def __init__(self, master, name, vbar, parent):
	___smalllist___.__init__ (self, master, name, vbar, parent)
    def addrow(self, item, idx="end"):
        if self.empty:
            self.listbox.delete(0, "end")
            self.empty = 0
        self.listbox.insert(idx, str(item))
    def click_event(self, event):
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
        self.select(index)
        self.parent.on_select(index)
        return "break"
    def delete (self, i1, i2):
	self.listbox.delete (i1, i2)

class ___scrolledtree___ (___smalllist___):
    def __init__(self, master, name, vbar, parent):
	___smalllist___.__init__ (self, master, name, vbar, parent)
	self.listbox ['font'] = 'courier -12 normal'
	fn= self.listbox ['font']
	fnl=string.split (fn)
	self.myfont = tkFont.Font (family=fnl[0], size=fnl[1], weight=fnl[2])
    def click_event(self, event):
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
	txt = self.listbox.get (index)
	j = txt.find ('-+')
	k = txt.find ('-*')
	if j != -1 and event.x > self.myfont.measure (txt[:j])\
		 and event.x <= self.myfont.measure (txt[:j+2]):
	    self.parent.expand (index)
	elif k != -1 and event.x > self.myfont.measure (txt[:k])\
		 and event.x <= self.myfont.measure (txt[:k+2]):
	    t = len (self.tstr (index))
	    i = index + 1
	    while len (self.tstr (i)) > t: i += 1 
	    self.parent.collapse (index+1, i)
	else:
            self.select(index)
            self.parent.on_select(index)
        return "break"
    def tstr (self, index):
	fn = self.listbox.get (index)
	return fn [:fn.find ('-')+2]
    def altstr (self, index, i, c):
	fn = self.listbox.get (index)
	tstr = fn [:fn.find ('-')+2]
	nstr = tstr [:i] + c
	if i != -1: nstr += tstr [i+1:]
	nm = fn [fn.find ('-')+2:]
	self.listbox.delete (index)
	self.listbox.insert (index, nstr + nm)
    def addrows (self, index, tdata):
        if self.empty:
            self.listbox.delete(0, "end")
            self.empty = 0
	    ast = ''
	else:
	    ast = self.tstr (index)[:-2] + ' |'
	    if len (ast) > 3 and ast [-3] == '\\':
		ast = ast [:-3] + ' ' + ast [-2:]
	    self.altstr (index, -1, '*')
	index += 1
	for i in range (len (tdata)):
	    if tdata [i][1]: vst = ast + '-+'
	    else: vst = ast + '--'
	    if vst [0] != '-' and i == len (tdata)-1:
		vst = vst [:-3] + '\\' + vst [-2:]
            self.listbox.insert(index + i, vst + tdata [i][0])
    def delete (self, i1, i2):
	self.altstr (i1-1, -1, '+')
	self.listbox.delete (i1, i2)

class ___tklistbase___(___disablable___, ___vexec___, ___implant___):
    fill = Tkinter.BOTH
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	self.master = master
	self.this = Tkinter.Frame (master.boxen [-1][0])
	self.vbar = Tkinter.Scrollbar(self.this, name="vbar")
	self.lists = [self.FirstL (self.this, colnam [0], self.vbar, self)]
	for i in colnam[1:]:
	   self.lists.append (___scrolledlist___ (self.this, i, self.vbar, self))
	self.vbar.pack(side="right", fill="y")
	self.vbar ['command'] = self.set_all
	self.this.pack ()
	self.implant ('gcode', gcode)
	self.scode = scode
	self.ecode = ecode
	self.rclick = rclick
	self.reload ()
    def sub (self): pass
    def unsub (self): pass
    def select(self, index):
	for i in self.lists:
	    i._select (index)
    def set_all (self, *args):
	for i in self.lists:
	    i.yview (*args)
    def set (self, *args):
	self.vbar.set (*args)
	self.set_all ('moveto', args [0])
    def fill_menu(self, index):
	self.rowdata (index)
        self.vexec (self.rclick)
    def on_select(self, index):
	self.rowdata (index)
        self.vexec (self.scode)
    def on_double(self, index):
	self.rowdata (index)
        self.vexec (self.ecode)
    def reload (self, code=None):
	if code: self.gcode = code
	for i in self.lists:
	    i.clear ()
	self.data = []
	self.vexec (self.gcode)

class ___tklist___ (___tklistbase___):
    FirstL = ___scrolledlist___
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	___tklistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
    def rowdata (self, index):
	self.row = self.data [index]
    def addrow (self, data):
	for i in range (len (data[0])):
	      self.lists [i].addrow (data [0][i])
	self.data.append (data)

class ___tktree___ (___tklistbase___):
    FirstL = ___scrolledtree___
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	self.idx = 'end'
	self.astr = ''
	self.tdata = []
	___tklistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
    def rowdata (self, index):
	self.row = self.data [index][0]
    def expand (self, index):
	self.row = self.data [index][0]
	fn = self.lists [0].get (index)
	rfn = self.row [0][0]
	self.astr = fn [:-(len (rfn)+2)] + ' |'
	self.idx = index+1
	self.tdata = []
	self.data [index][1] ()
	self.lists [0].addrows (index, self.tdata)
    def collapse (self, i1, i2):
	for i in self.lists:
	    i.delete (i1, i2-1)
	self.data = self.data [:i1] + self.data [i2:]
    # public
    def addrow (self, data, expander=None):
	self.tdata.append ((data [0][0], expander!=None))
	for i in range (len (data[0]))[1:]:
	    self.lists [i].addrow (data [0][i], self.idx)
	if self.idx == 'end':
	    self.data.append ((data, expander))
	else:
	    self.data.insert (self.idx, (data, expander))
	    self.idx += 1
    def reload (self, code=None):
	___tklistbase___.reload (self, code)
	self.lists [0].addrows (0, self.tdata)

class ___tkstree___ (___tklistbase___):
    FirstL = ___scrolledtree___
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	self.idx = 'end'
	self.astr = ''
	self.tdata = []
	___tklistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
    def rowdata (self, index):
	self.row = self.data [index][0]
    def addrows (self, index, xindex):
	self.tdata = []
	idx = index + 1
	for i in self.xlists [xindex]:
	    self.tdata.append ((i[0][0][0], i[1] != -1))
	    for j in range (len (i[0][0]))[1:]:
	        self.lists [j].addrow (i [0][0][j], idx)
	    self.data.insert (idx, i)
	    idx += 1
	self.lists [0].addrows (index, self.tdata)
    def expand (self, index):
	self.addrows (index, self.data [index][1])
    def collapse (self, i1, i2):
	for i in self.lists:
	    i.delete (i1, i2-1)
	self.data = self.data [:i1] + self.data [i2:]
    # public
    def addrow (self, data):
	self.xlists [self.xn].append ((data, -1))
    def sub (self):
	x = len (self.xlists)
	s = self.xlists [self.xn][-1][0]
	self.xlists [self.xn][-1] = (s, x)
	self.xlists.append ([])
	self.xnl.append (self.xn)
	self.xn = x
    def unsub (self):
	self.xn = self.xnl.pop ()
    def reload (self, code=None):
	self.xlists = [[]]
	self.xn = 0
	self.xnl = []
	___tklistbase___.reload (self, code)
	self.addrows (0, 0)

#
# The popup menu
#

class ___tkpopup___ (___vexec___, ___implant___):
    def __init__(self, master, code, *args, **kw):
	for i in kw.keys():
	    setattr (self, i, kw [i])
	self.master = master
	self.menu = Tkinter.Menu (master.win, tearoff=0)
	self.istack = []
	self.mstack = [ self.menu ]
	self.implant ('code', code)
	self.vexec (self.code)
	self.menu.tk_popup (*master.win.winfo_pointerxy())
    def callback (self, code):
        self.vexec (code)
    # to macrocode
    def item (self, name, code):
	self.mstack [-1].add_command (label=name, command = lambda : self.callback (code))
    def sub (self, name):
	self.istack.append (name)
        self.mstack.append (Tkinter.Menu (self.master.win, tearoff = 0))
    def unsub (self):
	sm = self.mstack.pop ()
	self.mstack [-1].add_cascade (label=self.istack.pop (), menu = sm)
    def sep (self):
        self.mstack [-1].add_separator ()

#
# workspaces
#

class ___tknotebook___(___disablable___):
    fill = Tkinter.BOTH
    def __init__(self, master):
	self.master = master
	self.active_fr = None
	self.count = 0
	self.choice = Tkinter.IntVar(0)
	self.this = Tkinter.Frame (master.boxen [-1][0])
	self.rb_fr = Tkinter.Frame(self.this, borderwidth=2, relief=Tkinter.RIDGE)
	self.rb_fr.pack(side=Tkinter.TOP, fill=Tkinter.BOTH)
	self.screen_fr = Tkinter.Frame(self.this, borderwidth=2, relief=Tkinter.RIDGE)
	self.screen_fr.pack(fill=Tkinter.BOTH)
    def __call__(self):
	return self.screen_fr
    def add_screen(self, fr, title):
	b = Tkinter.Radiobutton(self.rb_fr, text=title, indicatoron=0, \
		variable=self.choice, value=self.count, \
		command=lambda: self.display(fr))
	b.pack(fill=Tkinter.BOTH, side=Tkinter.LEFT)
	if not self.active_fr:
	    fr.pack(fill=Tkinter.BOTH, expand=1)
	    self.active_fr = fr
	self.count += 1
    def display(self, fr):
	self.active_fr.forget()
	fr.pack(fill=Tkinter.BOTH, expand=1)
	self.active_fr = fr

#
# main sheet class
#

class ___tksheet___:
    def transplant (self, method, method_name=None):
	transplant (method, self, method_name)
    # Private
    def attach (self, w, fill):
	w.pack (side=self.boxen [-1][1], fill=fill, expand=Tkinter.YES)
	if self.boxen [-1][2] == 2:
	    self.boxen [-1][2] = 1
	    self.boxen [-1].append (w)
	elif self.boxen [-1][2] == 1:
	    w2 = self.boxen [-1][0]
	    w2.add (self.boxen.pop () [3])
	    w2.add (w)
	    self.attach (w2, Tkinter.BOTH)
    def addwidget (self, b, name):
 	self.attach (b.this, b.fill)
	if name:
	    setattr (self, name, b)
    def popup (self, code, *args, **kw):
	___tkpopup___ (self, code, *args, **kw)
    def openFileDialog (self, name=''):
	return tkFileDialog.askopenfilename (initialfile = name)
    def saveFileDialog (self, name=''):
	return tkFileDialog.asksaveasfilename (initialfile = name)
    def start_construction (self):
        self.boxen = [ (self.win, Tkinter.TOP, -1) ]
	self.transistors = []
	self.icnt = 0
    def end_construction (self):
	if len (self.boxen) > 1:
	    print "___tksheet___ : WARNING. Unclosed container boxes"
    # Protected
    BaseGUI='tkinter'
    def __init__ (self, code=None):
	self.code = code
	if code:
	    self.start_construction ()
	    my_exec (code, globals(), locals ())
	    self.end_construction ()
    def button (self, name=None, text='button', cmd='0', rclick=None):
        b = ___tkbutton___ (self, text, cmd, rclick)
        self.addwidget (b, name)
	return b
    def checkbutton (self, name=None, text='check', cmd=None, active=0):
        b = ___tkcheckbutton___ (self, text, cmd, active)
        self.addwidget (b, name)
	return b
    def tbutton (self, name=None, text='tbutton', cmdact='', cmddeact='', active=0):
        b = ___tktogglebutton___ (self, text, cmdact, cmddeact, active)
        self.addwidget (b, name)
	return b
    def textentry (self, name=None, text='', length=0, cmd='', label=None):
        if label != None:
            self.open_hbox ()
            self.label (text=label)
            b = self.textentry (name, text, length, cmd)
            self.close_box ()
        else:
            b = ___tkentry___ (self, text, length, cmd)
            self.addwidget (b, name)
	return b
    def label (self, name=None, text='label'):
        b = ___tklabel___ (self, text)
        self.addwidget (b, name)
    def radio (self, name=None, text='radio', active=False):
	if not name: name=text
        b = ___tkradiobutton___ (self, name, text, self.transistors [-1], active)
        self.addwidget (b, None)
	return b
    def editor (self, name=None, dims = (50, 10), font=None, wrap=0, editable=True):
        b = ___tktext___ (self, wrap, dims, font, editable)
        self.addwidget (b, name)
	return b
    def listbox (self, name=None,gcode='',colnam=[''],scode=None,ecode=None,dims=(20,10),rclick=None):
        b = ___tklist___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def treebox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(20,10), rclick=None):
        b = ___tktree___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def streebox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(20,10), rclick=None):
        b = ___tkstree___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def image (self, filename=None, name=None):
	b = ___tkimage___ (self, filename)
	if not name:
	    # got to have a name otherwise it's garbage collected!
	    name = 'NYPD'+str (self.icnt)
	    self.icnt += 1
	self.addwidget (b, name)
	return b
    def separator (self):
	# is there one?
	pass
    def hsplitter (self):
	self.boxen.append ([Tkinter.PanedWindow (self.boxen [-1][0], handlesize=1, sashwidth=1), Tkinter.LEFT, 2])
    def vsplitter (self):
	self.boxen.append ([Tkinter.PanedWindow (self.boxen [-1][0], orient=Tkinter.VERTICAL, handlesize=1), Tkinter.TOP, 2])
    def open_hbox (self, text=None):
	if text:
	   self.boxen.append ((Tkinter.LabelFrame (self.boxen [-1][0], text=text), Tkinter.LEFT,-1))
	else:
	   self.boxen.append ((Tkinter.Frame (self.boxen [-1][0]), Tkinter.LEFT, -1))
    def open_vbox (self, text=None): 
	if text:
	   self.boxen.append ((Tkinter.LabelFrame (self.boxen [-1][0], text=text), Tkinter.TOP, -1))
	else:
	   self.boxen.append ((Tkinter.Frame (self.boxen [-1][0]), Tkinter.TOP, -1))
    def close_box (self):
	p = self.boxen.pop ()
        w = p [0]
	s = p [1]
	self.attach (w, Tkinter.BOTH)
    def open_radio (self, cmd=None, name=None):
	self.transistors.append (___tktransistor___ (cmd))
	if name:
	    setattr (self, name, self.transistors [-1])
    def close_radio (self):
	self.transistors.pop ()
    def tabworkspace (self, name=None):
	b = ___tknotebook___ (self)
	self.addwidget (b, name)
	return b
    def MDIworkspace (self, name=None):
	return self.tabworkspace (name)

#
# Main class namespace
#

class Window (___tksheet___):
    def start_construction (self):
	self.win = Tkinter.Tk ()
	___tksheet___.start_construction (self)
    def end_construction (self):
	___tksheet___.end_construction (self)
	self.win.protocol("WM_DELETE_WINDOW", self.quit)
	self.win.mainloop ()
    def __init__ (self, code=None):
	___tksheet___.__init__ (self, code)
    def settitle (self, title):
	self.win.title (title)
    def quit (self):
	self.win.destroy ()

class Sheet (___tksheet___, ___disablable___):
    def start_construction (self):
	self.this = self.win = Tkinter.Frame (self.workspace ())
	___tksheet___.start_construction (self)
        self.title = ''
    def __init__ (self, workspace, code=None):
	self.workspace = workspace
	___tksheet___.__init__ (self, code)
    def end_construction (self):
	___tksheet___.end_construction (self)
	self.workspace.add_screen (self.win, self.title)
    def settitle (self, title):
	self.title = title
    def show (self):
	pass

class Dialog (___tksheet___):
    def start_construction (self):
	self.win = Tkinter.Toplevel (self.master.win)
	self.win.transient (self.master.win)
	self.win.geometry("+%d+%d" % (self.master.win.winfo_rootx()+50,
                                  self.master.win.winfo_rooty()+50))
	___tksheet___.start_construction (self)
        self.title = ''
    def end_construction (self):
 	___tksheet___.end_construction (self)
	self.win.grab_set()
	self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.win.wait_window(self.win)
    def __init__ (self, master, code=None):
	self.master = master
	___tksheet___.__init__ (self, code)
    def settitle (self, title):
	self.win.title (title)
    def close (self, *args):
	self.win.destroy ()

main_running = False

def exec_loop ():
    global main_running
    if not main_running:
	main_running = True

def terminate ():
    global main_running
    main_running = False

