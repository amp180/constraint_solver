"""
# Constraint solving using domain reduction.

eg.
```
from amp_constraint_solver import solve

def constraint1(b, **variables):
    return variables['a'] != 5 and b != 3

constraint2 = lambda a, b: a != b

for solution in solve({'a': [1, 5], 'b': [1, 2, 3]}, [constraint1, constraint2]):
   print(solution)
```

* variables: Things that are assigned values in a possible solution.
* values: Possible values for variables in a solution.
* domains: Bags of possible valid values for a variable.
* constraints: Conditions that are used to check if solutions are valid.
"""
from typing import cast as _cast, TypeVar, List, Dict, Set, Callable, Generator
from inspect import getfullargspec as _getfullargspec

## Types
# Type of values being solved for.
ValueType = TypeVar("ValueType")
# Domain of candidate values to select a variable value from.
Domain = List[ValueType,]
# Mapping of variables to domains.
DomainsType = Dict[str, Domain]
# Mapping of variables to values (possible solution).
SolutionsType = Dict[str, ValueType]
# Function that partially checks if a possible solution is valid.
Constraint = Callable[..., bool]
# Type returned by the solve function.
SolutionGenerator = Generator[SolutionsType, None, None]


def _assert_domain(domain: Domain):
    """Function that checks if a list is a valid domain."""
    assert isinstance(domain, list), f"Domain must be a list, not { type(domain) }."
    assert len(domain) == len(
        set(domain)
    ), f"Values in domain should be unique. \n{ domain }"
    assert len(domain) > 0, "Domains cannot be empty."


def _assert_constraint(constraint: Constraint, domains: DomainsType):
    """Function that checks if a constraint is valid."""
    assert callable(constraint), f"Constrints must be callable, {constraint}"
    argspec = _getfullargspec(constraint)
    for arg in argspec.args:
        assert arg in domains.keys(), f"{arg} is not a known variable."


def _check_constraints(variables: SolutionsType, constraints: List[Constraint]) -> bool:
    """Function to check that a list of solution constraint checks are satisfied by a solution."""
    for constraint in constraints:
        # Inspect the function
        argspec = _getfullargspec(constraint)

        # Build a list of positional args that match variable names
        args = (
            [variables[arg] for arg in argspec.args if arg in variables]
            if argspec.args
            else []
        )

        # If the function globs **kwargs, supply all variables not already passed as kwargs.
        all_vars = dict(
            [
                (key, value)
                for key, value in variables.items()
                if key not in argspec.args
            ]
            if argspec.varkw is not None
            else {}
        )

        if len(args) < len(argspec.args):
            # Not all needed variables are assigned a value yet.
            continue

        # Call the constraint and return false only if the check fails.
        if not constraint(*args, **all_vars):
            return False

    return True


def solve(
    domains: DomainsType,
    constraints: List[Constraint] = [],
    *,
    _sorted_variables=None,
    _current_solution: SolutionsType = None,
    _depth: int = 0,
    sorted_function: Callable = sorted,
) -> SolutionGenerator:
    """
        A recursive generator function that yields solutions to a constraint solving problem,
        using domain reduction.
        eg. solve({'a': [1, 2], 'b': [1, 2]}, [lambda a, b: a > b])
    """
    if _current_solution is None:
        _current_solution = dict()

    if _depth == 0:
        # Assert domains are valid.
        assert isinstance(
            domains, Dict
        ), "The domains arg must be a dict of str to list."
        assert len(domains.items()) > 0, "Domains dictionary cannot be empty."
        for domain_to_check in domains.values():
            _assert_domain(domain_to_check)
        # Assert constraints are valid
        for constraint_to_check in constraints:
            _assert_constraint(constraint_to_check, domains)

    if _depth == len(domains):
        # Base case, all variables have been assigned and checked.
        yield _current_solution
        return

    # Recursive case, choose the next variable in order and iterate over all values.
    sorted_variables = _sorted_variables or sorted_function(domains.keys())
    current_var = sorted_variables[_depth]
    current_domain = domains[current_var]

    for value in current_domain:
        # Create a new partial solution and check against constraints.
        current_solution = dict(_current_solution)
        current_solution[current_var] = value
        if _check_constraints(current_solution, constraints):
            # Recurse to the next variable with the new partial solution.
            yield from solve(
                domains,
                constraints,
                _sorted_variables=sorted_variables,
                _current_solution=current_solution,
                _depth=_depth + 1,
            )


def no_duplicate_values_constraint(**variables) -> bool:
    """A function that ensures that values are assigned to only one domain at a time."""
    for var1, value1 in variables.items():
        for var2, value2 in variables.items():
            if var1 != var2:
                if value1 == value2:
                    return False
    return True


def make_vars_not_equal_constraint(var1: str, var2: str):
    """A function that checks if all values are assigned to only one variable at a time."""

    def not_equal(**variables) -> bool:
        f"Ensuring {var1} and {var2} are not equal."
        if all([key in variables for key in (var1, var2)]):
            if variables[var1] == variables[var2]:
                return False
        return True

    return not_equal


def make_vars_not_diagonal_on_grid_constraint(x1: str, y1: str, x2: str, y2: str):
    """Creates a constraint that checks that (x1, y1) is not diagonal with (x2, y2) on a positive grid."""

    def not_diagonal(**variables) -> bool:
        f"Ensure ({x1}, {y1}) is not diagonal with ({x2}, {y2})"
        variables = _cast(Dict[str, int], variables)
        # diagonal on a grid is when abs(x1-x2) == abs(y1-y2)
        if all([key in variables for key in (x1, y1, x2, y2)]):
            diff1 = abs(variables[x1] - variables[x2])
            diff2 = abs(variables[y1] - variables[y2])
            return diff1 != diff2
        else:
            return True

    return not_diagonal
