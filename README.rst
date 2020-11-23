parspace
========

This module is a simple tool to automatically explore a parameter space.

You can install parspace with ``pip``::

    $ python3 -m pip install -U --user parspace

Usage as a decorator
--------------------

This package provides a class that can be used to aumatically run a function
over all possible combinations of a given parameter space.

Say that you have a problem controlled by two parameters: an aspect ratio
``asp`` and a density ``density``.  The following example shows how to use
``ParSpace`` to automatically explore every combination of the requested values
for these two parameters.  If you have a function (here called ``launch_simu``)
that performs the desired task for a given value of these two parameters, you
merely have to use ``ParSpace`` as a decorator on that function.

.. code:: python

    from parspace import ParSpace


    @ParSpace(asp=[0.5, 1, 2],
              density=[1, 10])
    def launch_simu(asp, density):
        print(f"aspect ratio {asp} and density {density}")


    launch_simu()

This code will print the following on screen::

    aspect ratio 0.5 and density 1
    aspect ratio 0.5 and density 10
    aspect ratio 1 and density 1
    aspect ratio 1 and density 10
    aspect ratio 2 and density 1
    aspect ratio 2 and density 10

In real use cases, ``launch_simu`` could e.g. perform the desired simulation or
submit a job on a supercomputer.  The order of arguments of ``launch_simu``
does not matter, only their names.  In other words, if its signature is instead
``def launch_simu(density, asp)``, you would obtain the same result. On the
other hand, defining it as ``def launch_simu(aspect, density)`` would result in
a ``TypeError`` when calling the function as the ``asp`` argument fed to
``ParSpace`` does not match any argument of ``launch_simu``.

If you have a large number of parameters, you might prefer defining
``launch_simu`` as taking a dictionary of keyword arguments.  Parameter names
and values are then the keys and values of that dictionary.

.. code:: python

    from parspace import ParSpace


    @ParSpace(asp=[0.5, 1, 2],
              density=[1, 10])
    def launch_simu(**pars):
        asp = pars['asp']
        density = pars['density']
        print(f"aspect ratio {asp} and density {density}")


    launch_simu()


Iterating through returned values
---------------------------------

If you care about the returned values of the wrapped function rather than on
its side effects, you can iterate over the decorated object as shown below.

.. code:: python

    from parspace import ParSpace


    @ParSpace(asp=[0.5, 1, 2],
              density=[1, 10])
    def calc_mass(asp, density):
        return asp * density


    for pars, mass in calc_mass:
        asp = pars['asp']
        density = pars['density']
        print(f"Mass for aspect {asp} at density {density}: {mass}")


Note that iterating through a bare ``ParSpace`` instance yields the parameters
dictionary.

.. code:: python

    from parspace import ParSpace


    space = ParSpace(asp=[0.5, 1, 2],
                     density=[1, 10])
    for pars in space:
        print("aspect ratio {asp} and density {density}".format(**pars))


Exploring the same space on several functions
---------------------------------------------

Provided that the iterables used to build the ``ParSpace`` instance can be
iterated through any number of times (mind that generators can only be iterated
through *once*), you can use that instance on several functions as follow.

.. code:: python

    from parspace import ParSpace


    space = ParSpace(asp=[0.5, 1, 2],
                     density=[1, 10])


    @space
    def launch_simu(asp, density):
        print(f"aspect ratio {asp} and density {density}")


    launch_simu()


    for pars, mass in space(lambda asp, density: asp * density):
        asp = pars['asp']
        density = pars['density']
        print(f"Mass for aspect {asp} at density {density}: {mass}")
