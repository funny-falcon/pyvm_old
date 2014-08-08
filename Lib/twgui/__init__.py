"""Twilight GUI

init (wlist=('tk', 'gtk', 'qt', 'wx', 'pgu'))	

	attempt to import the wrappers with the preferred order.
	returns the first module that suceeded. Edit this file
	and set your favorites.
"""

def init (wlist = ('tk', 'gtk', 'qt', 'wx')):
    for i in wlist:
	if i == 'tk':
	    try:
		import wrap_tkinter as GUI
	    except:
		continue
	elif i == 'gtk':
	    try:
		import wrap_pygtk as GUI
	    except:
		continue
	elif i == 'qt':
	    try:
		import wrap_pyqt as GUI
	    except:
		continue
	elif i == 'wx':
	    try:
		import wrap_wxpython as GUI
	    except:
		continue
	else:
	    print "Unknown widget set:", i
	    continue
	return GUI
