# Constraint solver

A toy constraint solver that  uses domain reduction.

eg. 
```
from amp_constraint_solver import solve 

def constraint1(b, **variables):
    return variables['a'] != 5 and b != 3
    
constraint2 = lambda a, b: a != b

for solution in solve({'a': [1, 5], 'b': [1, 2, 3]}, [constraint1, constraint2]):
   print(solution)
```

## To build:
```
pip install --user poetry 
make build
```

## To run tests:
`make test`
