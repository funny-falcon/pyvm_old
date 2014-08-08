#!/usr/bin/env python

import sys
import os
import time

print '########## bytecompiling tests ##########'

RUNPYCS = '-nocompile' not in sys.argv

if not RUNPYCS:
    pass
elif '-pyc' in sys.argv:
    import pyc
    for i in sorted (os.listdir ('.')):
        if i.endswith ('.py'):
	    print i, ':',
  	    pyc.compileFile (i, showmarks=1, dynlocals=False, rrot3=1) 
	    print 
else:
    import compileall
    compileall.compile_dir ('.')

if sys.argv [0][-4:] == 'Make':
    sys.exit ()

def readparams(f):
    FL = iter (file (f))
    for x in FL:
	if x.startswith("#DEJAVU"):
	    desc = ''
	    FL.next ()
	    for x in FL:
		if x.startswith ("'''"):
		    break
		desc += x
	    break
    else:
	print "No DESCRIPTION for", f
	return
    return eval (desc)

print '########### reading specs ##############'

PROG1="python"
PROG2="./pyvm"
PROG2="pyvm"

def semtest (t):
    if RUNPYCS: pyc = t + 'c'
    else: pyc = t
    cmd = '%s %s %s > py.out' % (PROG1, pyc, SPECS[t]['ARGS'])
    print '+++++++++Running:', cmd
    os.system (cmd)
    cmd = '%s %s %s > pyvm.out' % (PROG2, pyc, SPECS[t]['ARGS'])
    print '+++++++++Running:', cmd
    os.system (cmd)
    print '+++++++++Comparing...',
    if os.system ('diff -u py.out pyvm.out > /dev/null'):
	print "***** TEST %s FAILED *****" % t
	raise SystemExit (1)
    print " Ok"

def benchmark (cmd):
    t1 = time.time()
    os.system (cmd)
    t1 = time.time() - t1
    print "* %.5f" % t1
    return t1

RUNS=2
T1TOTAL=0
T2TOTAL=0

def benchtest(t):
    global T1TOTAL, T2TOTAL
    if RUNPYCS: pyc = t + 'c'
    else: pyc = t
    cmd = '%s %s %s > py.out' % (PROG1, pyc, SPECS[t]['BARGS'])
    T1 = min ([ benchmark (cmd) for i in range(RUNS) ])
    T1TOTAL += T1
    cmd = '%s %s %s > pyvm.out' % (PROG2, pyc, SPECS[t]['BARGS'])
    T2 = min ([ benchmark (cmd) for i in range(RUNS) ])
    T2TOTAL += T2
    MSG = "%s:%.4f %s:%.4f\t  --> %.2f%%" % (PROG1, T1, PROG2, T2, 100.0*T2/T1)
    print "%s\t: %.4fs \n%s\t: %.4fs  --> %.2f%%" % (PROG1, T1, PROG2, T2, 100.0*T2/T1)
    return MSG, 100.0 * T2 / T1, T1, T2

TESTS= [
 "Eratosthenes.py",
 "ackermann.py",
 "fibo.py",
 "harmonic.py",
 "object.py",
 "ometh.py",
 "pystone.py",
 "ran.py",
 "takfp.py",
 "nccstrip.py",
 "thpystone.py",
 "gengraph.py",
 "statistics.py",
 "wc.py",
 "linalg_brute.py",
 "wordfreq.py",

# More
 "anagram.py",
 "AllAnagrams.py",
 "divisors.py",
 "fannk.py",
 "nbody.py",
 "hamming.py",
 "robotpy.py",
 "markov.py",

# second wave
 "quicksort.py",
 "permsign.py",
 "bellman_ford.py",
 "floodFill.py",
 "zipcode.py",
 "pirate.py",
 "dictx.py",

# third wave
 "convexhull.py",
 "sudoku.py",
 "fbench.py",
 "zipmap.py",
 "bintree.py",
 "super.py",
 "richards.py",
 "bpnn.py",
 "CRC16.py",
 "jspy1.py",

# fourth wave
 "queens.py",
 "except.py", 
 "bwt.py",
 "nprpuzzle.py",
 "startup.py",
 "obfuscated-quine.py",
 "phash.py",
 "fannkuchen.py",
 "XML.py",
 "markdown.py",

# fifth
 "mandel.py",
 "p117.py",
 "qsre.py",
 "fact.py",
 "markov2.py",
 "primes.py",
 "Queens2.py",
 "5x5.py",

# sixth
 "chess.py",
 "life.py",
 "linalg.py",
 "voronoi.py",
]

SPECS={}

for i in TESTS:
    SPECS[i] = readparams (i)

print len (TESTS), "tests"

for i in [ i for i in TESTS if 'DATA' in SPECS [i] and os.access (SPECS [i]['DATA'], os.R_OK) == 0 ]:
    print "Removing", i, ". No datafile"
    TESTS.remove (i)

############### parse cmdline ############

BENCH= '-check' not in sys.argv
DESCR= '-descr' in sys.argv
RANDO= '-random' in sys.argv
for i in sys.argv:
    if i.startswith ('-nr='):
	RUNS = int (i [4:])
UTESTS = [ i for i in sys.argv [1:] if i [0] != '-' ]
if UTESTS != []:
    for i in UTESTS:
	if i not in TESTS:
	    print "No such testcase", i
	    raise "Error"
    TESTS = UTESTS
    print "Will run", len (TESTS), "of them"

if BENCH:
    print '######### Running semantic and benchmark tests #########'
else:
    print '######### Running semantics tests only #########'

RESULTS = []

T0=time.time()
for i in TESTS:
    print SPECS [i]['NAME'] + '(' + i + '):'
    if BENCH:
        MSG = benchtest (i)
        RESULTS.append  (('* '+ SPECS [i]['NAME'] + '/\n\t' + MSG [0], MSG [1], MSG [2], MSG [3]))
    if SPECS[i]['CMPOUT']:
        semtest (i)
T0=time.time()-T0

if BENCH:
    print "Summary:"
    avg = 0
    for i in RESULTS:
        print i [0]
	avg += 100.0 * i[3] / i [2]
    avg /= len (RESULTS)
    sum=0.0
    print
    print "Total of bests:"
    print "%s \t\t %.4fs" % (PROG1, T1TOTAL)
    print "%s \t\t %.4fs\t-->   %.2f%% %.2f%%" % (PROG2, T2TOTAL, float(T2TOTAL) * 100.0 / T1TOTAL, avg)
    print "Total time %im%.1fs" % (int (T0)/60, T0 % 60) 
    print "Thank You."

if DESCR:
    print "\n\nTestsuite Descriptions"
    print "------------------------"
    for i in TESTS:
	print SPECS[i]['NAME'] + ':'
	print '  ' + SPECS[i]['DESC'], '\n'

################## cleanup ##################

print 'rm *.out'
os.system ("rm *.out *.pyc")
