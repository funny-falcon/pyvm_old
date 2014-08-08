#
# Twilight GUI wrapper for wxPython
#
# Copyright (C) 2004, Stelios Xanthakis
#  Tom Parker <palfrey@tevp.net>
#

import wx
import wx.lib.evtmgr
import wx.gizmos

#
# Util
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

class disable:
    def disable (self):
	self.this.Disable ()
    def enable (self):
	self.this.Enable ()

def functype(): pass

class ___implant___:
    def implant (self, fname, func):
	if type (func) == type (functype):
	    name = func.__name__
	    transplant (func, self, name)
	    exec 'self.'+fname+'=self.'+name
	else:
	    exec 'self.'+fname+'= func'

class ___vexec___:
    def vexec (self, code):
	if not code: return
	if type (code) == type (''):
	    exec code
	elif type (code) == type (functype):
	    code (self)
	else: code ()

#
# label
#

class ___wxlabel___:
    def __init__ (self, master, text):
        self.this = wx.StaticText (master.win, -1, text)
        self.master = master
    # available to code
    def get_text (self):
        return self.this.GetLabel ()
    def set_text (self, text):
        self.this.SetLabel (text)

#
# buttons
#

class ___wxbutton___(disable, ___vexec___):
    def __init__ (self, master, text, cmd, rcmd):
        self.this = wx.Button (master.win, 10, text)
        self.master = master
        self.code = cmd
        self.rcode = rcmd
        wx.lib.evtmgr.eventManager.Register (self.dostuff2, wx.EVT_RIGHT_UP, self.this)
        wx.lib.evtmgr.eventManager.Register (self.dostuff, wx.EVT_BUTTON, self.this)
    def dostuff (self, *args):
        self.vexec (self.code)
    def dostuff2 (self, *args):
        self.vexec (self.rcode)

class ___wxtogglebutton___(disable, ___vexec___):
    def __init__ (self, master, text, cmda, cmdd, active):
        self.this = wx.ToggleButton (master.win, -1, text)
        self.master = master
        self.cmdact = cmda
        self.cmddeact = cmdd
        if (active):
            self.this.SetValue (1)
        wx.lib.evtmgr.eventManager.Register (self.dostuff, wx.EVT_TOGGLEBUTTON, self.this)
    def dostuff (self, *args):
        if self.this.GetValue ():
            self.vexec (self.cmdact)
        else:
            self.vexec (self.cmddeact)
    # macrocode
    def toggle (self):
        self.this.SetValue (not self.this.GetValue ())
        self.dostuff ()
    def isOn (self):
        return self.this.GetValue ()

class ___wxcheckbutton___(disable, ___vexec___):
    def __init__ (self, master, text, cmd, active):
        self.this = wx.CheckBox (master.win, -1, text)
        self.master = master
        self.code = cmd
        self.active = active
        if (active):
            self.this.SetValue (1)
        wx.lib.evtmgr.eventManager.Register (self.dostuff, wx.EVT_CHECKBOX, self.this)
    def dostuff (self, *args):
        self.active = not self.active
        self.vexec (self.code)
    # macrocode
    def activate (self, value):
        self.this.SetValue (value)
        self.dostuff ()

class ___wxradiobuttongroup___ (___vexec___):
    def __init__ (self, master, cmd, L1, L2, active):
        self.this = wx.RadioBox (master.win, -1, '', wx.DefaultPosition,
			 wx.DefaultSize, L2, 1, wx.RA_SPECIFY_COLS | wx.NO_BORDER)
        self.master = master
        self.code = cmd
        self.this.SetSelection (active)
        wx.lib.evtmgr.eventManager.Register (self.dostuff, wx.EVT_RADIOBOX, self.this)
        self.names = L1
        self.current = self.names [self.this.GetSelection ()]
    def dostuff (self, e):
        self.current = self.names [self.this.GetSelection ()]
        self.vexec (self.code)
    # macrocode
    def activate (self, name):
        if self.names [self.this.GetSelection()] == name:
            return
        for i in range (len (self.names)):
            if self.names [i] == name:
                break
        else:
            print 'No radio button named like that', name
            return
        self.this.SetSelection (i)
    def disable (self, name):
	self.set_able (name, False)
    def enable (self, name):
	self.set_able (name, True)
    def set_able (self, name, value):
        for i in range (len (self.names)):
            if self.names [i] == name:
                break
        else:
            print 'No radio button named like that', name
            return
        self.this.EnableItem (i, value)

#
# image
#

class ___wximage___:
    def __init__ (self, master, image):
	img = wx.Image (image).ConvertToBitmap()
	self.this = wx.StaticBitmap (master.win, -1, img)
    def load (self, image):
	img = wx.Image (image).ConvertToBitmap()
	self.this.SetBitmap (img)

#
# Text
#

class ___wxentry___(disable, ___vexec___):
    def __init__ (self, master, text, length, cmd):
        self.this = wx.TextCtrl (master.win, -1)
	if length > 0:
            gx = self.this.GetCharWidth () * length
            self.this.SetMinSize ((gx, -1))
        if text != '':
            text = self.set_text (text)
        self.master = master
        self.code = cmd
        wx.lib.evtmgr.eventManager.Register (self.dostuff, wx.EVT_CHAR, self.this)
    def dostuff (self, event):
        if event.KeyCode() == 13:
            self.vexec (self.code)
            return
        event.Skip ()
    # Public functions accessible from self.code
    def text (self):
        return self.this.GetValue ()
    def set_text (self, text):
        self.this.SetValue (text)


class ___wxtext___(disable):
    def __init__ (self, master, mode, dims, font, editable):
        self.this = wx.TextCtrl (master.win, -1, '', style=wx.TE_MULTILINE|mode)
        if font:
            i = font.find (' ')
            if i != -1:
                nm = int (font [i+1:])
                font = font [:i]
            else:
                nm = self.this.GetFont ().GetPointSize ()
            self.this.SetFont (wx.Font (nm, wx.SWISS, wx.NORMAL, wx.NORMAL, faceName=font))
        if dims [0] and dims [1]:
            if dims [0]: gx = self.this.GetCharWidth () * dims [0]
            else: gx = -1
            if dims [1]: gy = self.this.GetCharHeight () * dims [1]
            else: gy = -1
            self.this.SetSizeHints (minW = gx, minH = gy)
	self.set_editable (editable)
    # available to code
    def get_text (self):
        return self.this.GetValue ()
    def set_text (self, text):
        self.this.SetValue (text)
    def set_editable (self, setting):
        self.this.SetEditable (setting)



#
# list and tree
#

class ___wxlistbase___(disable, ___vexec___, ___implant___):
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
        self.master = master
	self.implant ('gcode', gcode)
        self.scode = scode
        self.ecode = ecode
        self.rclick = rclick
        if dims [0] or dims [1]:
            if dims [0]: gx = self.this.GetCharWidth () * dims [0]
            else: gx = -1
            if dims [1]: gy = self.this.GetCharHeight () * dims [1]
    	    else: gy = -1
            self.this.SetMinSize ((gx, gy))
        self.reload ()
    def dorclick (self, e):
        self.rowfromevent (e)
        self.vexec (self.rclick)
        e.Skip ()
    def dclicked (self, e):
        self.rowfromevent (e)
        self.vexec (self.ecode)
        e.Skip ()
    def doselected (self, e):
        self.rowfromevent (e)
        self.vexec (self.scode)
        e.Skip ()

class ___wxlist___ (___wxlistbase___):
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
        self.this = wx.ListCtrl (master.win, -1, style=wx.LC_REPORT|wx.BORDER_NONE)
        for i in range (len (colnam)):
            self.this.InsertColumn (i, colnam [i])
	___wxlistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
        wx.lib.evtmgr.eventManager.Register (self.doselected, wx.EVT_LIST_ITEM_SELECTED, self.this)
        wx.lib.evtmgr.eventManager.Register (self.dclicked, wx.EVT_LIST_ITEM_ACTIVATED, self.this)
        wx.lib.evtmgr.eventManager.Register (self.dorclick, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.this)
    def rowfromevent (self, e):
        self.row = self.zdict [self.this.GetItemData (e.m_itemIndex)]
    # to reload code
    def sub (self):
	pass
    def unsub (self):
	pass
    def addrow (self, data):
        i = self.this.Append (data[0])
        self.this.SetItemData (i, self.cnt)
        self.zdict [self.cnt] = data
        self.cnt += 1
    # to macros
    def reload (self):
        self.cnt = 0
        self.zdict = {}
        self.this.DeleteAllItems ()
        self.vexec (self.gcode)

class ___wxstree___ (___wxlistbase___):
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
        self.this = wx.gizmos.TreeListCtrl (master.win, -1)
        self.roots = []
        for i in range (len (colnam)):
            self.this.AddColumn (colnam [i])
	___wxlistbase___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
        wx.lib.evtmgr.eventManager.Register (self.doselected, wx.EVT_TREE_SEL_CHANGED, self.this)
        wx.lib.evtmgr.eventManager.Register (self.dclicked, wx.EVT_TREE_ITEM_ACTIVATED, self.this)
        wx.lib.evtmgr.eventManager.Register (self.dorclick, wx.EVT_TREE_ITEM_RIGHT_CLICK, self.this)
    def rowfromevent (self, e):
        self.row = self.this.GetPyData (e.GetItem ())
    # to reload code
    def sub (self):
        self.roots.append (self.root)
        self.root = self.last
    def unsub (self):
        self.root = self.roots.pop ()
    def addrow (self, data):
        i = self.this.AppendItem (self.root, data [0][0])
        for j in range (len (data[0]) - 1):
            self.this.SetItemText (i, data[0][j+1], j+1)
        self.this.SetItemPyData (i, data)
        self.last = i
    # to macros
    def reload (self):
        self.cnt = 0
        self.zdict = {}
        self.this.DeleteAllItems ()
        self.root = self.this.AddRoot ('') # its gotta have one
        self.vexec (self.gcode)
        self.this.Expand (self.root)

class ___wxtree___ (___wxstree___):
    def __init__ (self, master, gcode, colnam, scode, ecode, dims, rclick):
	___wxstree___.__init__ (self, master, gcode, colnam, scode, ecode, dims, rclick)
        wx.lib.evtmgr.eventManager.Register (self.expander, wx.EVT_TREE_ITEM_EXPANDING, self.this)
        wx.lib.evtmgr.eventManager.Register (self.collapser, wx.EVT_TREE_ITEM_COLLAPSED, self.this)
    def rowfromevent (self, e):
        self.row = self.this.GetPyData (e.GetItem ())[0]
    def collapser (self, e):
	# not collapse the artificial wx root
	if not self.this.GetItemParent (e.GetItem ()).m_pItem:
	    return
	self.this.DeleteChildren (e.GetItem ())
    def expander (self, e):
	self.rowfromevent (e)
	expander = self.this.GetPyData (e.GetItem ())[1]
	self.last = e.GetItem ()
	___wxstree___.sub (self)
	self.vexec (expander)
	___wxstree___.unsub (self)
    # to reload code
    def sub (self):
	pass
    def unsub (self):
	pass
    def addrow (self, data, expander=None):
        i = self.this.AppendItem (self.root, data [0][0])
        for j in range (len (data[0]) - 1):
            self.this.SetItemText (i, data[0][j+1], j+1)
        self.last = i
	self.this.SetItemPyData (i, (data, expander))
	if expander:
	    self.this.SetItemHasChildren (i, True)


#
# Popup menu
#

class ___wxpopup___ (___vexec___, ___implant___):
    def __init__(self, master, code, *args, **kw):
        for i in kw.keys():
            setattr (self, i, kw [i])
        self.master = master
        self.menu = [ (wx.Menu (),'') ]
        self.cdict = {}
	self.implant ('code', code)
        self.vexec (self.code)
        master.win.Bind (wx.EVT_MENU, self.callback)
        master.win.PopupMenu (self.menu [0][0])
    def callback (self, x):
        self.vexec (self.cdict [x.GetId()])
    # to macrocode
    def item (self, name, code):
        id = wx.NewId ()
        self.menu [-1][0].Append (id, name)
        self.cdict [id] = code
    def sub (self, name):
        self.menu.append ((wx.Menu (), name))
    def unsub (self):
        m, n = self.menu.pop ()
        self.menu [-1][0].AppendMenu (-1, n, m)
    def sep (self):
        self.menu [-1][0].AppendSeparator ()




#
# workspace
#

class ___wxnotebook___(disable):
    wstype = 'tab'
    def __init__ (self, master):
	self.this = wx.Notebook (master.win)
	self.master = master
    def addon (self, sheet):
	self.this.AddPage (sheet.win, sheet.title)
	self.this.Show ()

class ___wxmdiworkspace___(disable):
    wstype = 'MDI'
    def __init__ (self, master):
	self.this = wx.MDIParentFrame (master.win, size=(300,120))
	self.this.Show ()
	self.master = master
    def addon (self, sheet):
	sheet.win.Show ()
	pass

#
# main sheet
#

class ___wxsheet___:
    def transplant (self, method, method_name=None):
	transplant (method, self, method_name)
    # Private
    def addwidget (self, b, name):
	if len (self.sizerz) > 0:
	    self.sizerz [-1][0].Add (b.this, flag=wx.ALL)
	    if self.sizerz [-1][1] > -1:
		self.sizerz [-1][1] -= 1
		if self.sizerz [-1][1] == 0:
		    self.close_box ()
	if name:
	    setattr (self, name, b)
    def popup (self, code, *args, **kw):
	___wxpopup___ (self, code, *args, **kw)
    def saveFileDialog (self, name=''):
	dlg = wx.FileDialog (self.win, defaultFile=name, style=wx.SAVE)
	if dlg.ShowModal () == wx.ID_OK:
	    ret = dlg.GetPath ()
	else: ret = None
	dlg.Destroy ()
	return ret
    def openFileDialog (self, name=''):
	dlg = wx.FileDialog (self.win, defaultFile=name, style=wx.OPEN)
	if dlg.ShowModal () == wx.ID_OK:
	    ret = dlg.GetPath ()
	else: ret = None
	dlg.Destroy ()
	return ret
    def start_construction (self):
        self.sizerz = []
        self.radiolist = []
        self.transistors = []
        self.open_vbox ()
    def end_construction (self):
        self.this = self.sizerz.pop ()[0]
    # Protected
    BaseGUI='wxpython'
    def __init__ (self, code=None):
        pass
    def button (self, name=None, text='button', cmd='0', rclick=None):
        b = ___wxbutton___ (self, text, cmd, rclick)
        self.addwidget (b, name)
	return b
    def checkbutton (self, name=None, text='check', cmd='', active=0):
        b = ___wxcheckbutton___ (self, text, cmd, active)
        self.addwidget (b, name)
	return b
    def tbutton (self, name=None, text='tbutton', cmdact='', cmddeact='', active=0):
        b = ___wxtogglebutton___ (self, text, cmdact, cmddeact, active)
        self.addwidget (b, name)
	return b
    def textentry (self, name=None, text='', length=0, cmd='', label=None):
        if label != None:
            self.open_hbox ()
            self.label (text=label)
            b = self.textentry (name, text, length, cmd)
            self.close_box ()
        else:
            b = ___wxentry___ (self, text, length, cmd)
            self.addwidget (b, name)
	return b
    def label (self, name=None, text='label'):
        b = ___wxlabel___ (self, text)
        self.addwidget (b, name)
	return b
    def radio (self, name=None, text='radio', active=False):
	if not name: name=text
        self.radiolist [-1].append ([name, text, active])
    def editor (self, name=None, dims = (50, 10), font=None, wrap=0, editable=True):
        wrp = [ wx.TE_DONTWRAP, wx.TE_LINEWRAP, wx.TE_WORDWRAP ]
        b = ___wxtext___ (self, wrp [wrap], dims, font, editable)
        self.addwidget (b, name)
	return b
    def listbox (self, name=None,gcode='',colnam=[''],scode=None,ecode=None,dims=(0,0),rclick=None):
        b = ___wxlist___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def treebox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(0,0), rclick=None):
        b = ___wxtree___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def streebox (self, name=None, gcode='', colnam=[''], scode=None, ecode=None, dims=(10,20), rclick=None):
        b = ___wxstree___ (self, gcode, colnam, scode, ecode, dims, rclick)
        self.addwidget (b, name)
	return b
    def image (self, name=None, filename=None):
	b = ___wximage___ (self, filename)
	self.addwidget (b, name)
	return b
    def separator (self):
        print "No separators for wx :("         # i don't care
    def hsplitter (self):
	print "No splitters for wx :("
        self.sizerz.append ([wx.BoxSizer (wx.HORIZONTAL),2])
    def vsplitter (self):
	print "No splitters for wx :("
        self.sizerz.append ([wx.BoxSizer (wx.VERTICAL),2])
    def open_hbox (self, text=None):
        if text:
            self.sizerz.append ([wx.StaticBoxSizer (wx.StaticBox (self.win, -1, text), wx.HORIZONTAL), -1])
        else:
            self.sizerz.append ([wx.BoxSizer (wx.HORIZONTAL),-1])
    def open_vbox (self, text=None):
        if text:
            self.sizerz.append ([wx.StaticBoxSizer (wx.StaticBox (self.win, -1, text), wx.VERTICAL),-1])
        else:
            self.sizerz.append ([wx.BoxSizer (wx.VERTICAL),-1])
    def close_box (self):
	class FF:
	 def __init__ (self, w): self.this = w
	self.addwidget (FF (self.sizerz.pop ()[0]), None)
    def open_radio (self, cmd=None, name=None):
        self.transistors.append ((cmd, name))
        self.radiolist.append ([])
    def close_radio (self):
        cmd, name = self.transistors.pop ()
        L = self.radiolist.pop ()
        L0 = [ i [0] for i in L ] 
        L1 = [ i [1] for i in L ] 
        for i in range (len (L)):
            if L[i][2] == True:
                break
        b = ___wxradiobuttongroup___ (self, cmd, L0, L1, i)
        self.addwidget (b, name)
    def tabworkspace (self, name=None):
	b = ___wxnotebook___ (self)
	self.addwidget (b, name)
	return b
    def MDIworkspace (self, name=None):
	b = ___wxmdiworkspace___ (self)
	self.addwidget (b, name)
	return b

#
# Base Interface
#

class Window (___wxsheet___):
    def start_construction (self):
        self.win = wx.Frame (None, -1, '')
        ___wxsheet___.start_construction (self)
    def end_construction (self):
        ___wxsheet___.end_construction (self)
        self.win.SetSizer (self.this)
        self.win.Fit ()
        self.win.Show ()
    	App.SetTopWindow (self.win)
    # Protected
    def __init__ (self, code=None):
        self.code = code
        if code:
           self.start_construction ()
           exec code
           self.end_construction ()
    def settitle (self, title):
        self.win.SetTitle (title)
    def quit (self):
	self.win.Destroy ()

class Sheet (___wxsheet___):
    def start_construction (self):
	if self.workspace.wstype == 'tab':
	    self.win = wx.Panel (self.workspace.this)
	else:
	    self.win = wx.MDIChildFrame (self.workspace.this, -1, "")
	___wxsheet___.start_construction (self)
        self.title = ''
    def end_construction (self):
	___wxsheet___.end_construction (self)
        self.win.SetSizer (self.this)
        self.win.Fit ()
        self.win.Show ()
	self.workspace.addon (self)
    def __init__ (self, workspace, code=None):
	self.workspace = workspace
	self.code = code
	if code:
	    self.start_construction ()
	    exec code
	    self.end_construction ()
    def settitle (self, title):
	self.title = title
    def disable (self):
	self.win.Disable ()
    def enable (self):
	self.win.Enable ()

class Dialog (___wxsheet___):
    def start_construction (self):
        self.win = wx.Dialog (self.master.win, -1, '')
        ___wxsheet___.start_construction (self)
    def end_construction (self):
        ___wxsheet___.end_construction (self)
        self.win.SetSizer (self.this)
        self.win.Fit ()
	self.win.CenterOnScreen ()
        self.win.ShowModal ()
    # Protected
    def __init__ (self, master, code=None):
        self.code = code
	self.master = master
        if code:
           self.start_construction ()
           exec code
           self.end_construction ()
    def settitle (self, title):
        self.win.SetTitle (title)
    def close (self):
 	self.win.Destroy ()

main_running = False

class MyApp(wx.App):
    def OnInit (self):
        return True

App = MyApp ()

def exec_loop ():
    global main_running
    if not main_running:
	main_running = True
 	App.MainLoop ()
	main_running = False

def terminate ():
    global main_running
    main_running = False
    pass
