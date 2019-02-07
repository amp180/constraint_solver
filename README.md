# Constraint solver

A minimal constraint solver that uses domain reduction.

Module docs at https://amp180.github.io/constraint_solver/ 

## Example

```
from amp_constraint_solver import solve 


def constraint1(b, **variables):
    return variables['a'] != 5 and b != 3
    
    
constraint2 = lambda a, b: a != b


for solution in solve({'a': [1, 5], 'b': [1, 2, 3]}, [constraint1, constraint2]):
   print(solution)
  
 
```
prints:
```
{'a': 1, 'b': 2}
```

## To install:
Download wheel or sdist from https://github.com/amp180/constraint_solver/releases

or on pip 19.0+

```
pip install git+https://github.com/amp180/constraint_solver.git
```

## To build:
```
pip install --user poetry
make build
```

## To run tests:
`make test`
