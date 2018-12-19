import unittest
from .constraint_solver import *
import itertools

reference_4_queens_solution = {
    'x1': 0,
    'y1': 1,
    'x2': 1,
    'y2': 3,
    'x3': 2,
    'y3': 0,
    'x4': 3,
    'y4': 2
}
reference_x_ne_y_solutions = [{'x': 1, 'y': 2}, {'x': 2, 'y': 1}]
reference_cartesian_product_solution = [{
    'x': 1,
    'y': 3
}, {
    'x': 1,
    'y': 4
}, {
    'x': 2,
    'y': 3
}, {
    'x': 2,
    'y': 4
}]


class ConstraintSolverTests(unittest.TestCase):

    def test_cartesian_product(self):
        print("Solving for x in [1,2] and y in [3, 4] without constraints.")
        solutions = list(solve({'x': [1, 2], 'y': [3, 4]}))
        print(solutions)
        assert solutions, "There should be a solution"
        assert solutions == reference_cartesian_product_solution, "Solutions should form a cartesian product."

    def test_solve_x_ne_y(self):
        print("Solving for values of x and y in range(1, 2) where x!=y:")
        solutions = list(
            solve({
                'x': [1, 2],
                'y': [1, 2]
            },
                  domain_constraints=[
                      all_unique_in_domain_constraint,
                  ]))
        print(solutions)
        assert solutions, f"There should be a solution, \n{solutions}\n"
        assert solutions == reference_x_ne_y_solutions, "Solution should match reference"

    def test_solve_4_queens(self):
        print("Solving a unique solution to the 4 queens problem:")
        domain = list(range(0, 4))

        x_coords = ["x1", "x2", "x3", "x4"]
        y_coords = ["y1", "y2", "y3", "y4"]
        pieces = zip(x_coords, y_coords)

        solutions = list(
            solve({
                'x1': domain,
                'y1': domain,
                'x2': domain,
                'y2': domain,
                'x3': domain,
                'y3': domain,
                'x4': domain,
                'y4': domain,
            }, [
                vars_not_equal_domain_constraint(a, b)
                for a, b in itertools.permutations(x_coords, 2)
                if a != b
            ] + [
                vars_not_equal_domain_constraint(a, b)
                for a, b in itertools.permutations(y_coords, 2)
                if a != b
            ] + [
                vars_not_diagonal_on_grid_domain_constraint(*a, *b)
                for a, b in itertools.permutations(pieces, 2)
                if a != b
            ], [
                values_unique_set_constraint(),
            ]))

        print(solutions)
        assert len(solutions) == 1, "Solution should be unique."
        assert reference_4_queens_solution in solutions, "First solution was not the same as the hand-checked one."
