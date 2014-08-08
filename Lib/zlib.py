#
# wrap zlib with the DLL module
#

from array import array

if 1:
	#
	# zlib from our internally linked libz.a
	#
	from _JIT import fptr_wrapper
	import _zlibfuncs
	_adler32 = fptr_wrapper ('i', _zlibfuncs.adler32, 'isi')
	_crc32 = fptr_wrapper ('i', _zlibfuncs.crc32, 'isi')
	compress2 = fptr_wrapper ('i', _zlibfuncs.compress2, 'sp32sii', True)
	uncompress = fptr_wrapper ('i', _zlibfuncs.uncompress, 'sp32si', True)
	del fptr_wrapper, _zlibfuncs
else:
	import DLL
	#
	# zlib ABI from system's libz.so
	#
	Zlib = DLL.dllopen ('libz.so')

	def DF (name, spec, ret='', blocking=False, iname=''):
	    globals() [iname or name] = Zlib.get ((ret, name, spec), blocking)

	DF ('adler32', 'isi', 'i', iname='_adler32')
	DF ('crc32', 'isi', 'i', iname='_crc32')
	DF ('compress2', 'sp32sii', 'i', blocking=True)
	DF ('uncompress', 'sp32si', 'i', blocking=True)
	del DLL, DF

Z_BUF_ERROR = -5

#
#

def alder32 (string, value=0):
    return _adler32 (value, string, len (string))

def crc32 (string, value=0):
    return _crc32 (value, string, len (string))

def compress (string, level=6):
    sl = l = len (string)
    deststr = ' ' * l
    destlen = array ('i', [l])
    while 1:
	rez = compress2 (deststr, destlen, string, sl, level)
	if rez == Z_BUF_ERROR:
	    l *= 2
	    deststr = ' ' * l
	    destlen = array ('i', [l])
	    continue
	if rez:
	    raise error
	break
    return deststr [:destlen [0]]

def decompress (string, wbits=None, bufsize=None):
    sl = len (string)
    l = sl * 4
    deststr = ' ' * l
    destlen = array ('i', [l])
    while 1:
	rez = uncompress (deststr, destlen, string, sl)
	if rez == Z_BUF_ERROR:
	    l += sl
	    deststr = ' ' * l
	    destlen = array ('i', [l])
	    continue
	if rez:
	    raise error
	break
    return deststr [:destlen [0]]
