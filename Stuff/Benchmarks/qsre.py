#DEJAVU
'''
{
'NAME':"Regular Expressions",
'DESC':"Regexp tokenizer of python source (sre vs pcre vs rejit)",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"SEM",
'BARGS':""
}
'''

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
# try to use the JIT
try: Tokenize = re.compile (Token, re.DOTALL, dojit=1).match
except: Tokenize = re.compile (Token, re.DOTALL).match
White = re.compile (r'\s*', re.DOTALL).match
del re

def gentokens (t, ws=False, Tokenize=Tokenize, White=White):
	i = 0
	while 1:
		W = White (t, i)
		if not W:
			break
		i = W.end (0)
		T = Tokenize (t, i)
		if not T:
			break
		yield T.group ()
		i = T.end (0)

if __name__ == '__main__':
	import sys
	t = open ('DATA/epl').read ()
	tu = tuple ([x for x in gentokens (t)])
	print hash (tu)
	if 'SEM' not in sys.argv:
		for i in xrange (100):
			for j in gentokens (t):
				pass
