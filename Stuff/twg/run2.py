#!/usr/bin/env python


import sys


GUI = None
GUIList = []

if 1:
 try:
    import wrap_pygtk
    have_pygtk = True
    if not GUI:
	GUI = wrap_pygtk
    GUIList.append (('PyGTK', wrap_pygtk))
 except ImportError:
    print "pygtk not found"
    have_pygtk = False

if 1:
 try:
    import wrap_pyqt
    have_pyqt = True
    if not GUI:
        GUI = wrap_pyqt
    GUIList.append (('PyQT', wrap_pyqt))
 except ImportError:
    print "pyqt not found"
    have_pyqt = False

if 1:
 try:
    import wrap_wxpython
    have_wxpython = True
    if not GUI:
	GUI = wrap_wxpython
    GUIList.append (('wxPython', wrap_wxpython))
 except ImportError:
    print "wxpython not found"
    have_wxpython = False

if 1:
 try:
    import wrap_tkinter
    have_tkinter = True
    if not GUI:
	GUI = wrap_tkinter
    GUIList.append (('Tkinter', wrap_tkinter))
 except ImportError:
    print "tkinter not found"
    have_tkinter = False

if not GUI:
    print "No toolkits"
    sys.exit (1)

FILE='Editor2.py'
WRAPPER=None

for i in sys.argv [1:]:
    if i[0] == '-':
        WRAPPER = i[1:]
    else: FILE = i

if WRAPPER:
    exec ('GUI=wrap_'+WRAPPER)

print "Ok. Current GUI["+GUI.Window.BaseGUI+"]"

execfile (FILE, globals(), globals())

GUI.exec_loop ()
