#
# Build pyc
#

import root
import sys

from time import time

def compileFile (fnm, **kwargs):
    print 'Compiling %s...'%fnm,
    root.compileFile (fnm, **kwargs)
    print

SHOW=0
if 'nomarks' in sys.argv:
    SHOW=0
RROT3=1
MARSHAL_BUILTIN='-marshalbuiltin' in sys.argv
if '-arch-pyvm' not in sys.argv:
	ARCH=None
else:
	ARCH='pyvm'

MARSHAL_BUILTIN=0
t0=time()
compileFile ('arch24.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	 arch=ARCH)
compileFile ('consts.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	 arch=ARCH)
compileFile ('visitor.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	arch=ARCH)
compileFile ('parser.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, constfiles=['parserconsts.py'],
		 marshal_builtin=MARSHAL_BUILTIN, arch=ARCH)
compileFile ('pyassem.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, constfiles=['consts.py'],
	 marshal_builtin=MARSHAL_BUILTIN, arch=ARCH)
compileFile ('pycodegen.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, constfiles=['consts.py'],
	 marshal_builtin=MARSHAL_BUILTIN, arch=ARCH)
compileFile ('pyc.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	arch=ARCH)
compileFile ('symbols.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, constfiles=['consts.py'],
	 marshal_builtin=MARSHAL_BUILTIN, arch=ARCH)
compileFile ('misc.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	arch=ARCH)
compileFile ('optimizer.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3,
	 marshal_builtin=MARSHAL_BUILTIN, arch=ARCH)
compileFile ('transform.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	arch=ARCH)
compileFile ('ast.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	arch=ARCH)
compileFile ('__init__.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3,
	 marshal_builtin=MARSHAL_BUILTIN, arch=ARCH)
compileFile ('root.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	arch=ARCH)
compileFile ('gco.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	arch=ARCH)
compileFile ('JITS.py', dynlocals=0, showmarks=SHOW, rrot3=RROT3, marshal_builtin=MARSHAL_BUILTIN,
	arch=ARCH)
print time()-t0
