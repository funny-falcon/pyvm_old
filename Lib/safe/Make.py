import compileall
import sys
compileall.compile_dir ('..', force='force' in sys.argv)
