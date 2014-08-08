#! /usr/bin/env python
#
# ATTENTION.  threaded pystone does not report its pystones/second at all
# It is meant to be tested with 'time python thpystone.py'
# There seems to be a bug in python's libraries and time does not work
# with threads ?!?!
#

"""
"PYSTONE" Benchmark Program

Version:        Python/1.1 (corresponds to C/1.1 plus 2 Pystone fixes)

Author:         Reinhold P. Weicker,  CACM Vol 27, No 10, 10/84 pg. 1013.

                Translated from ADA to C by Rick Richardson.
                Every method to preserve ADA-likeness has been used,
                at the expense of C-ness.

                Translated from C to Python by Guido van Rossum.

Version History:

                Version 1.1 corrects two bugs in version 1.0:

                First, it leaked memory: in Proc1(), NextRecord ends
                up having a pointer to itself.  I have corrected this
                by zapping NextRecord.PtrComp at the end of Proc1().

                Second, Proc3() used the operator != to compare a
                record to None.  This is rather inefficient and not
                true to the intention of the original benchmark (where
                a pointer comparison to None is intended; the !=
                operator attempts to find a method __cmp__ to do value
                comparison of the record).  Version 1.1 runs 5-10
                percent faster than version 1.0, so benchmark figures
                of different versions can't be compared directly.

"""

#DEJAVU
'''
{
'NAME':"threaded pystone",
'DESC':"threaded pystone benchmark - 60 threads pystoning",
'GROUP':'real-bench',
'CMPOUT':0,
'ARGS':"",
'BARGS':""
}
'''


import sys
if not sys.copyright.startswith ('pyvm'):
    import gc
    gc.disable()

LOOPS = 1000
THREADS = 13

import thread
import time
#from time import time.clock

__version__ = "1.1"

[Ident1, Ident2, Ident3, Ident4, Ident5] = range(1, 6)

class Record:

    def __init__(self, PtrComp = None, Discr = 0, EnumComp = 0,
                       IntComp = 0, StringComp = 0):
        self.PtrComp = PtrComp
        self.Discr = Discr
        self.EnumComp = EnumComp
        self.IntComp = IntComp
        self.StringComp = StringComp

    def copy(self):
        return Record(self.PtrComp, self.Discr, self.EnumComp,
                      self.IntComp, self.StringComp)

TRUE = 1
FALSE = 0

def main(loops=LOOPS, threads=THREADS):
    benchtime, stones = pystones(loops, threads)
    print "ThrPystone(", __version__, ") time for ", loops, " passes on ", threads, "threads = ", benchtime
    print "This machine benchmarks at ", stones, " pystones/second"


L = thread.allocate_lock ()

COUNTDOWN = 0;

def pystones(loops=LOOPS, threads=THREADS):
    starttime = time.clock()
    for i in range(loops):
        pass
    nulltime = time.clock() - starttime

    L.acquire()
    thrd = [ PyStoner(i) for i in range (threads) ]
    global COUNTDOWN
    COUNTDOWN = threads
    starttime = time.clock()
    for i in thrd:
	thread.start_new_thread (i.Proc0, (loops,))
    L.acquire()
    benchtime = time.clock() - starttime - nulltime
    return benchtime, (loops, benchtime)

Array1Glob = [0]*51
Array2Glob = map(lambda x: x[:], [Array1Glob]*51)

class PyStoner:
    def __init__ (self, ID):
	global Array1Glob
	global Array2Glob
	self.ID = ID
	self.IntGlob = 0
	self.BoolGlob = FALSE
	self.Char1Glob = '\0'
	self.Char2Glob = '\0'
	self.Array1Glob = Array1Glob [:]
	self.Array2Glob = Array2Glob [:]
	self.PtrGlb = None
	self.PtrGlbNext = None

    def Proc0(self, loops=LOOPS):

	global COUNTDOWN
        self.PtrGlbNext = Record()
        self.PtrGlb = Record()
        self.PtrGlb.PtrComp = self.PtrGlbNext
        self.PtrGlb.Discr = Ident1
        self.PtrGlb.EnumComp = Ident3
        self.PtrGlb.IntComp = 40
        self.PtrGlb.StringComp = "DHRYSTONE PROGRAM, SOME STRING"
        String1Loc = "DHRYSTONE PROGRAM, 1'ST STRING"
        self.Array2Glob[8][7] = 10

        for i in range(loops):
            self.Proc5()
            self.Proc4()
            IntLoc1 = 2
            IntLoc2 = 3
            String2Loc = "DHRYSTONE PROGRAM, 2'ND STRING"
            EnumLoc = Ident2
            self.BoolGlob = not Func2(String1Loc, String2Loc)
            while IntLoc1 < IntLoc2:
                IntLoc3 = 5 * IntLoc1 - IntLoc2
                IntLoc3 = self.Proc7(IntLoc1, IntLoc2)
                IntLoc1 = IntLoc1 + 1
            self.Proc8(self.Array1Glob, self.Array2Glob, IntLoc1, IntLoc3)
            self.PtrGlb = self.Proc1(self.PtrGlb)
            CharIndex = 'A'
            while CharIndex <= self.Char2Glob:
                if EnumLoc == Func1(CharIndex, 'C'):
                    EnumLoc = self.Proc6(Ident1)
                CharIndex = chr(ord(CharIndex)+1)
            IntLoc3 = IntLoc2 * IntLoc1
            IntLoc2 = IntLoc3 / IntLoc1
            IntLoc2 = 7 * (IntLoc3 - IntLoc2) - IntLoc1
            IntLoc1 = self.Proc2(IntLoc1)
        COUNTDOWN = COUNTDOWN - 1
	if COUNTDOWN <= 0:
	    L.release ()


    def Proc1(self, PtrParIn):
        PtrParIn.PtrComp = NextRecord = self.PtrGlb.copy()
        PtrParIn.IntComp = 5
        NextRecord.IntComp = PtrParIn.IntComp
        NextRecord.PtrComp = PtrParIn.PtrComp
        NextRecord.PtrComp = self.Proc3(NextRecord.PtrComp)
        if NextRecord.Discr == Ident1:
            NextRecord.IntComp = 6
            NextRecord.EnumComp = self.Proc6(PtrParIn.EnumComp)
            NextRecord.PtrComp = self.PtrGlb.PtrComp
            NextRecord.IntComp = self.Proc7(NextRecord.IntComp, 10)
        else:
	    print 'Branch never taken'
            PtrParIn = NextRecord.copy()
        NextRecord.PtrComp = None
        return PtrParIn

    def Proc2(self, IntParIO):
        IntLoc = IntParIO + 10
        while 1:
            if self.Char1Glob == 'A':
                IntLoc = IntLoc - 1
                IntParIO = IntLoc - self.IntGlob
                EnumLoc = Ident1
            if EnumLoc == Ident1:
                break
        return IntParIO

    def Proc3(self, PtrParOut):
        if self.PtrGlb is not None:
            PtrParOut = self.PtrGlb.PtrComp
        else:
            self.IntGlob = 100
        self.PtrGlb.IntComp = self.Proc7(10, self.IntGlob)
        return PtrParOut

    def Proc4(self):
        BoolLoc = self.Char1Glob == 'A'
        BoolLoc = BoolLoc or self.BoolGlob
        self.Char2Glob = 'B'

    def Proc5(self):
        self.Char1Glob = 'A'
        self.BoolGlob = FALSE

    def Proc6(self, EnumParIn):
        EnumParOut = EnumParIn
        if not Func3(EnumParIn):
            EnumParOut = Ident4
        if EnumParIn == Ident1:
            EnumParOut = Ident1
        elif EnumParIn == Ident2:
            if self.IntGlob > 100:
                EnumParOut = Ident1
            else:
                EnumParOut = Ident4
        elif EnumParIn == Ident3:
            EnumParOut = Ident2
        elif EnumParIn == Ident4:
            pass
        elif EnumParIn == Ident5:
            EnumParOut = Ident3
        return EnumParOut

    def Proc7(self,IntParI1, IntParI2):
        IntLoc = IntParI1 + 2
        IntParOut = IntParI2 + IntLoc
        return IntParOut

    def Proc8(self, Array1Par, Array2Par, IntParI1, IntParI2):
        IntLoc = IntParI1 + 5
        Array1Par[IntLoc] = IntParI2
        Array1Par[IntLoc+1] = Array1Par[IntLoc]
        Array1Par[IntLoc+30] = IntLoc
        for IntIndex in range(IntLoc, IntLoc+2):
            Array2Par[IntLoc][IntIndex] = IntLoc
        Array2Par[IntLoc][IntLoc-1] = Array2Par[IntLoc][IntLoc-1] + 1
        Array2Par[IntLoc+20][IntLoc] = Array1Par[IntLoc]
        self.IntGlob = 5

def Func1(CharPar1, CharPar2):
    CharLoc1 = CharPar1
    CharLoc2 = CharLoc1
    if CharLoc2 != CharPar2:
        return Ident1
    else:
        return Ident2

def Func2(StrParI1, StrParI2):
    IntLoc = 1
    while IntLoc <= 1:
        if Func1(StrParI1[IntLoc], StrParI2[IntLoc+1]) == Ident1:
            CharLoc = 'A'
            IntLoc = IntLoc + 1
    if CharLoc >= 'W' and CharLoc <= 'Z':
        IntLoc = 7
    if CharLoc == 'X':
        return TRUE
    else:
        if StrParI1 > StrParI2:
            IntLoc = IntLoc + 7
            return TRUE
        else:
            return FALSE

def Func3(EnumParIn):
    EnumLoc = EnumParIn
    if EnumLoc == Ident3: return TRUE
    return FALSE

if __name__ == '__main__':
    import sys
    def error(msg):
        print >>sys.stderr, msg,
        print >>sys.stderr, "usage: ", sys.argv [0], " [number_of_loops]" 
        sys.exit(100)
    nargs = len(sys.argv) - 1
    if nargs > 1:
        error(" arguments are too many;")
    elif nargs == 1:
        try: loops = int(sys.argv[1])
        except ValueError:
            error("Invalid argument " + sys.argv[1])
    else:
        loops = LOOPS
    main(loops)
