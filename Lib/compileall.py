#
# compileall, taken from python because we need some adaptions
# to make it take advantage of the pyc compiler
#	copyrights PSF et al.
#
#

import os
import sys
import py_compile

__all__ = ["compile_dir","compile_path"]

def compile_dir(dir, maxlevels=10, ddir=None,
                force=0, rx=None, quiet=0, fork=False, **kw):
	if not quiet:
		print 'Listing', dir, '...'
	try:
		names = os.listdir(dir)
	except os.error:
		print "Can't list", dir
		names = []
	names.sort()
	success = 1
	for name in names:
		fullname = os.path.join(dir, name)
		if ddir is not None:
			dfile = os.path.join(ddir, name)
		else:
			dfile = None
		if rx is not None:
			mo = rx.search(fullname)
			if mo:
				continue
		if os.path.isfile(fullname):
			head, tail = name[:-3], name[-3:]
			if tail == '.py' or tail == '.pe':
				if tail == '.py':
					cfile = fullname + 'c'
				else:
					cfile = fullname [:-1] + 'yc'
				ftime = os.stat(fullname).st_mtime
				try: ctime = os.stat(cfile).st_mtime
				except os.error: ctime = 0
				if (ctime > ftime) and not force: continue
				if not quiet:
					print 'compiling', fullname, '...'
				try:
					ok = py_compile.compile(fullname, None, dfile, True, fork, kw)
				except KeyboardInterrupt:
					raise KeyboardInterrupt
				except py_compile.PyCompileError,err:
					if quiet:
						print 'Compiling', fullname, '...'
					print err.msg
					success = 0
				except IOError, e:
					print "Sorry", e
					success = 0
				else:
					if ok == 0:
						success = 0
		elif maxlevels > 0 and \
             name != os.curdir and name != os.pardir and \
             os.path.isdir(fullname) and \
             not os.path.islink(fullname):
			if not compile_dir(fullname, maxlevels - 1, dfile, force, rx, quiet, fork, **kw):
				success = 0
	return success

def compile_path(skip_curdir=1, maxlevels=0, force=0, quiet=0):
	success = 1
	for dir in sys.path:
		if (not dir or dir == os.curdir) and skip_curdir:
			print 'Skipping current directory'
		else:
			success = success and compile_dir(dir, maxlevels, None,
                                              force, quiet=quiet)
	return success

def main():
	import getopt
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'lfqd:x:')
	except getopt.error, msg:
		print msg
		print "usage: python compileall.py [-l] [-f] [-q] [-d destdir] " \
              "[-x regexp] [directory ...]"
		print "-l: don't recurse down"
		print "-f: force rebuild even if timestamps are up-to-date"
		print "-q: quiet operation"
		print "-d destdir: purported directory name for error messages"
		print "   if no directory arguments, -l sys.path is assumed"
		print "-x regexp: skip files matching the regular expression regexp"
		print "   the regexp is search for in the full path of the file"
		sys.exit(2)
	maxlevels = 10
	ddir = None
	force = 0
	quiet = 0
	rx = None
	for o, a in opts:
		if o == '-l': maxlevels = 0
		if o == '-d': ddir = a
		if o == '-f': force = 1
		if o == '-q': quiet = 1
		if o == '-x':
			import re
			rx = re.compile(a)
	if ddir:
		if len(args) != 1:
			print "-d destdir require exactly one directory argument"
			sys.exit(2)
	success = 1
	try:
		if args:
			for dir in args:
				if not compile_dir(dir, maxlevels, ddir,
                                   force, rx, quiet):
					success = 0
		else:
			success = compile_path()
	except KeyboardInterrupt:
		print "\n[interrupt]"
		success = 0
	return success

if __name__ == '__main__':
	exit_status = int(not main())
	sys.exit(exit_status)
