Constraint solver
+++++++++++++++++

A minimal constraint solver that uses domain reduction.

Made to test out poetry, mypy, black, sphinx and doctest.

Module docs at https://amp180.github.io/constraint_solver/ 

Example
-------

.. code:: python

	from amp_constraint_solver import solve 


	def constraint1(b, **variables):
		return variables['a'] != 5 and b != 3
		
		
	constraint2 = lambda a, b: a != b


	for solution in solve({'a': [1, 5], 'b': [1, 2, 3]}, [constraint1, constraint2]):
	   print(solution)
  

prints:

.. code:: text

    {'a': 1, 'b': 2}

Installation
------------

Download wheel or sdist from https://github.com/amp180/constraint_solver/releases
and install via `pip install ./file.whl`

or on pip 19.0+

.. code:: bash

    pip install git+https://github.com/amp180/constraint_solver.git


To build
--------

.. code:: bash

    pip install --user poetry
    make build


To run tests
------------

.. code:: bash

    make test
