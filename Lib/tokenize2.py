#
# Advanced tokenizer of python and epl source code.
# This is one big regular expression. The entry function
# of the module is gentokens which is a generator that
# yields tokens (and optionaly the whitespace between).
#
#

Group = '|'.join

Operator = Group ((r'\*\*=?',
	'>>=?',
	'<<=?',
	'<>',
	'!=',
	'//=?',
	r"[~.$?:@,;{}()\[\]]",
	"[-+*/%&|^=<>]=?"
))

# String. The problem is escaped quotes and the fact that
# we want to avoid repetition-on-repetition. For that we
# use a non greedy repetitioner up to the first non escaped
# quote (escaped == quote preceded by odd number of backslash).
# That can't match an empty string and that's the first part
# of the |
QS1 = r"""[RruU]?%s(?:(?:\\\\)*|.*?[^\\](?:\\\\)*)%s""";
String1 = Group ([QS1 % (x,x) for x in ('"', "'")])
String3 = Group ([QS1 % (x,x) for x in ('"""', "'''")])
String = Group ((String3, String1))
del QS1, String1, String3

Symbol = r'[a-zA-Z_]\w*'
Hex = r'0x[\da-zA-Z]+[lL]?'
Oct = r'0[0-7]*[lL]?'
Int = r'[1-9]\d*[lL]?'
E = r'(?:[eE][-+]?\d+)'
Float1 = r'\d+' + E
Float2 = r'(?:\d+\.\d*|\.\d+)' + E + '?'
Comment = r'#[^\n]*\n'

# the order is important
Token = Group ((Float2, Operator, String, Symbol, Hex, Oct, Int, Float1, Comment))

del Symbol, Hex, Oct, Int, E, Float1, Float2, String, Operator, Comment, Group

import re
try:
	Tokenize = re.compile (Token, re.DOTALL, dojit=0).match
except:
	Tokenize = re.compile (Token, re.DOTALL).match
White = re.compile (r'\s*', re.DOTALL).match
del re

def gentokens (t, ws=False, Tokenize=Tokenize, White=White):
	i = 0
	if not ws:
		while 1:
			R = White (t, i)
			if not R:
				break
			R = Tokenize (t, R.end (0))
			if not R:
				break
			yield R.group ()
			i = R.end (0)
	else:
		while 1:
			R = White (t, i)
			if not R:
				break
			yield R.group ()
			R = Tokenize (t, R.end (0))
			if not R:
				break
			yield R.group ()
			i = R.end (0)

class Lexer:
	def __init__ (self, t):
		self.Gnext = gentokens (t, True).next
		self.line = 1
		self.reyield = False
	def nextc (self):
		if self.reyield:
			self.reyield = False
			return self.tok
		while 1:
			tok = self.Gnext ()
			if '\n' in tok:
				self.line += tok.count ('\n')
			tok = self.Gnext ()
			if tok [0] == '#':
				self.line += 1
				continue
			self.tok = tok
			return tok
	def ungetc (self):
		self.reyield = True
	def __iter__ (self):
		while 1:
			yield self.nextc ()

if __name__ == '__main__':
	L = Lexer (open ('rejit/_rejit.pe', 'r').read ())
	while 1:
		print L.nextc(), L.line
