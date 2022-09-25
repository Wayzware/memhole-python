all: c-code python-code local-install 

all-upload: clean all upload-test
	
local-clean: 
	rm -rf ~/.local/lib/python3.10/site-packages/memhole*

local-install:
	python3 -m pip install $(shell find memhole/dist -name "*.tar.gz")

upload-test:
	echo "Uploading to PyPI-Test"
	cd memhole; python3 -m build
	cd memhole; python3 -m twine upload --repository testpypi dist/*

upload-release:
	cd memhole; python3 -m build
	cd memhole; python3 -m twine upload --repository pypi dist/*

c-code:
	gcc -fPIC -shared -o memhole/memhole/memhole_lib.so csrc/memhole.c

python-code:
	rm memhole/dist/*
	cd memhole; hatch build

clean:
	rm -f memhole/memhole/memhole_lib.so