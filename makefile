.PHONY: all test

all:
	python main.py

test:
	python -m unittest discover -v
