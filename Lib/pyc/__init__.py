"""
compile(source, filename, mode, flags=None, dont_inherit=Nonei, assignexpr=False)
    Returns a code object.  A replacement for the builtin compile() function.

compileFile(filename)
    Generates a .pyc file by compiling filename. Returns the full pathname of the pyc.

eval_ast (source)
     same as 'eval (source)', but the code is executed on the AST.
"""

from root import compile, compileFile, eval_ast, compileFile_internal
