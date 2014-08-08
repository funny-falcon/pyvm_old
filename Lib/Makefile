
all:
	pyvm Make.pyc

# Produces incompatible bytecode: builtins are marshalled
# and the pycs are optimized for size with 'global names tuple', etc.
# This saves about 15%.
bootstrap:
	@echo
	@echo "Bootstrap (incompatible bytecode)..."
	tar xf img.tar
	pyvm Make.pyc force fork
	@cd pyc && make optimized

# Produces bytecode which is compatible with Python 2.4 and
# can be executed with it. This should be preferred for development
# because running the pycs with Python can be used to find bugs
# in pyvm
bootstrap-compat:
	@echo
	@echo "Bootstrap..."
	tar xf img.tar
	pyvm Make.pyc force

no-bootstrap:
	@echo
	@echo "Bootstrap with python..."
	tar xf img.tar
	cd pyc && python test_bootstrap.py
	pyvm Make.py

image:
	rm -f pyc/indent.pyc pyc/installer.pyc pyc/ptest.pyc pyc/test_libsize.pyc pyc/build.pyc
	tar c pyc/*.pyc re.pyc itertools.pyc Make.pyc posix.pyc compileall.pyc py_compile.pyc DLL.pyc operator.pyc types.pyc > img.tar

clean:
	find . -name \*.pyc | xargs rm -f
	find . -name \*.so | xargs rm -f
	cd pyc && make clean
	cd rejit && make clean
