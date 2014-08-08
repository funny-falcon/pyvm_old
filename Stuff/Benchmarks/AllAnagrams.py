

import sys

#DEJAVU
'''
{
'NAME':"All-anagrams",
'DESC':"Scott David Daniel's program to find all anagrams in a text",
'GROUP':'real-bench',
'DATA':'/usr/share/dict/words',
'CMPOUT':1,
'ARGS':"1 /usr/share/dict/words",
'BARGS':"3 /usr/share/dict/words"
}
'''


def words(source):
    for line in source:
        for word in line.split():
            yield word


def all_anagrams(words):
    seen = {}

    for word in words:
        word = word.lower()

        if word not in seen:
            dorw = ''.join(sorted(word))
            try:
                seen[dorw].append(word)
            except KeyError:
                seen[dorw] = [word]
                if word == dorw:
                    continue
            seen[word] = ()

    for group in seen.itervalues():
        if len(group) > 1:
            yield -len(group), sorted(group) # conveniently sortable

def main(sources):
    for filename in sources:
        dictionary = open(filename, 'r')
        print "All anagrams from %s:" % filename
        try:
            for nsize, group in sorted ([i for i in all_anagrams(words(dictionary))]):
                print '%2i: %s' % (-nsize, ' = '.join(group))
        finally:
            dictionary.close()
            print



if __name__ == '__main__':
    import sys
    for i in range (int (sys.argv [1])):
        main(sys.argv[2:] or ['anagrams.py'])
