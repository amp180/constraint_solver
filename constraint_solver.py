"""
# Constraint solving using domain reduction.

Glossary:
	* variables: Things that are assigned values in a possible solution.
	* values: Possible values for variables in a solution.
	* domains: Bags of possible valid values for a variable.
	* constraints: Conditions that are used to reduce domains or check if solutions are valid.

"""
from typing import *
import itertools

## Types
ValueType = TypeVar('ValueType') # Type of values being solved for.
Domain = List[ValueType] # Domain of candidate values to select a variable value from.
DomainsType = Dict[str, Domain] # Mapping of variables to domains.
SolutionsType = Dict[str, ValueType] # Mapping of variables to values (possible solution).
DomainsConstraint = Callable[[DomainsType,], DomainsType] # Function to map variable->domain mappings to a more restrictive set of variable->domain mappings.
SolutionConstraint = Callable[[SolutionsType,], bool] # Function that partially checks if a possible solution is valid.
SolutionGenerator = Generator[SolutionsType, None, None] # Type returned by the solve function.


def _assert_domain(domain: Domain):
    """Function that checks if a list is a valid domain."""
    assert isinstance(domain, list), f"Domain must be a list, { domain }."
    assert (len(domain) == len(set(domain))), f"Values in domain should be unique. \n{ domain }"
    return None


def domain_is_empty(domain: Domain) -> bool:
    """Function that checks if a domain (list of values) is empty."""
    _assert_domain(domain)
    return len(domain) == 0


def domain_is_value(domain: Domain) -> bool:
    """Function that checks if a domain (list of values) contains only one possible value."""
    _assert_domain(domain)
    return len(domain) == 1


def domain_get_value(domain: Domain) -> ValueType:
    """Function that gets a single possible value from a domain (list of values), assuming it contains only one."""
    _assert_domain(domain)
    assert domain_is_value(domain), f"This can only be called on a domain that contains a single value, not { domain }."
    return domain[0]


def _all_domains_have_remaining_values(domains: DomainsType) -> bool:
    """Function that checks if all variables in a variable->domain mapping still have candidate values."""
    return all((not domain_is_empty(d) for v, d in domains.items()))


def _check_solution_constraints(variables: SolutionsType, constraints : List[SolutionConstraint]) -> bool:
    """Function to check that a list of solution constraint checks are satisfied by a solution."""
    return all([constraint(variables) for constraint in constraints])


def _domains_with_assigned_value(domains: DomainsType, var: str, value: ValueType):
     """Creates a copy of a variable->domain mapping with one domain replaced with a single value domain."""
     new_domains = dict(domains)
     new_domains[var] = [value,] # list (domain) with a single value.
     return new_domains


def _constrain_domains(domains: DomainsType, constraints : List[DomainsConstraint]) -> DomainsType:
     """Compose/Apply a list of functions to the variable->domain mapping to produce a new mapping."""
     ## Apply each of the functions in turn to the variable->domain mappings 
     for constraint in constraints:
        domains = constraint(domains)
        if not _all_domains_have_remaining_values(domains):
            # One of the domains has no valid values, no point continuing with this branch of possible solutions.
            break;
     return domains


def solve(domains: DomainsType, domain_constraints: List[DomainsConstraint] = [], solution_constraints: List[SolutionConstraint] = [], *, _depth: int = 0, sorted_function=sorted) -> SolutionGenerator:
    """A recursive generator function that yields solutions to a constraint solving problem using domain reduction."""
    if _depth == len(domains):
            # Base case, all the domains have been reduced to one value
            # We need to get the solution variable->value mapping and check if it is valid.
            values: SolutionsType = dict([(name, domain_get_value(domain)) for name, domain in domains.items()])
            if _check_solution_constraints(values, solution_constraints):
                # Yield the valid solution up the generator chain
                yield values
    else:
        # Recursive case, choose the next variable in alphabetical order and iterate over all values.
        current_var = sorted_function(domains.keys())[_depth]
        current_domain = domains[current_var]
        _assert_domain(current_domain) # Assert current domain is valid.
        for value in current_domain:
            # Create a new set of domains where only the current value is in the current domain.
            new_domains = _domains_with_assigned_value(domains, current_var, value)
            # Run the `DomainsConstraint`s on the new variable->domain mapping. 
            new_domains = _constrain_domains(new_domains, domain_constraints)
            if not _all_domains_have_remaining_values(new_domains):
                # One of the variables we've chosen does not lead to solutions, don't bother recursing.
                continue;
            # Recurse to the next variable with the new variable->domain mappings.
            yield from solve(new_domains, domain_constraints, solution_constraints, _depth=_depth+1)


def all_unique_in_domain_constraint(domains: DomainsType) -> DomainsType:
    """A function that ensures that values are assigned to only one domain at a time."""    
    for var, domain in domains.items():
        if domain_is_value(domain):
              for v, d in domains.items():
                  if v != var:
                      domains[v] = list(filter(lambda x: x != domain_get_value(domain), d))
                      if domain_is_empty(domains[v]):
                          return domains
    return domains


def vars_not_equal_domain_constraint(var1: str, var2: str):
     """A function that checks if all values are assigned to only one variable at a time."""
     def not_equal(domains: DomainsType) -> DomainsType:
         f"ensuring {var1} and {var2} are not equal"

         new_domains = dict(domains)

         if domain_is_value(domains[var1]):
             new_domains[var2] = list(filter(lambda x: x != domain_get_value(domains[var1]), domains[var2]))
         
         if domain_is_value(domains[var2]):
             new_domains[var1] = list(filter(lambda x: x != domain_get_value(domains[var2]), domains[var1]))

         return new_domains
     return not_equal


def vars_not_diagonal_on_grid_domain_constraint(x1:str, y1: str, x2: str, y2:str):
    def not_diagonal(domains: DomainsType) -> DomainsType:
        new_domains = dict(domains)
        """Ensure ({x1}, {y1}) is not diagonal with ({x2}, {y2})"""
        # diagonal on a grid is when abs(x1-x2) == abs(y1-y2)
        if domain_is_value(domains[x1]) and domain_is_value(domains[x2]):
            x1_value = domain_get_value(domains[x1])
            x2_value = domain_get_value(domains[x2]) 
            if domain_is_value(domains[y1]):
                y1_value = domain_get_value(domains[y1])
                new_domains[y2] = list(filter(lambda y2_value: abs(y1_value-y2_value) != abs(x1_value-x2_value), domains[y2]))
            if domain_is_value(domains[y2]):
                y2_value = domain_get_value(domains[y2])
                new_domains[y1] = list(filter(lambda y1_value: abs(y1_value-y2_value) != abs(x1_value-x2_value), domains[y1]))
        if domain_is_value(domains[y1]) and domain_is_value(domains[y2]):
            y1_value = domain_get_value(domains[y1])
            y2_value = domain_get_value(domains[y2]) 
            if domain_is_value(domains[x1]):
                x1_value = domain_get_value(domains[x1])
                new_domains[x2] = list(filter(lambda x2_value: abs(y1_value-y2_value) != abs(x1_value-x2_value), domains[x2]))
            if domain_is_value(domains[x2]):
                x2_value = domain_get_value(domains[x2])
                new_domains[x1] = list(filter(lambda x1_value: abs(y1_value-y2_value) != abs(x1_value-x2_value), domains[x1]))
        return new_domains
    return not_diagonal


def values_unique_set_constraint():
    variables_set = set()
    def func(variables: Dict[str, object]) -> bool:
        """Function to check all sets of values are unique."""
        values_set = frozenset(variables.values())
        if values_set in variables_set:
            return False
        variables_set.add(values_set)
        return True

    return func

if __name__=='__main__':
    print("Solving for x in [1,2] and y in [3, 4] without constraints.")
    for solution in solve(
    {
        'x': [1, 2],
        'y': [3, 4]
    }):
        print(solution)

#####
    print("Solving for values of x and y in range(1, 5) where x!=y:")
    for solution in solve(
    {
        'x': [1, 2, 3, 4],
        'y': [1, 2, 3, 4]
    },
    domain_constraints=[all_unique_in_domain_constraint,]):
        print(solution)
    
#####
    print("Solving a unique solution to the 4 queens problem:")
    domain = list(range(0, 4))
    
    x_coords = ["x1", "x2", "x3", "x4"]
    y_coords = ["y1", "y2", "y3", "y4"]
    pieces = zip(x_coords, y_coords)
    
    for solution in solve(
    {
        'x1': domain,
        'y1': domain,
        'x2': domain,
        'y2': domain,
        'x3': domain,
        'y3': domain,
        'x4': domain,
        'y4': domain,
    },
    [vars_not_equal_domain_constraint(a, b) for a, b in itertools.permutations(x_coords, 2) if a != b]
    + [vars_not_equal_domain_constraint(a, b) for a, b in itertools.permutations(y_coords, 2) if a != b]
    + [vars_not_diagonal_on_grid_domain_constraint(*a, *b) for a, b in itertools.permutations(pieces, 2) if a != b],
    [values_unique_set_constraint(),]
    ):
        print(solution)
