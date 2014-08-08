import struct, imp, os, marshal, sys, ast, gc, parser
from pycodegen	import ast2code
from misc	import import_constants_from_files
from optimizer	import optimize_tree, constify_names, pyc_constants, marshal_builtins
from transform	import transform_tree
from os.path	import getmtime
from symbols	import parseSymbols
from gco	import GCO
#from specialize	import study_specialize

#
# This code is embedded into the beginning of a module if it uses --constants-files
#
DEPCHECK = """
def checkmod (cf, t):
     from os.path import getmtime
     try:
	# if getmtime fails meaning the file is not there, assume OK
	# (for the case somebody has distributed the bytecode only).
	ct = getmtime (cf)
     except:
	return
     if ct != t:
	raise RuntimeError ("DependencyError: file %s has been modified since compilation" % cf)
# Below we will add entries like:
# checkmod ('consts.py', 1122210730)
"""

#
#
def get_version ():
	return '%i.%i' %(sys.version_info [0], sys.version_info [1])


#
def eval_ast (expr, gl=None, lc=None):
	""" Provide an 'eval' function which is identical to the builtin 'eval'.
	The thing is that the expression will be evaluated on the AST nodes
	(dynamic languages cool or what?), without the generation of any
	bytecode objects.
	The existance of an 'eval' function that can evaluate code objects
	is required though (this is not pure in terms of 'no virtual machine
	that can execute python bytecode is required').  The reason is
	that for loops (list comprehensions, generator expressions) we'd
	rather evaluate it in bytecode which is faster.  """

	if gl:
		if lc:
			def lookup_name (x):
				if x in l: return lc [x] 
				if x in gl: return gl [x]
				return __builtins__ [x]
		def lookup_name (x):
			try: return gl [x]
			except: return __builtins__ [x]
	else:
		def lookup_name (x):
			return __builtins__ [x]
	GCO.new_compiler ()
	GCO ['eval_lookup'] = lookup_name
	GCO ['py2ext'] = False
	GCO ['dynlocals'] = True
	GCO ['gnt'] = False
	GCO ['gnc'] = False
	GCO ['filename'] = '*eval*'
	GCO ['docstrings'] = True
	try:
		return parser.parse_expr (source=expr).eval ()
	finally:
		GCO.pop_compiler ()

#
def makePycHeader (filename):
	mtime = os.path.getmtime (filename)
	mtime = struct.pack ('<i', mtime)
	try:
		MAGIC = struct.pack ('<i', GCO ['MAGIC'])
	except:
		MAGIC = imp.get_magic ()
	return MAGIC + mtime

#
def compile(source, filename, mode, flags=None, dont_inherit=None, py2ext=False,
	    dynlocals=True, showmarks=False, ConstDict=None, RRot3=False, asserts=True, nolno=False):
	"""Replacement for builtin compile() function"""
	if flags is not None or dont_inherit is not None:
		raise RuntimeError, "not implemented yet"

	ConstDict = None
	GCO.new_compiler ()
	GCO ['Asserts'] = asserts
	GCO ['dynlocals'] = dynlocals
	GCO ['gnt'] = False
	GCO ['gnc'] = False
	GCO ['showmarks'] = showmarks
	GCO ['rrot3'] = RRot3
	GCO ['py2ext'] = py2ext
	GCO ['filename'] = filename and os.path.abspath (filename) or '*eval*'
	GCO ['arch'] = get_version ()
	GCO ['lnotab'] = not nolno
	GCO ['pyvm'] = sys.copyright.startswith ('pyvm')
	GCO ['docstrings'] = True

	try:
		if mode == "exec":
			if not source:
				tree = parser.parse (filename=filename)
			else:							# ???
				tree = parser.parse (filename=filename, source=source)
			transform_tree (tree)
			if GCO ['have_with']:
				tree.Import ('sys')
			if ConstDict:
				constify_names (tree, ConstDict)
			pyc_constants (tree)
			parseSymbols (tree)
			optimize_tree (tree)
		elif mode == "eval":
			tree = ast.Expression (parser.parse_expr (source))
			transform_tree (tree)
			pyc_constants (tree)
			parseSymbols (tree)
		elif mode == "single":
			# XXX pass an iterator from which it can read more lines!
			tree = parser.parse (source=source)
			if GCO ['have_with']:
				tree.Import ('sys')
			transform_tree (tree)
			pyc_constants (tree)
			parseSymbols (tree)
		else:
			raise ValueError("compile() 3rd arg must be 'exec' or "
                             "'eval' or 'single'")
		return ast2code (tree, mode)
	finally:
		GCO.pop_compiler ()

#
import arch24

def compileFile(filename, display=0, dynlocals=True, py2ext=False, showmarks=False,
		constfiles=None, rrot3 = False, mtime=True, marshal_builtin=False,
		asserts=True, nolno=False, altdir=None, pyvm=False, output=None,
		arch=None, docstrings=True):

	# compileFile returns the filename of the pyc file on success.
	# it's possible that we won't be able to store the pyc next to the py

	if arch is None:
		arch = get_version ()
	if arch not in ('2.4', '2.3', 'pyvm'):
		print "Cannot produce bytecode for %s" %arch
		raise SystemExit

	constfiles=None
	pe = filename.endswith ('.pe')
	GCO.new_compiler ()
	GCO ['dynlocals'] = dynlocals
	GCO ['gnt'] = arch == 'pyvm'
	GCO ['gnc'] = arch == 'pyvm'
	GCO ['showmarks'] = showmarks
	GCO ['rrot3'] = rrot3
	GCO ['py2ext'] = filename.endswith ('.py2') or py2ext or pe
	GCO ['filename'] = os.path.abspath (filename)
	GCO ['Asserts'] = asserts
	if arch == 'pyvm':
		MAGIC = arch24.MAGIC_PYVM
	elif arch == '2.4':
		MAGIC = arch24.MAGIC
	else:
		MAGIC = arch24.MAGIC23
	GCO ['MAGIC'] = MAGIC
	GCO ['arch'] = arch
	GCO ['lnotab'] = not nolno
	GCO ['pyvm'] = pyvm
	GCO ['docstrings'] = docstrings

	try:
		if not pe:
			tree = parser.parse (filename)
		else:
			import epl
			tree = epl.parse (filename)
		if GCO ['have_with']:
			tree.Import ('sys')
		transform_tree (tree)
		pyc_constants (tree)
		if constfiles:
			constify_names (tree, import_constants_from_files (constfiles))

			# Dependency check
			if mtime:
				TestDep = DEPCHECK + '\n'.join (
		          ['checkmod ("%s", %i)' % (intern (os.path.abspath (i)), getmtime (i)) for
			  i in constfiles]) + '\ndel checkmod\n'
				tree.node.nodes.insert (0, parser.parse (source=TestDep).node)
		parseSymbols (tree)
		if marshal_builtin:
			marshal_builtins (tree)
		optimize_tree (tree)
###		study_specialize (tree.Functions)
		codeobj = ast2code (tree, 'exec')
		if output:
			outfile = output
		elif filename.endswith ('.py2'):
			outfile = filename [:-1] + 'c'
		elif pe:
			outfile = filename [:-1] + 'yc'
		else:
			outfile = filename + 'c'
		try:
			f = open(outfile, "wb")
		except IOError:
			if altdir is None:
				raise
			outfile = altdir (outfile)
			f = open (outfile, "wb")
		f.write(makePycHeader (filename))
		gc.collect ()
		if arch == 'pyvm':
			marshal.dump(codeobj, f, 2006)
		else:
			marshal.dump(codeobj, f)
		return outfile
	finally:
		GCO.pop_compiler ()

#
def altpyc (fnm):
	return os.path.join (sys.pyctmp, fnm.replace ('/', '_'))

def compileFile_internal (*args, **kwargs):
	# this is what pyvm uses internally to compile files
	# if the file pyc output can't be saved next to the py file,
	# it goes to the temporaries
	# xxx: reentrant lock
	kwargs ['altdir'] = altpyc
	kwargs ['pyvm'] = True
	kwargs ['dynlocals'] = False
	kwargs ['rrot3'] = True
	kwargs ['marshal_builtin'] = True
	return compileFile (*args, **kwargs)
