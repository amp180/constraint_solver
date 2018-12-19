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
from .constraint_solver import *
