r"""
Constraint solving using domain reduction.

Imports * from :py:mod:`amp_constraint_solver.constraint_solver` and :py:mod:`amp_constraint_solver.builtin_constraints`.

Usage of :py:func:`amp_constraint_solver.constraint_solver.solve`:

>>> from amp_constraint_solver import solve 
>>> def constraint1(b, **variables):
...     return variables['a'] != 5 and b != 3
... 
>>> constraint2 = lambda a, b: a != b 
>>> for solution in solve({'a': [1, 5], 'b': [1, 2, 3]}, [constraint1, constraint2]):
...    print(solution)
... 
{'a': 1, 'b': 2}

"""
from .constraint_solver import *
from .builtin_constraints import *

__version__ = "0.4.0"
