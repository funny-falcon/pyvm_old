all:
	@echo "compiling lwc"
	@cd lwc && make
	@echo "compiling pyvm"
	@cd pyvm && make o3
	@echo "compiling Lib with pyvm/pyc"
	@cd Lib && make bootstrap
	@echo "OK."

cygwin:
	@echo "compiling lwc"
	@cd lwc && make
	@echo "compiling pyvm"
	@cd pyvm && make cygwin
	@echo "compiling Lib with pyvm/pyc"
	@cd Lib && make no-bootstrap
	@echo "OK."

clean:
	@cd Lib && make clean
	@cd Stuff && make clean
	@cd lwc && make distclean
	@cd pyvm && make distclean
	@cd tmp && make clean
	@cd Public && make clean
	@cd Bin && make clean

tar:
	tar cv --exclude-from=.xclude ../toolchain/ > ../Toolchain.tar
	bzip2 -vv ../Toolchain.tar

pyvm-devel:
	make clean
	tar cv --exclude-from=.xclude ../toolchain/ > ../pyvm-devel.tar
	bzip2 -vv ../pyvm-devel.tar

pyvm-lite:
	make clean
	cd lwc && make
	cd pyvm && make cfiles
	tar cv --exclude-from=.xclude-lite ../toolchain/ > ../pyvm-lite.tar
	bzip2 -vv ../pyvm-lite.tar

dist:
	make clean
	tar cv --exclude-from=.dist ../toolchain/ > ../pyvm-toolchain.tar
	bzip2 -vv ../pyvm-toolchain.tar
