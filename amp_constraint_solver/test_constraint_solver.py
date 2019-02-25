"""Contains tests that demonstrate usage and assumptions."""

import unittest
import itertools
from amp_constraint_solver.constraint_solver import *
from amp_constraint_solver.builtin_constraints import *

reference_4_queens_solution = {
    "x1": 0,
    "y1": 1,
    "x2": 1,
    "y2": 3,
    "x3": 2,
    "y3": 0,
    "x4": 3,
    "y4": 2,
}
reference_x_ne_y_solutions = [{"x": 1, "y": 2}, {"x": 2, "y": 1}]
reference_cartesian_product_solution = [
    {"x": 1, "y": 3},
    {"x": 1, "y": 4},
    {"x": 2, "y": 3},
    {"x": 2, "y": 4},
]


class ConstraintSolverTests(unittest.TestCase):
    def test_cartesian_product(self):
        """A test to check that all solutions are visited."""
        print("Solving for x in [1,2] and y in [3, 4] without constraints.")
        solutions = list(solve({"x": [1, 2], "y": [3, 4]}))
        print(solutions)
        assert solutions, "There should be a solution"
        assert (
            solutions == reference_cartesian_product_solution
        ), "Solutions should form a cartesian product."

    def test_solve_x_ne_y(self):
        """A test to check that the solver works correctly with a
           :py:func:`amp_constraint_solver.builtin_constraints.make_vars_not_equal_constraint`."""
        print("Solving for values of x and y in range(1, 2) where x!=y:")
        solutions = list(
            solve(
                {"x": [1, 2], "y": [1, 2]},
                constraints=[make_vars_not_equal_constraint("x", "y")],
            )
        )
        print(solutions)
        assert solutions, f"There should be a solution, \n{solutions}\n"
        assert (
            solutions == reference_x_ne_y_solutions
        ), "Solution should match reference, \n{solutions}\n"

    def test_lambda_solve_x_ne_y(self):
        """A test to check that the solver works correctly with lambdas
           and can discover how to call them from their parameter names.
        """
        print("Testing that lambdas work:")
        solutions = list(
            solve(
                {"x": [1, 2], "y": [1, 2]}, constraints=[(lambda x, y: x != y)]
            )
        )
        print(solutions)
        assert solutions, f"There should be a solution, \n{solutions}\n"
        assert (
            solutions == reference_x_ne_y_solutions
        ), "Solution should match reference, \n{solutions}\n"

    def test_solve_4_queens(self):
        """Test the solver against a reference solution to the 4 queens problem.

           Tests that :py:func:`amp_constraint_solver.builtin_constraints.make_vars_not_diagonal_on_grid_constraint`
           and :py:func:`amp_constraint_solver.builtin_constraints.make_vars_not_equal_constraint`
           work with the solver.
        """
        print("Solving for 2d coordinates that solve the 4 queens problem:")
        domain = list(range(0, 4))

        x_coords = ["x1", "x2", "x3", "x4"]
        y_coords = ["y1", "y2", "y3", "y4"]
        pieces = zip(x_coords, y_coords)

        solutions = list(
            solve(
                {
                    "x1": domain,
                    "y1": domain,
                    "x2": domain,
                    "y2": domain,
                    "x3": domain,
                    "y3": domain,
                    "x4": domain,
                    "y4": domain,
                },
                [
                    make_vars_not_equal_constraint(a, b)
                    for a, b in itertools.permutations(x_coords, 2)
                    if a != b
                ]
                + [
                    make_vars_not_equal_constraint(a, b)
                    for a, b in itertools.permutations(y_coords, 2)
                    if a != b
                ]
                + [
                    make_vars_not_diagonal_on_grid_constraint(*a, *b)
                    for a, b in itertools.permutations(pieces, 2)
                    if a != b
                ],
            )
        )

        print(solutions[0])
        assert (
            len(solutions) == 48
        ), "There are 2 solutions and 4! ways of arranging the variables for a solution."
        assert (
            reference_4_queens_solution in solutions
        ), "Handchecked solution was not found in solutions."

    def test_kwargs_not_passed_twice(self):
        r"""A test that the solver can correctly call functions with both globbed kwargs and named args."""

        def constraint1(b, **variables):
            return variables["a"] != 5 and b != 2

        constraint2 = lambda a, b: a != b
        for solution in solve(
            {"a": [1, 5], "b": [1, 2, 3]}, [constraint1, constraint2]
        ):
            assert solution == {"a": 1, "b": 3}

    def test_no_domains(self):
        """Test that the solver raises an error if provided with an empty dict for variables and domains.

        >>> from amp_constraint_solver import solve
        >>> try:
        ...     list(solve({}))
        ... except ValueError as e:
        ...     print(e)
        ...
        Domains dictionary cannot be empty.
        """
        test_empty = lambda: list(solve({}))
        self.assertRaises(ValueError, test_empty)

    def test_domain_not_list(self):
        """Test that the solver raises an error when supplied with a domain that is not a list.

        >>> from amp_constraint_solver import solve
        >>> try:
        ...     list(solve({"x": 1}, [lambda z: True]))
        ... except ValueError as e:
        ...     print(e)
        ...
        Domain must be a list, not <class 'int'>.
        """
        test_invalid = lambda: list(solve({"x": None}))
        self.assertRaises(ValueError, test_invalid)

    def test_invalid_domain(self):
        """Test that the solver raises an error when supplied an empty domain.

        >>> from amp_constraint_solver import solve
        >>> try:
        ...     list(solve({"x": []}))
        ... except ValueError as e:
        ...     print(e)
        ...
        Domains cannot be empty.
        """
        test_invalid = lambda: list(solve({"x": []}))
        self.assertRaises(ValueError, test_invalid)

    def test_unique_values(self):
        """Test that the solver raises an error when supplied a domain with repeated values

        >>> from amp_constraint_solver import solve
        >>> try:
        ...     list(solve({'x': [1, 1]}))
        ... except ValueError as e:
        ...     print(e)
        ...
        Values in domain should be unique. [1, 1]
        """
        test_invalid = lambda: list(solve({"x": [1, 1]}))
        self.assertRaises(ValueError, test_invalid)

    def test_invalid_constraint(self):
        """Test that the solver raises an error if a constraint needs a variable that isn't being solved for.

        >>> from amp_constraint_solver import solve
        >>> try:
        ...     list(solve({"x": [1]}, [lambda z: True]))
        ... except ValueError as e:
        ...     print(e)
        ...
        z is not a known variable.
        """
        wrong_arg = lambda: list(solve({"x": [1]}, [lambda z: True]))
        self.assertRaises(ValueError, wrong_arg)


if __name__ == "__main__":
    unittest.main()
