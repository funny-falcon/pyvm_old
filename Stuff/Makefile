
all:
	pyvm ../Lib/Make.pyc
	@echo "Ready."

clean:
	find . -name \*.pyc | xargs rm -f
	find . -name \*.so | xargs rm -f
	(cd wiki/example && make clean)
