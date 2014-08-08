# crc16.py by Bryan G. Olson, 2005
# This module is free software and may be used and
# distributed under the same terms as Python itself.
#

"""
    CRC-16 in Python, as standard as possible. This is
    the 'reflected' version, which is usually what people
    want. See Ross N. Williams' /A Painless Guide to
    CRC error detection algorithms/.
"""

#DEJAVU
'''
{
'NAME':"CRC16",
'DESC':"Python implementation of CRC-16 by Bryan Olson",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"SEM",
'BARGS':"838"
}
'''

from array import array

import sys
TRY_JIT = False
if sys.copyright.startswith ('pyvm') and TRY_JIT:
    #
    # try cjit.	100 times faster :)
    # candidate for inclusion in the standard library?
    #
	import _JIT as DLL
	import os
	PROGRAM = r"""
		unsigned int crc16 (unsigned short *tbl, unsigned char *str, unsigned int val)
		{
			while (*str)
				val = tbl [*str++ ^ (val & 0xff)] ^ (val >> 8);
			return val;
		}
"""

	LibNo = xrange (1000000).next

	def MakeLib (PROGRAM):
	    file ('tmpfile.c', 'w+').write (PROGRAM)
	    libno = LibNo ()
	    os.system ('gcc -fpic -O3 -shared tmpfile.c -o mylib%i.so' % libno)
	    mylib = DLL.dllopen ('./mylib%i.so' %libno)
	    os.unlink ('./mylib%i.so'%libno)
	    return mylib

	mylib = MakeLib (PROGRAM)
	_crc16 = mylib.get (('i', 'crc16', 'p16si'))
	def crc16(string, value=0):
	    return _crc16 (Htable, string, value)
else:


 def crc16(string, value=0):
    """ Single-function interface, like gzip module's crc32
    """
    for ch in string:
        value = table[ord(ch) ^ (value & 0xff)] ^ (value >> 8)
    return value

class CRC16(object):
    """ Class interface, like the Python library's cryptographic
        hash functions (which CRC's are definitely not.)
    """

    def __init__(self, string=''):
        self.val = 0
        if string:
            self.update(string)

    def update(self, string):
        self.val = crc16(string, self.val)

    def checksum(self):
        return chr(self.val >> 8) + chr(self.val & 0xff)

    def hexchecksum(self):
        return '%04x' % self.val

    def copy(self):
        clone = CRC16()
        clone.val = self.val
        return clone

# CRC-16 poly: p(x) = x**16 + x**15 + x**2 + 1
# top bit implicit, reflected
def mktable ():
    poly = 0xa001
    table = []
    for byte in range(256):
        crc = 0
        for bit in range(8):
            if (byte ^ crc) & 1:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            byte >>= 1
        table.append(crc)
    return table

table = tuple (mktable ())
Htable = array ('H', table)

def test ():
    from binascii import hexlify
    crc = CRC16()
    crc.update("123456789")
    print hexlify (crc.checksum ())
    assert crc.checksum() == '\xbb\x3d'

def bench (N):
    from binascii import hexlify
    from time import time
    crc = CRC16 ()
    data = file ('CRC16.py').read ()
    t0 = time()
    for i in xrange (N):
	crc.update (data)
    print time()-t0, hexlify (crc.checksum ())

if 'SEM' in sys.argv:
    test ()
else:
    bench (int (sys.argv [1]))
