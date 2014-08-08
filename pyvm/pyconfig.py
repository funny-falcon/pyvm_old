import sys
if sys.version_info[0] != 2 or sys.version_info [1] not in (3, 4):
	print '#error "We need an installed python 2.4/3"'
# Not very robust but works in the common case
path = min ([x for x in sys.path if x.startswith ('/usr')])
print '#define PYTHON_PATH "%s/"'%path
