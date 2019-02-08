"""
Contains implementation of a domain reduction constraint resolver.

Usage of :py:func:`solve`:

>>> from amp_constraint_solver import solve 
>>> def constraint1(b, **variables):
...     return variables['a'] != 5 and b != 3
... 
>>> constraint2 = lambda a, b: a == b 
>>> for solution in solve({'a': [1, 5], 'b': [1, 2, 3]}, [constraint1, constraint2]):
...    print(solution)
... 
{'a': 1, 'b': 1}

Glossary: 

- variables: Things that are assigned values in a possible solution.
- values: Possible values for variables in a solution.
- domains: Bags of possible valid values for a variable.
- constraints: Conditions that are used to check if solutions are valid.

.. py:class:: ValueType

   A type variable. Type of values being solved for. Used in the following generic types.

.. py:class:: Domain

   Type annotation for a list of values that can be assigned to a variable.

.. py:class:: DomainsType

   Type annotation for a dictionary of variable names mapped to a list of possible values (a domain).

.. py:class:: SolutionsType

   Type annotation for a dictionary of variable names mapped to values (a candidate solution.)

.. py:class:: Constraint

   Type annotation for a function that takes in parameters that share their name and type with variables
   being solved for (or takes kwargs) and returns bool. Used to check if a solution is valid.
   Should return true if valid arguments are passed, otherwise false.

.. py:class:: SolutionGenerator

   The type returned by `solve`, It's a generator of dicts that map variables to values 
   (a generator of SolutionType.).

"""
from typing import cast as _cast, TypeVar, List, Dict, Set, Callable, Generator, Any
from inspect import getfullargspec as _getfullargspec


__all__ = [
    "solve",
    "ValueType",
    "Domain",
    "DomainsType",
    "SolutionsType",
    "Constraint",
    "SolutionGenerator",
]


## Types
ValueType = TypeVar("ValueType")
Domain = List[ValueType,]
DomainsType = Dict[str, Domain]
SolutionsType = Dict[str, ValueType]
Constraint = Callable[..., bool]
SolutionGenerator = Generator[SolutionsType, None, None]


def _validate_domain(domain: Domain):
    """Function that checks if a list is a valid domain."""
    if not isinstance(domain, list):
        raise ValueError(f"Domain must be a list, not { type(domain) }.")
    if not len(domain) == len(set(domain)):
        raise ValueError(f"Values in domain should be unique. { domain }")
    if not len(domain) > 0:
        raise ValueError("Domains cannot be empty.")


def _validate_constraint(constraint: Constraint, domains: DomainsType):
    """Function that checks if a constraint is valid."""
    if not callable(constraint):
        raise ValueError(f"Constrints must be callable, {constraint}")
    argspec = _getfullargspec(constraint)
    for arg in argspec.args:
        if not arg in domains.keys():
            raise ValueError(f"{arg} is not a known variable.")


def _validate_domains_and_constraints(
    domains: DomainsType, constraints: List[Constraint]
):
    """A function to assert that a group of domains and constraints are valid."""
    # Assert domains are valid.
    if not isinstance(domains, Dict):
        raise ValueError("The domains arg must be a dict of str to list.")
    if not len(domains.items()) > 0:
        raise ValueError("Domains dictionary cannot be empty.")
    for domain_to_check in domains.values():
        _validate_domain(domain_to_check)
    # Assert constraints are valid
    for constraint_to_check in constraints:
        _validate_constraint(constraint_to_check, domains)


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
    sorted_function=sorted,
) -> SolutionGenerator:
    """
        A recursive generator function that yields solutions to a constraint solving problem,
        using domain reduction.

        eg.

        >>> from amp_constraint_solver import solve
        >>> list(solve({'a': [1, 2], 'b': [1, 2]}, [(lambda a, b: a > b),]))
        [{'a': 2, 'b': 1}]


        :param domains: A dict of variable names to lists of possible assignments, :py:class:`DomainsType`.
        :param constraints: A list of :py:class:`Constraint` functions to check possible solutions.
        :param sorted_function: Can be used to override what order variables are assigned in. 
        :returns: A generator of candidate solutions. :py:data:`SolutionGenerator`
        :raise ValueError: Invalid domains or constraints. See :py:mod:`amp_constraint_solver.test_constraint_solver`
    """
    if _current_solution is None:
        _current_solution = dict()

    if _depth == 0:
        # Assert args are valid
        _validate_domains_and_constraints(domains, constraints)

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
