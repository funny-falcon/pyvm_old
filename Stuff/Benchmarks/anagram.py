
#DEJAVU
'''
{
'NAME':"Anagram",
'DESC':"simple anagram",
'GROUP':'real-bench',
'DATA':'/usr/share/dict/words',
'CMPOUT':1,
'ARGS':"1 stop step statement",
'BARGS':"6 stop step words lots pool eat fast slow cold door planet statement triangle coolness parse"
}
'''

import sys

if 0:
 WORDS = []
 for i in file ('/usr/share/dict/words'):
    i = i.rstrip
    WORDS.append (i ())
else:   
 WORDS = [ i.rstrip ().lower () for i in file ('/usr/share/dict/words') ]

def findana (anagram):
    sorted_anagram = sorted(anagram.lower())
    len_anagram = len (anagram)
    found = [ word for word in WORDS if len(word)==len_anagram and sorted(word)==sorted_anagram ]
    print "Anagrams of %s: %s" % (anagram, ' '.join(found))

for t in range(int (sys.argv [1])):
 for i in sys.argv [2:]:
    findana (i)
