
.PHONY: installdeps build format typecheck test

build: installdeps format typecheck test
	poetry build

test: installdeps
	poetry run python -m unittest discover

typecheck: installdeps
	poetry run python -m mypy amp_constraint_solver

format: installdeps
	poetry run python -m black .

installdeps:
	poetry install

clean:
	rm -rf ./**/__pycache__ ./**/.mypy_cache *.egg-info ./**/.pyc ./dist/
