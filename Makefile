init:
	python -m venv ./venv

install:
	pip install -r requirements.txt

test:
	python -m pytest	

run:
	./venv/bin/python ./translation_god/main.py

clean:
	rm ./translation_god/*.xlsx

build:
	python3 -m build

publish:
	python3 -m twine upload --repository pypi dist/*


.PHONY: init active install test
