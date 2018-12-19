
.PHONY: build format typecheck test

build: typecheck test 
	poetry build

test:
	poetry run python -m unittest discover

typecheck:
	poetry run python -m mypy constraint_solver

format:
	poetry run python -m black .

clean:
	rm -rf ./**/__pycache__ ./**/.mypy_cache *.egg-info ./**/.pyc ./dist/
