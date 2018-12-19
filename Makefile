
.PHONY: install build format typecheck test

install: build
	poetry install

build: format typecheck test
	poetry build

test:
	poetry run python -m unittest discover

typecheck:
	poetry run python -m mypy constraint_solver

format:
	poetry run python -m black .

clean:
	rm -rf ./**/__pycache__ ./**/.mypy_cache *.egg-info ./**/.pyc ./dist/
