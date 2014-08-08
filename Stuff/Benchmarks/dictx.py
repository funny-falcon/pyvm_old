import sys, time, random
random.seed (123);

import sys


#DEJAVU
'''
{
'NAME':"In-Try-Get-HasKey",
'DESC':"""Great test from Florian Bosch (http://pyalot.blogspot.com) which proves that
 'in' is the fastest and 'try' the slowest (in CPython at least!)""",
'GROUP':'real-bench',
'CMPOUT':0,
'ARGS':"#unused#",
'BARGS':"1234"
}
'''


def random_key( keylen = 10 ):
    return ''.join([chr(random.randint(ord('a'),ord('z'))) for _ in range( keylen )])

def new_key( existing_keys ):
    key = random_key()
    while key in existing_keys:
        key = random_key()
    return key

def unique_keys( amount=1000, existing_keys=set() ):
    keys = set( existing_keys )
    for _ in xrange( amount ):
        key = new_key( keys )
        keys.add( key )
    return keys-existing_keys

def data( dictionary_size=1000, search_size=3000, intersection=0.5 ):
    dict_keys = unique_keys( dictionary_size )
    intersection_amount = int(search_size*intersection)
    unique_search_keys = unique_keys( search_size-intersection_amount, dict_keys )
    intersection_search_keys = set(list(dict_keys)[0:intersection_amount])
    return dict([(key,None) for key in dict_keys]), unique_search_keys | intersection_search_keys


def core_test( out_prefix, dictionary, searched, test_functions ):
    print out_prefix
    for function in test_functions:
        start = time.time()
        for _ in range( 20*(len(dictionary)/len(searched) or 1) ):
            function( dictionary, searched, None )
        end = time.time()
        print '\t%s \t%2.4f'%(function.__name__, end-start)

def inner_test( out_prefix, dictionary_size, search_size, test_functions ):
    #small intersection
    dictionary, search = data( dictionary_size, search_size, 0.1 )
    core_test( '%s, small intersect'%out_prefix, dictionary, search, test_functions )
    #half intersection
    dictionary, search = data( dictionary_size, search_size, 0.5 )
    core_test( '%s, half intersect'%out_prefix, dictionary, search, test_functions )
    #big intersection
    dictionary, search = data( dictionary_size, search_size, 0.9 )
    core_test( '%s, big intersect'%out_prefix, dictionary, search, test_functions )


#test functions
def test_has_key( dictionary, searched, default ):
    for key in searched:
        if dictionary.has_key( key ):
            value = dictionary[key]
        else:
            value = default

def test_has_key_cached( dictionary, searched, default ):
    has_key = dictionary.has_key
    for key in searched:
        if has_key( key ):
            value = dictionary[key]
        else:
            value = default

def test_get( dictionary, searched, default ):
    for key in searched:
        value = dictionary.get(key, default)

def test_get_cached( dictionary, searched, default ):
    get = dictionary.get
    for key in searched:
        value = get(key, default)

def test_try( dictionary, searched, default ):
    KeyError_cache = KeyError
    for key in searched:
        try:
            value = dictionary[key]
        except KeyError_cache:
            value = default

def test_in( dictionary, searched, default ):
    for key in searched:
        if key in dictionary:
            value = dictionary[key]
        else:
            value = default

def test():
    factor = 1
    N1000 = int (sys.argv [1])

    test_functions = [test_has_key, test_get, test_try, test_in, test_get_cached, test_has_key_cached]
    #big dict, small search, small
    inner_test( 'big dict, small search', N1000*factor, 1*factor, test_functions )

    #even dict/search
    inner_test( 'even', N1000*factor, N1000*factor, test_functions )

    #small dict, big search
    inner_test( 'small dict, big search', 1*factor, N1000*factor, test_functions )

if __name__ == '__main__':
    test()
