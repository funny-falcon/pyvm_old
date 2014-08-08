
all:
	python Make.py

b:
	python test_bootstrap.py

bootstrap:
	pyvm test_bootstrap.pyc nomarks

optimized:
	# `make optimized`: The pycs are NOT compatible with python
	# If you want to run the compiler with Python,
	# type `make bootstrap` in this directory
	pyvm build.pyc -marshalbuiltin -arch-pyvm

clean:
	python installer.py clean
