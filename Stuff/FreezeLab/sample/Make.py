import compileall
compileall.compile_dir ('.', fork=True, force=True, docstrings=False, asserts=False)
