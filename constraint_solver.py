"""
# Constraint solving
* variables
* values
* domains (bags of values)
* constraints
"""
from typing import *

class Domain:
    def __init__(self, values: List[str]):
        self.values: Set = set(values)
        assert len(self.values)==len(values), "Values must be unique."

    def constrained(self, filter_func: Callable) -> "Domain":
        return Domain(list(filter(filter_func, self.values)))

    def __len__(self) -> int:
        return len(self.values)

    def is_empty(self) -> bool:
        return len(self) == 0

    def is_value(self) -> bool:
       return len(self) == 1

    def value(self) -> object:
       assert self.is_value(), "This can only be called on a domain that's fully constrained."
       return next(iter(self.values))


class ConstrainResult(NamedTuple): 
    consistent: bool
    variables: Dict[str, Domain]


class SolveResult(NamedTuple): 
    consistent: bool
    variables: Dict[str, object]


class Constraint():
    def constrain(self, domains : Dict[str, Domain]) -> ConstrainResult:  
        return ConstrainResult(all((not d.is_empty() for v, d in domains.items())), domains)

    def check(self, variables: Dict[str, object]) -> bool:
        return True


def _check_constraints(variables: Dict[str, object], constraints : List[Constraint]) -> bool:
    return all([constraint.check(variables) for constraint in constraints])


def _domains_with_assigned_value(domains: Dict[str, Domain], var: str, value: object):
     new_domains = dict(domains)
     new_domains[var] = Domain([value,])
     return new_domains


def _constrain_domains(domains: Dict[str, Domain], constraints : List[Constraint]) -> ConstrainResult:
     newdomains = dict(domains)
     for constraint in constraints:
        consistency, newdomains = constraint.constrain(newdomains)
        if not consistency:
            return ConstrainResult(consistency, newdomains)
     return ConstrainResult(True, newdomains)


def solve(domains: Dict[str, Domain], constraints : List[Constraint], depth: int = 0) -> SolveResult:
    if depth == len(domains):
            values = dict([(name, domain.value()) for name, domain in domains.items()])
            consistent = _check_constraints(values, constraints)
            if consistent:
                yield SolveResult(consistent, values)
    else:
        current_var = sorted(domains.keys())[depth]
        current_domain = domains[current_var]
        for value in current_domain.values:
            new_domains = _domains_with_assigned_value(domains, current_var, value)
            consistent, new_domains = _constrain_domains(new_domains, constraints)
            if not consistent:
                continue;
            for solution in solve(new_domains, constraints, depth+1):
                    yield solution


class AllDifferentConstraint(Constraint):
    def constrain(self, domains : Dict[str, Domain]) -> ConstrainResult:
        new_domains = dict(domains)
        for var, domain in domains.items():
             if domain.is_value():
                  for v, d in new_domains.items():
                      if v != var:
                          new_domains[v] = d.constrained(lambda x: x != domain.value())
                          if new_domains[v].is_empty():
                              return ConstrainResult(False, new_domains)
        return ConstrainResult(True, new_domains)

    def check(self, variables: Dict[str, object]) -> bool:
        for key1, value1 in variables.items():
             for key2, value2 in variables.items():
                 if key1 != key2 and value1 == value2:
                     return False
        return True
             

for solution in solve({'x': Domain([1, 2]), 'y': Domain([1, 2, 3, 4])}, [Constraint(), AllDifferentConstraint(),]):
    print(solution)