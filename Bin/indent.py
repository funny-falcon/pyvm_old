'''indent.py

The python indentor (tooth fairy exists).
This uses stuff from the pyc parser in order to study/corrent the indentation
of python sources. The goal is to detect files that use mixed tabs and spaces
and convert them to tabs-only or spaces-only. A full AST tree is also generated
in the procedure of doing so, but good indentation is worth it.

Usage:
	python indent.py -check file1.py file2.py ...
	python indent.py [-tabs|-spaces] file.py

	-check: print whether the file is OK or mixed tabs/spaces
	-tabs: print to stdout with tabs only
	-spaces: print to stdout with spaces only

The -tabs and -spaces modes assume that TABSTOP is 8 characters in file.py
(python's compiler does the same)

Like most programs that try to do correct indentation, it doesn't have true AI
and the result may not be exactly what was expected. More specifically
this indent.py will correct the indentation only where it really matters.
In other places like: indentation of comments, indentation of docstrings
and indentation of expressions it's not so intelligent to figure out what
should be the best visual effect and most likely will not change anything.
'''

# This indentor has indented itself

import sys
if 'Python Software Foundation' in sys.copyright:
	sys.path.append ('../Lib/')

import pyc
from pyc.parser import Lexer, DFA_parser, count_idnt, enumerate1, readline_generator

class MixError:
	def __init__ (self, LINENO):
		self.lineno = LINENO

class CheckIndentor (Lexer):
	def study_idnt (self, LINENO, line):
		for i in line:
			if i == ' ':
				if self.havetabs:
					raise MixError (LINENO)
				self.havespaces = True
			elif i == '\t':
				if self.havespaces:
					raise MixError (LINENO)
				self.havetabs = True
			else: break

	def blank (self, line):
		pass

	def line_generator (self, source_generator):
		for LINENO, line in source_generator:
			sline = line.lstrip ()
			if sline == '' or sline [0] == '#':
				self.blank (line)
				continue
			self.study_idnt (LINENO, line)
			yield LINENO, line

	def rawline_generator (self, source_generator):
		for LINENO, line in source_generator:
			yield LINENO, line.lstrip ()
		raise SyntaxError ("Unexpected end of file")

	def __init__ (self, filename=None, source=None):
		self.havetabs = self.havespaces = False
		x = readline_generator (filename)
		self.LG1 = self.line_generator (x)
		self.SOURCEGEN = self.LG2 = self.rawline_generator (x)

class DFA_indentor (DFA_parser):
	Lexer_class = CheckIndentor

#
#
#

TABSIZE = 8

class Indentor (CheckIndentor):
	def __init__ (self, iq, filename, source):
		CheckIndentor.__init__ (self, filename, source)
		self.istack = [0]
		self.iq = iq
	def blank (self, line):
		if line.strip ():
			# Try to indent comments. the indentation of comments
			# does not alter the current indentation level
			cnt = count_idnt (line)
			if cnt > self.istack [-1]:
				print self.iq * len (self.istack) + line.lstrip ()[:-1]
				return
			for i, j in enumerate (self.istack):
				if cnt == j:
					print self.iq * i + line.lstrip ()[:-1]
					return
		print line[:-1]
	def rawline_generator (self, source_generator):
		for LINENO, line in source_generator:
			print line [:-1]
			yield LINENO, line.lstrip ()
		raise SyntaxError ("Unexpected end of file")
	def study_idnt (self, LINENO, line):
		cnt = 0
		for i in line:
			if i == ' ':
				cnt += 1
			elif i == '\t':
				cnt = ((cnt + TABSIZE) / TABSIZE) * TABSIZE
			else: break
		while cnt < self.istack [-1]:
			self.istack.pop ()
		if cnt > self.istack [-1]:
			self.istack.append (cnt)
		print self.iq * (len (self.istack)-1) + line.lstrip ()[:-1]

class DFA_Indent (DFA_parser):
	def __init__ (self, filename, source, iq):
		lx = Indentor (iq, filename=filename, source=source)
		self.Lexer_class = lambda filename, source : lx
		DFA_parser.__init__ (self, filename, source)


from pyc import gco
gco.GCO.new_compiler ()

if __name__ == '__main__':
	import sys
	O = ''
	for i in ('-check', '-spaces', '-tabs'):
		if i in sys.argv:
			sys.argv.remove (i)
			O += i
	if O == '-check':
		for i in sys.argv [1:]:
			print i+':',
			try:
				DFA_indentor (i, None)
			except MixError, M:
				print "Mixed tabs and spaces, first offeding line:", M.lineno
			else:
				print "OK"
	elif O == '-spaces':
		DFA_Indent (sys.argv [1], None, '    ')
	elif O == '-tabs':
		DFA_Indent (sys.argv [1], None, '\t')
	else:
		print "Need ONE of -check -spaces -tabs"
		print __doc__
