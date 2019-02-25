
.PHONY: installdeps build format typecheck test doctest html_docs dist_docs docs

build: installdeps format typecheck test
	poetry build
	make docs

test: unittest doctest typecheck
	true

unittest: installdeps
	poetry run python -m unittest discover

doctest: installdeps
	cd sphinx && poetry run make doctest

typecheck: installdeps
	poetry run python -m mypy amp_constraint_solver

format: installdeps
	poetry run python -m black .

docs: doctest html_docs dist_docs
	true

html_docs: installdeps sphinx
	rm -rf docs/*
	cd sphinx && poetry run make html
	mkdir -p docs
	cp -R sphinx/build/html/* ./docs/
	cp -R sphinx/build/html/\.[a-z]* ./docs/

dist_docs: installdeps sphinx
	cd sphinx && poetry run make epub latexpdf
	cp -R sphinx/build/epub/*.epub ./dist/
	cp -R sphinx/build/latex/*.pdf ./dist/

installdeps:
	poetry develop

clean:
	rm -rf ./**/__pycache__ ./**/.mypy_cache *.egg-info ./**/.pyc ./dist/ ./docs
	cd sphinx && make clean
