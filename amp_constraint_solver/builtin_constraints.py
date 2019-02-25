""" Some built in constraints to be used in testing. """
from .constraint_solver import Constraint
from typing import cast as _cast, TypeVar, List, Dict, Set, Callable, Generator


__all__ = [
    "no_duplicate_values_constraint",
    "make_vars_not_equal_constraint",
    "make_vars_not_diagonal_on_grid_constraint",
]


def no_duplicate_values_constraint(**variables) -> bool:
    """An :py:class:`amp_constraint_solver.constraint_solver.Constraint` that can be passed to :py:func:`amp_constraint_solver.constraint_solver.solve`.
       Ensures that values are assigned to only one variable at a time.

       :param variables: All variables in a candidate solution.
       :returns: Whether all variables are destinct.
    """
    for var1, value1 in variables.items():
        for var2, value2 in variables.items():
            if var1 != var2:
                if value1 == value2:
                    return False
    return True


def make_vars_not_equal_constraint(var1: str, var2: str) -> Constraint:
    """A function that creates a constraint that ensures two variables are different.

       :param var1: A variable name.
       :param var2: Another variable name.
       :returns: An :py:class:`amp_constraint_solver.constraint_solver.Constraint` that can be passed to :py:func:`amp_constraint_solver.constraint_solver.solve`.
    """

    def not_equal(**variables) -> bool:
        f"Ensuring {var1} and {var2} are not equal."
        if all([key in variables for key in (var1, var2)]):
            if variables[var1] == variables[var2]:
                return False
        return True

    return not_equal


def make_vars_not_diagonal_on_grid_constraint(
    x1: str, y1: str, x2: str, y2: str
) -> Constraint:
    """A function that creates a constraint ensures that (x1, y1) is not diagonal with (x2, y2) on a positive grid.

       :param x1: The variable name of the X coord of the first point.
       :param y1: The variable name of the Y coord of the first point.
       :param x2: The variable name of the X coord of the second point.
       :param y2: The variable name of the Y coord of the second point.
       :returns: An :py:class:`amp_constraint_solver.constraint_solver.Constraint` that can be passed to :py:func:`amp_constraint_solver.constraint_solver.solve`.
    """

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
