import compileall
import sys
if 'fork' in sys.argv and 'pyvm' in sys.copyright:
	compileall.compile_dir ('.', force='force' in sys.argv, fork=True)
else:
	compileall.compile_dir ('.', force='force' in sys.argv)
