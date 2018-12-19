import unittest
import itertools
from constraint_solver.constraint_solver import *

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
        print("Solving for x in [1,2] and y in [3, 4] without constraints.")
        solutions = list(solve({"x": [1, 2], "y": [3, 4]}))
        print(solutions)
        assert solutions, "There should be a solution"
        assert (
            solutions == reference_cartesian_product_solution
        ), "Solutions should form a cartesian product."

    def test_solve_x_ne_y(self):
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
        print("Testing that lambdas work:")
        solutions = list(
            solve({"x": [1, 2], "y": [1, 2]}, constraints=[(lambda x, y: x != y)])
        )
        print(solutions)
        assert solutions, f"There should be a solution, \n{solutions}\n"
        assert (
            solutions == reference_x_ne_y_solutions
        ), "Solution should match reference, \n{solutions}\n"

    def test_solve_4_queens(self):
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


if __name__ == "__main__":
    unittest.main()
