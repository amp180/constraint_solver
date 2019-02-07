
.PHONY: installdeps build format typecheck test

build: installdeps format typecheck test
	poetry build
	make docs

test: installdeps
	poetry run python -m unittest discover

typecheck: installdeps
	poetry run python -m mypy amp_constraint_solver

format: installdeps
	poetry run python -m black .

docs: installdeps sphinx
	rm -rf docs/*
	cd sphinx && make clean 
	cd sphinx && make doctest
	cd sphinx && make html
	mkdir -p docs
	cp -R sphinx/build/html/* ./docs/
	cp -R sphinx/build/html/\.[a-z]* ./docs/

installdeps:
	poetry install

clean:
	rm -rf ./**/__pycache__ ./**/.mypy_cache *.egg-info ./**/.pyc ./dist/ ./docs
	cd sphinx && make clean
